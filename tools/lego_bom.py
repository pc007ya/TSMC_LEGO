"""Append evidence-linked LEGO IDs to release BOMs without modifying source fields.

The audited join key is the existing LDraw part and color, not a number in a
third-party catalog. Future generators use the same augmentation, and unreviewed
part/color pairs remain visibly blank instead of borrowing a neighboring color.
"""
import argparse
import csv
from collections import Counter
import io
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data" / "lego-part-verification.json"
SINGLE = ("設計或LDraw庫號", "Rebrickable料號", "零件", "顏色", "LDraw色號", "總件數")
SERIES = ("LDraw料號", "Rebrickable料號", "零件", "顏色", "色號", "全系列合計")
EXTRA = (
    "LEGO官方設計號", "LEGO官方元素號（含顏色）", "採購對應LEGO色號",
    "採購對應LEGO色名", "採購對應LDraw色號", "採購對應Rebrickable料號",
    "採購對應Rebrickable色號", "料號核對狀態", "證據種類", "LEGO官方證據",
    "設計號查證來源", "備註",
)
STATUS = {
    "verified": "LEGO 元素已核對",
    "design_verified": "僅設計號已核對",
    "unverified": "LEGO 元素未核實",
    "legacy": "舊款或變體，未核實元素",
    "not_applicable": "不適用 LEGO 元素號",
}
EVIDENCE = {
    "lego_pab": "LEGO Pick a Brick",
    "lego_manual_and_rebrickable": "LEGO 說明書元素號＋第三方款式／顏色交叉核對",
    "lego_manual": "LEGO 官方說明書",
    "lego_service": "LEGO 官方零件服務",
}
LDRAW_COLOR_SPEC = "https://www.ldraw.org/article/547.html"

def official(url):
    try:
        p = urlsplit(url)
        return p.scheme == "https" and not p.username and not p.password and (
            p.hostname == "lego.com" or (p.hostname or "").endswith(".lego.com")
        )
    except ValueError:
        return False


def key(part, color):
    if not isinstance(part, str):
        raise ValueError(f"Invalid LDraw part: {part!r}")
    stem = part.strip().lower().removesuffix(".dat")
    if not re.fullmatch(r"[a-z0-9_-]+", stem):
        raise ValueError(f"Invalid LDraw part: {part!r}")
    if color is None or isinstance(color, bool) or not re.fullmatch(r"\d+", str(color)):
        raise ValueError(f"Invalid LDraw color: {color!r}")
    return stem, int(color)


def load_mapping(path=MAP):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        raise ValueError(f"{path}: missing rows list")
    rows = {}
    for entry in data["rows"]:
        k = key(entry["ldraw_part"], entry["ldraw_color"])
        if k in rows:
            raise ValueError(f"Duplicate mapping: {k!r}")
        status = entry["status"]
        design = str(entry.get("lego_design_id") or "")
        element = str(entry.get("lego_element_id") or "")
        site = entry.get("source_url") or ""
        design_site = entry.get("design_source_url") or ""
        if status not in STATUS:
            raise ValueError(f"{k}: unknown status {status!r}")
        if (design and not design.isascii()) or (design and not design.isdecimal()):
            raise ValueError(f"{k}: LEGO Design ID must be digits, not an LDraw filename")
        if element and not re.fullmatch(r"[0-9]{6,8}", element):
            raise ValueError(f"{k}: malformed LEGO Element ID")
        if status == "verified" and not (design and element and official(site)):
            raise ValueError(f"{k}: verified row requires Design ID, Element ID, and official LEGO HTTPS evidence")
        if status != "verified" and element:
            raise ValueError(f"{k}: unverified Element ID must not be published as an acquisition number")
        if design and not (official(design_site) or official(site)) and status != "verified":
            raise ValueError(f"{k}: Design ID requires its own official LEGO evidence")
        mapping_color = entry.get("ldraw_color_expected")
        if mapping_color not in (None, ""):
            key(k[0], mapping_color)
        if status != "verified" and not entry.get("note"):
            raise ValueError(f"{k}: unresolved procurement requires a note")
        rows[k] = entry
    return rows


