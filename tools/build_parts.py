"""Build the site's offline geometry from the official LDraw complete.zip.

Usage: python3 tools/build_parts.py /path/to/complete.zip
Requires NumPy. Acquires no network resources. The website only reads the outputs.
"""
from collections import defaultdict
from functools import cache
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import sys
import numpy as np

PARTS = """
3024 3023 3623 3710 3666 3460 3022 3021 3020 3795 3034 3031 3032 3035
3958 41539 91405 3036 3030 3005 3004 3622 3010 3009 3008 3003 3002 3001
2456 3070b 3069b 63864 2431 6636 4162 3068b 87079 14719 4073 3062b 3941
4032a 98138 4150 60474 85080 30565 2412b
58846 48092 27507 3245c 15068 24866 32607 11477 2540 85861 20482 11213 44375b 87081
1750 3224
""".split()
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "parts"


# Pin the reviewed-for-this-model revision even when an upstream update adds it.
SUPPLEMENTAL = {"ldraw/parts/3224.dat": OUTPUT / "supplemental" / "3224.dat"}


class PartLibrary:
    def __init__(self, archive):
        self.archive = archive
        self.paths = {name.lower(): name for name in archive.namelist()}
        self.sources = {}

    @cache
    def locate(self, filename):
        filename = filename.replace("\\", "/").lower()
        for directory in ("p", "parts"):
            key = f"ldraw/{directory}/{filename}"
            if key in SUPPLEMENTAL:
                return key
            if key in self.paths:
                return self.paths[key]
        raise ValueError(f"Missing official library file {filename}")

    @cache
    def triangles(self, path):
        source = SUPPLEMENTAL[path].read_bytes() if path in SUPPLEMENTAL else self.archive.read(path)
        lines = source.decode("utf-8-sig").splitlines()
        author = next(line[10:].strip() for line in lines if line.startswith("0 Author: "))
        license_line = next(line[11:].strip() for line in lines if line.startswith("0 !LICENSE "))
        self.sources[path.removeprefix("ldraw/")] = (author, license_line)
        faces = []
        ccw = True
        invert_next = False
        for line in lines:
            words = line.split()
            if not words:
                continue
            if words[:2] == ["0", "BFC"]:
                if "CCW" in words:
                    ccw = True
                if "CW" in words:
                    ccw = False
                if "INVERTNEXT" in words:
                    invert_next = True
            if words[0] in ("3", "4"):
                points = np.array(words[2:], dtype=float).reshape(-1, 3)
                if not ccw:
                    points = points[::-1]
                indices = [0, 1, 2] if len(points) == 3 else [0, 1, 2, 0, 2, 3]
                faces.append(points[indices].reshape(-1, 3, 3))
            if words[0] == "1":
                shift = np.array(words[2:5], dtype=float)
                matrix = np.array(words[5:14], dtype=float).reshape(3, 3)
                child = self.triangles(self.locate(" ".join(words[14:])))
                if len(child):
                    transformed = child @ matrix.T + shift
                    if (np.linalg.det(matrix) < 0) != invert_next:
                        transformed = transformed[:, ::-1]
                    faces.append(transformed)
                invert_next = False
        return np.concatenate(faces) if faces else np.empty((0, 3, 3))


def mesh_attributes(faces):
    # A 1/2048 stud coordinate unit keeps the small notches and curved edges
    # distinguishable while allowing a compact, deterministic binary format.
    quantized = np.rint(faces * 2048).astype("<i2")
    faces = quantized.astype(float)
    cross = np.cross(faces[:, 1] - faces[:, 0], faces[:, 2] - faces[:, 0])
    lengths = np.linalg.norm(cross, axis=1)
    good = lengths > 0
    unit = cross[good] / lengths[good, None]
    quantized = quantized[good]
    # Average adjoining face normals only across gentle bends. Adjacent right
    # angles on a brick must stay sharp while a round stud should shade smoothly.
    linked = defaultdict(set)
    rounded_normals = [tuple(normal.round(5)) for normal in unit]
    points = [[tuple(point) for point in face] for face in quantized]
    for face, normal in zip(points, rounded_normals):
        for point in face:
            linked[point].add(normal)

    @cache
    def vertex(point, normal):
        local = np.array(sorted(linked[point]))
        soft = local[local @ normal > 0.86].sum(axis=0)
        return point + tuple(np.rint(soft * (127 / np.linalg.norm(soft))).astype("i1"))

    lookup = {}
    indices = []
    for face, normal in zip(points, rounded_normals):
        for point in face:
            key = vertex(point, normal)
            indices.append(lookup.setdefault(key, len(lookup)))
    records = np.array(list(lookup))
    index_type = "<u2" if len(lookup) <= 65536 else "<u4"
    return (records[:, :3].astype("<i2"), records[:, 3:].astype("i1"),
            np.array(indices, dtype=index_type))