def columns(mapping, part, color):
    k = key(part, color)
    e = mapping.get(k)
    default_expected = 43 if k[1] == 41 else k[1]
    if e is None:
        e = {"status": "unverified", "note": "尚未取得 LEGO 元素與顏色對照證據，請勿直接下單。"}
    expected = e.get("ldraw_color_expected")
    expected = default_expected if expected in (None, "") else int(expected)
    note = e.get("note") or ""
    if expected != k[1]:
        conflict = f"既有數位 LDraw {k[1]} 與採購目標 LDraw {expected} 不同；本次不改原模型。{LDRAW_COLOR_SPEC}"
        note = " ".join(x for x in (note, conflict) if x)
    source_kind = e.get("evidence_type") or ""
    return [
        e.get("lego_design_id") or "", e.get("lego_element_id") or "", e.get("lego_color_id") or "",
        e.get("lego_color_name") or "", expected, e.get("rebrickable_part") or "",
        e.get("rebrickable_color") if e.get("rebrickable_color") is not None else "",
        STATUS[e["status"]], EVIDENCE.get(source_kind, source_kind), e.get("source_url") or "",
        e.get("design_source_url") or "", note,
    ]


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    csv.writer(stream).writerows(rows)
    return stream.getvalue().encode("utf-8-sig")


def export_bom(model, catalog, path, mapping_path=None):
    """Per-model BOM entry point used by both manual generators."""
    from design import procurement_id

    bags = [Counter((str(piece["part"]), piece["color"])
                    for step in bag["steps"] for piece in step["pieces"])
            for bag in model["bags"]]
    whole = sum(bags, Counter())
    mapping = load_mapping(mapping_path) if mapping_path else load_mapping()
    rows = [list(SINGLE) + [f"袋{i:02d}" for i in range(1, len(bags)+1)]]
    for part, color in sorted(whole, key=lambda k: (catalog["colors"][k[1]]["ldraw"], k[0])):
        color_info = catalog["colors"][color]
        rows.append([part, procurement_id(part), catalog["parts"][part]["name"], color_info["name"],
                     color_info["ldraw"], whole[part, color]] + [bag[part, color] for bag in bags])
    path.write_bytes(augment(rows, mapping))


def base_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError(f"{path}: no CSV rows")
    header = rows[0]
    if not all(len(row) == len(header) for row in rows[1:]):
        raise ValueError(f"{path}: invalid number of columns")
    n = len(EXTRA)
    if tuple(header[-n:]) == EXTRA:
        header = header[:-n]
        rows = [header] + [r[:-n] for r in rows[1:]]
    if tuple(header[:6]) not in (SINGLE, SERIES) or len(set(header)) != len(header):
        raise ValueError(f"{path}: unrecognized original BOM header")
    unique = set()
    for i, row in enumerate(rows[1:], start=2):
        if len(row) != len(header):
            raise ValueError(f"{path}:{i}: invalid number of columns")
        k = key(row[0], row[4])
        if k in unique:
            raise ValueError(f"{path}:{i}: repeated part / color {k}")
        unique.add(k)
        quantities = [int(v) for v in row[5:]]
        if quantities[0] <= 0 or min(quantities) < 0 or quantities[0] != sum(quantities[1:]):
            raise ValueError(f"{path}:{i}: quantity does not equal sum of bags or models")
    return rows


def augment(rows, mapping):
    modified = [rows[0] + list(EXTRA)]
    for row in rows[1:]:
        modified.append(row + columns(mapping, row[0], row[4]))
    return csv_bytes(modified)


def ldraw_counts(path):
    with path.open(encoding="utf-8-sig") as f:
        named_root = False
        for line in f:
            directive = line.split(maxsplit=2)[:2]
            if directive == ["0", "FILE"]:
                if named_root:
                    break  # Embedded LDraw parts are library geometry, not separately purchased.
                named_root = True
            if directive == ["0", "NOFILE"]:
                break
            words = line.split(maxsplit=14)
            if words and words[0] == "1":
                if len(words) != 15:
                    raise ValueError(f"{path}: invalid LDraw type-1 line: {line.strip()}")
                yield key(words[14], words[1])


def candidates(root):
    downloads = root / "downloads"
    return sorted(downloads.glob("*/bom.csv")) + sorted(downloads.glob("*-bom.csv"))


def audit(root, mapping, check=False, require_reviewed=False):
    paths = candidates(root)
    if not paths:
        raise ValueError(f"{root}: no release BOMs found")
    expected_keys, files, counts, changed = set(), [], Counter(), []
    individual = {}
    by_name, by_id, colors = {}, {}, {}
    models_path = root / "data" / "models.json"
    if models_path.exists():
        models = json.loads(models_path.read_text(encoding="utf-8"))
        by_name = {m["name"]: m["id"] for m in models}
        by_id = {m["id"]: m for m in models}
        colors = json.loads((root / "data" / "catalog.json").read_text(encoding="utf-8"))["colors"]
    for path in paths:
        rows = base_rows(path)
        total = Counter({key(row[0], row[4]): int(row[5]) for row in rows[1:]})
        expected_keys.update(total)
        ldr = path.parent / "model.ldr"
        if tuple(rows[0][:6]) == SINGLE:
            if not ldr.is_file():
                raise ValueError(f"{path}: model.ldr missing")
            if Counter(ldraw_counts(ldr)) != total:
                raise ValueError(f"{path}: LDraw vs BOM totals differ")
            model_id = path.parent.name
            individual[model_id] = total
            if by_id:
                model = by_id[model_id]
                if rows[0][6:] != [f"袋{i:02d}" for i in range(1, len(model["bags"])+1)]:
                    raise ValueError(f"{path}: bag headers disagree with source model")
                for idx, bag in enumerate(model["bags"], start=6):
                    from_steps = Counter(key(p["part"], colors[p["color"]]["ldraw"]) for step in bag["steps"] for p in step["pieces"])
                    from_csv = Counter({key(r[0], r[4]): int(r[idx]) for r in rows[1:] if int(r[idx])})
                    if from_steps != from_csv:
                        raise ValueError(f"{path}: bag quantities disagree with source model for {rows[0][idx]}")
        if tuple(rows[0][:6]) == SERIES and by_name:
            for idx, name in enumerate(rows[0][6:], start=6):
                model_id = by_name.get(name)
                if model_id not in individual:
                    raise ValueError(f"{path}: no per-model BOM found for aggregate column {name}")
                series_parts = Counter({key(r[0], r[4]): int(r[idx]) for r in rows[1:] if int(r[idx])})
                if series_parts != individual[model_id]:
                    raise ValueError(f"{path}: aggregate column disagrees with {model_id}/bom.csv")
        states = Counter(mapping.get(k, {}).get("status", "unverified") for k in total)
        counts.update(states)
        desired = augment(rows, mapping)
        files.append((path, desired))
        if desired != path.read_bytes():
            changed.append(path)
    if by_id and set(individual) != set(by_id):
        raise ValueError("BOM model coverage differs from data/models.json")
    missing = sorted(expected_keys - set(mapping))
    unused = sorted(set(mapping) - expected_keys)
    if require_reviewed and (missing or unused):
        raise ValueError(f"mapping does not match the BOM scope: {len(missing)} missing, {len(unused)} unused. Examples: {missing[:4]!r}, {unused[:4]!r}")
    if check and changed:
        raise ValueError(f"{len(changed)} stale BOM(s): {', '.join(str(p.relative_to(root)) for p in changed)}")
    if not check:
        for path, desired in files:
            if path in changed:
                path.write_bytes(desired)
    unique_counts = Counter(mapping.get(k, {}).get("status", "unverified") for k in expected_keys)
    return {
        "per_model_boms": len(individual), "series_boms": len(paths)-len(individual),
        "unique_part_color_combinations": len(expected_keys), "unique_status": dict(sorted(unique_counts.items())),
        "all_bom_rows_status": dict(sorted(counts.items())), "missing_mapping_rows": len(missing),
        "unused_mapping_rows": len(unused), "updated_files": len(changed),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT, help="Directory containing downloads/ and data/")
    p.add_argument("--mapping", type=Path, help="Override the evidence JSON for a staging run")
    p.add_argument("--check", action="store_true", help="Compare generated BOM bytes without writing anything")
    p.add_argument("--require-reviewed", action="store_true", help="Require an explicit map row for every combination and no stale keys; unresolved statuses remain allowed")
    args = p.parse_args()
    try:
        mapping = load_mapping(args.mapping or (args.root / "data" / MAP.name))
        summary = audit(args.root, mapping, args.check, args.require_reviewed)
    except (ValueError, KeyError, OSError, TypeError) as e:
        p.exit(1, f"{e}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