def convert_part(library, part, stream):
    path = library.locate(part + ".dat")
    faces = library.triangles(path)
    minimum = faces.min(axis=(0, 1))
    maximum = faces.max(axis=(0, 1))
    # The native part origin may be at a single stud of a corner element.
    # Use its projected bounding box for footprint center, its lowest surface
    # for the building plane. Transform LDraw's Y-down to Three's Y-up.
    center = (minimum + maximum) / 2
    native_origin = np.array([center[0], maximum[1], center[2]])
    dx, _, dz = maximum - minimum
    swap = bool(dz > dx + .1)
    rotation = np.array([[0, 0, -1], [0, -1, 0], [-1, 0, 0]]) if swap else np.diag([1, -1, -1])
    if part in {'2540','24866','32607'}:
        # Their handles and leaves extend beyond the studded footprint.
        native_origin = np.array([0., maximum[1], 0.])
        rotation = np.diag([1,-1,-1])
    faces = (faces - native_origin) @ rotation.T / 20
    attributes = mesh_attributes(faces)
    offsets = []
    for attribute in attributes:
        stream.write(bytes((-stream.tell()) % 4))
        offsets.append(stream.tell())
        stream.write(attribute.tobytes())
    positions, _, indices = attributes
    return {
        "vertices": len(positions), "indices": len(indices),
        "indexBytes": indices.itemsize, "offsets": offsets,
        "nativeOrigin": native_origin.round(4).tolist(),
        "nativeToLocal": rotation.flatten().tolist(),
        "footprint": [round(max(dx, dz) / 20, 3), round(min(dx, dz) / 20, 3)],
    }


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    packed = BytesIO()
    with ZipFile(sys.argv[1]) as archive:
        library = PartLibrary(archive)
        catalog = {part: convert_part(library, part, packed) for part in PARTS}
        for file in ("CAreadme.txt", "CAlicense.txt", "CAlicense4.txt"):
            (OUTPUT / file).write_bytes(archive.read("ldraw/" + file))
    data = packed.getvalue()
    (OUTPUT / "geometry.bin").write_bytes(data)
    (OUTPUT / "index.json").write_text(json.dumps(catalog, separators=(",", ":")) + "\n")
    credits = ["# 零件模型來源", "",
               "幾何來自 [LDraw.org 官方零件圖庫](https://library.ldraw.org/updates)及 Gerald Lasser 的 [3224 斜撐框](https://library.ldraw.org/parts/31658)。"
               "本專案將面片三角化、轉換座標、量化並計算表面法線。"
               "原始模型的作者及各檔案所列授權如下。適用條款見本目錄的 CAreadme.txt、"
               "CAlicense.txt 和 CAlicense4.txt。", "",
               "Geometry derived from the LDraw Parts Library. These meshes are adapted "
               "under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as permitted "
               "by the individual source files listed below.", "",
               f"Geometry SHA-256: `{hashlib.sha256(data).hexdigest()}`", "",
               "| Source file | Author | Source license |", "| --- | --- | --- |"]
    for path, (author, license_line) in sorted(library.sources.items()):
        status = "unofficial" if "ldraw/" + path in SUPPLEMENTAL else "official"
        credits.append(f"| [{path}](https://library.ldraw.org/library/{status}/{path}) | {author} | {license_line} |")
    (OUTPUT / "CREDITS.md").write_text("\n".join(credits) + "\n")
    print(f"Packed {len(catalog)} elements derived from {len(library.sources)} sources into {len(data):,} bytes.")


if __name__ == "__main__":
    main()
