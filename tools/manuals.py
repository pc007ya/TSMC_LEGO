#!/usr/bin/env python3
"""Build self-contained field manuals and inventory files from the exhibit data."""
import argparse
import base64
import csv
import heapq
import io
import json
import math
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PER_PAGE = 8
ROUND_PARTS = {"4073", "3062b", "3941", "4032a", "98138", "4150", "60474"}
CURVED_PARTS = {"85080", "30565"}
CSS = """
*{box-sizing:border-box}html{color-scheme:light;scroll-behavior:smooth}body{margin:0;background:#e8edee;color:#172e37;font:16px/1.55 -apple-system,BlinkMacSystemFont,"PingFang TC","Microsoft JhengHei",sans-serif}
h1,h2,h3,p{margin:0}h1{font-size:clamp(1.9rem,5vw,3.5rem);line-height:1.15;margin:.25em 0}h2{font-size:1.65rem;line-height:1.25;margin:.15em 0 .3em}h3{font-size:1.12rem;margin:1.1em 0 .4em}a{color:#075c66}nav{margin:0 auto;padding:10px max(18px,calc((100vw - 820px)/2));display:flex;align-items:center;gap:18px;background:#123039;color:white}nav a{color:white;white-space:nowrap}nav button{margin-left:auto;border:1px solid #adc2c5;color:white;background:transparent;padding:.5rem .9rem;border-radius:3px;cursor:pointer;white-space:nowrap}
.sheet{position:relative;background:white;max-width:860px;margin:22px auto;padding:32px 40px;box-shadow:0 3px 14px #15293017}.eyebrow,.signature{letter-spacing:.08em;font-size:.78rem;font-weight:700;color:#416269}.signature{border-top:1px solid #d2dfe0;margin-top:18px;padding-top:9px;display:flex;justify-content:space-between;gap:10px}.subtitle{color:#4b656a}.figure{display:block;width:100%;max-height:420px;margin:12px auto}.iso{display:block;width:100%;height:265px;margin:16px 0;background:#f1f5f4;border:1px solid #dae3e3;border-radius:5px}.tags{display:flex;gap:10px;flex-wrap:wrap;margin:.8em 0;color:#17585e}.tags span{padding:.15rem .6rem;background:#eaf3f2}.guidance{border-left:3px solid #0f7277;padding:6px 12px;background:#f1f7f6;color:#1c4850;margin:.6em 0}.contents{margin:6px 0;padding-left:1.5em}.contents li{padding:.12em 0}.contents a{text-decoration:none}.small{font-size:.85rem;color:#475f66}.planhint{font-size:.86em;color:#3a555d}table{width:100%;border-collapse:collapse;margin:.45em 0;font-size:.92rem;font-variant-numeric:tabular-nums}th{text-align:left;color:#335761;background:#eef4f3}th,td{padding:.36em .5em;border-bottom:1px solid #dfe7e7}thead{display:table-header-group}tr{break-inside:avoid}td.qty,th.qty{text-align:right;white-space:nowrap}.num{display:inline-block;min-width:1.55em;text-align:center;background:#0e545b;color:white;border-radius:100px;font-weight:700}.chip{display:inline-block;vertical-align:middle;width:.9em;height:.9em;margin-right:.32em;border:1px solid #65737c88;border-radius:2px}.mono{font-family:ui-monospace,monospace}.rowid{color:#5e7178;font-size:.85em}.fixed{white-space:nowrap}.inventory{columns:2;column-gap:24px}.inventory li{break-inside:avoid;margin:0 0 3px}.qtymark{font-weight:700}.picklist{margin:.3em 0 .8em;font-size:.88em}.picklist span{display:inline-block;margin-right:.65em}.stephead{display:flex;justify-content:space-between;align-items:baseline;gap:.75rem;flex-wrap:wrap}
@media(max-width:600px){.sheet{margin:10px auto;padding:20px 12px}.inventory{columns:1}nav{gap:10px;font-size:.86em}.figure{max-height:345px}th,td{padding:.3em .2em}.rowid{display:block}.iso{height:210px}}
@page{size:A4 portrait;margin:12mm}
@media print{*{-webkit-print-color-adjust:exact;print-color-adjust:exact}html,body{background:white;font-size:10pt}nav{display:none}.sheet{max-width:none;margin:0;padding:0;box-shadow:none;break-before:page}.sheet:first-of-type{break-before:auto}.eyebrow,.signature{font-size:8pt}h1{font-size:30pt}h2{font-size:19pt}.figure{height:105mm;max-height:105mm;margin:2mm auto}.iso{height:85mm}.signature{margin-top:3mm;padding-top:2mm}.small,.planhint{font-size:9pt}th,td{padding:.27em .45em}.contents a{color:inherit}a{text-decoration:none}.inventory{columns:2}.rowid{display:inline}.picklist{font-size:9pt}.stephead{margin-top:0}.sheet h3{break-after:avoid}table{margin-top:2mm}}
"""
CSS += """
.views{display:grid;grid-template-columns:1.4fr 1fr;gap:16px;align-items:center;margin:1em 0}.views figure{min-width:0;margin:0}.views figcaption{font-weight:700;font-size:.86em;color:#385761;margin:.35em 0}.views .figure{height:300px;margin:0}.stageimg{width:100%;max-height:235px;object-fit:contain;background:white;display:block}
@media(max-width:640px){.views{grid-template-columns:1fr;gap:.45em}.views .figure{height:auto;max-height:305px}.stageimg{height:160px}}
@media print{.views{grid-template-columns:1fr;margin:2mm 0 1mm;gap:1mm}.views figcaption{font-size:8.5pt;margin:0}.views .figure{height:80mm;max-height:80mm}.stageimg{height:44mm;max-height:44mm}.views figure:last-child{display:grid;grid-template-columns:25% 75%;align-items:center}.sheet .signature{font-size:7.5pt}.sheet .stephead{break-after:avoid}}
"""


def e(value):
    return escape(str(value), quote=True)


def n(value):
    return f"{value:.4f}".rstrip("0").rstrip(".") if value else "0"


def count(items):
    return Counter((str(item["part"]), item["color"]) for item in items)


def merge_steps(steps):
    return [piece for step in steps for piece in step["pieces"]]


def size(piece, catalog):
    spec = catalog["parts"][str(piece["part"])]
    w, d = spec["w"], spec["d"]
    return (d, w) if piece.get("r", 0) % 2 else (w, d)


def is_round(piece, spec):
    return str(piece["part"]) in ROUND_PARTS or str(spec.get("shape", "")).lower().startswith(("round", "cylinder", "disc"))


def footprint(piece, catalog):
    w, d = size(piece, catalog)
    part = str(piece["part"])
    masks = {"85080": (".#", "#."), "30565": ("####", "###.", "###.", "#..."),
             "60474": (".##.", "####", "####", ".##.")}
    if part in masks:
        mask = masks[part]
        cells = {(x,z) for z,row in enumerate(mask) for x,ch in enumerate(row) if ch == "#"}
        for _ in range(piece.get("r",0) % 4):
            cells = {(w - 1 - z, x) for x,z in cells}
    else:
        cells = {(x,z) for x in range(w) for z in range(d)}
    return {(piece["x"] + x, piece["z"] + z) for x,z in cells}


def paginate(pieces, catalog):
    # Stacked pieces need separate pictures so that lower placement numbers stay legible.
    page, cells = [], set()
    for number, piece in enumerate(pieces, 1):
        occupied = footprint(piece, catalog)
        if len(page) >= PER_PAGE or cells.intersection(occupied):
            yield page
            page, cells = [], set()
        page.append((number, piece))
        cells.update(occupied)
    if page:
        yield page


def rgb(hex_code):
    value = str(hex_code).lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def mix(hex_code, other, amount):
    return "#" + "".join(f"{round(v * (1 - amount) + t * amount):02x}" for v, t in zip(rgb(hex_code), other))


def swatch(color):
    return f'<i class="chip" style="background:{e(color["hex"])}"></i>{e(color["name"])}'


def orientation(piece, catalog):
    part = catalog["parts"][str(piece["part"])]
    if str(piece["part"]) in CURVED_PARTS:
        return ["圓心左後", "圓心右後", "圓心右前", "圓心左前"][piece.get("r", 0) % 4]
    if part["w"] == part["d"] and str(piece["part"]) != "14719":
        return "—"
    return ["沿 X", "沿 Z", "沿 X（180°）", "沿 Z（270°）"][piece.get("r", 0) % 4]


def labelpiece(part, color, catalog):
    return f'{catalog["colors"][color]["name"]} {catalog["parts"][part]["name"]}（{part}）'


def sorted_inventory(inventory, catalog):
    return sorted(inventory.items(), key=lambda row: (catalog["colors"][row[0][1]]["ldraw"], row[0][0]))


def coord(piece):
    return piece["x"] + 1, piece["z"] + 1, piece["y"]


def line_svg(x1, y1, x2, y2, attrs):
    return f'<path d="M{n(x1)},{n(y1)}L{n(x2)},{n(y2)}" {attrs}/>'


def plan_svg(model, prior, page, catalog):
    w, d = model["width"], model["depth"]
    svg = [f'<svg class="figure" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="模型俯視定位圖，編號對應本頁取件表" viewBox="-2.4 -2 {n(w+3.4)} {n(d+3.1)}">']
    svg += [f'<rect width="{w}" height="{d}" fill="#f4f7f7" stroke="#9aafb2" stroke-width=".07"/>']
    for x in range(w + 1):
        svg.append(line_svg(x, 0, x, d, 'stroke="#d6e1e2" stroke-width=".035"'))
    for z in range(d + 1):
        svg.append(line_svg(0, z, w, z, 'stroke="#d6e1e2" stroke-width=".035"'))
    # One stud can have many plates under it. Draw only pieces with an exposed cell.
    top = {}
    for index, p in enumerate(prior):
        height = p["y"] + catalog["parts"][str(p["part"])]["h"]
        for cell in footprint(p, catalog):
            if height >= top.get(cell, (-1, -1))[0]:
                top[cell] = height, index
    visible = sorted(set(top.values()))
    for _, index in visible:
        p = prior[index]
        spec = catalog["parts"][str(p["part"])]
        color = mix(catalog["colors"][p["color"]]["hex"], (219, 229, 229), .81)
        svg.append(plan_shape(p, spec, color, "#9caeb0", .045, catalog))
    for number, p in page:
        spec = catalog["parts"][str(p["part"])]
        color = catalog["colors"][p["color"]]["hex"]
        svg.append(plan_shape(p, spec, color, "#096771", .12, catalog))
        pw, pd = size(p, catalog)
        x, z = p["x"] + pw / 2, p["z"] + pd / 2
        svg.append(f'<circle cx="{n(x)}" cy="{n(z)}" r=".44" fill="#113e48" stroke="#fff" stroke-width=".05"/>')
        svg.append(f'<text x="{n(x)}" y="{n(z+.19)}" text-anchor="middle" font-size=".56" fill="white" font-weight="700">{number}</text>')
    svg.append('<g fill="#385661" font-size=".56" font-family="Arial,sans-serif" text-anchor="middle">')
    stride = 2 if max(w, d) > 18 else 1
    for i in range(0, w, stride):
        svg.append(f'<text x="{n(i+.5)}" y="-.43">{i+1}</text>')
    for i in range(0, d, stride):
        svg.append(f'<text x="-.69" y="{n(i+.68)}">{i+1}</text>')
    svg += [f'<text x="{n(w/2)}" y="-1.24">X</text><text x="-1.75" y="{n(d/2+.2)}">Z</text></g></svg>']
    return "".join(svg)


def plan_shape(p, spec, color, stroke, thickness, catalog):
    w, d = size(p, catalog)
    attrs = f'fill="{color}" stroke="{stroke}" stroke-width="{n(thickness)}"'
    if str(p["part"]) in CURVED_PARTS:
        path = " ".join(f"{n(x)},{n(z)}" for x,z in curve_outline(p, w))
        return f'<polygon points="{path}" {attrs}/>'
    if is_round(p, spec):
        return f'<ellipse cx="{n(p["x"]+w/2)}" cy="{n(p["z"]+d/2)}" rx="{n(w/2-.045)}" ry="{n(d/2-.045)}" {attrs}/>'
    return f'<rect x="{n(p["x"]+.04)}" y="{n(p["z"]+.04)}" width="{n(w-.08)}" height="{n(d-.08)}" rx=".05" {attrs}/>'


def curve_outline(p, width):
    # Both parts are quarter circles with their centre at the back-left corner in r=0.
    # 85080 has a one-stud-wide wall; 30565 fills its quarter disc.
    arc = [(math.cos(i*math.pi/32), math.sin(i*math.pi/32)) for i in range(17)]
    outline = [(x*(width-.04),z*(width-.04)) for x,z in arc]
    if str(p["part"]) == "85080":
        outline.extend((x*(width-.97),z*(width-.97)) for x,z in reversed(arc))
    else:
        outline.append((.04,.04))
    for _ in range(p.get("r",0) % 4):
        outline = [(width-z,x) for x,z in outline]
    return [(p["x"]+x,p["z"]+z) for x,z in outline]


def painter_order(pieces, catalog, project, ax, az):
    # Sort intersecting projections by their separating 3D planes. Sorting by
    # centre alone lets a long roof cut through a nearer wall or a foundation.
    bounds, frames = [], []
    for p in pieces:
        w,d=size(p,catalog)
        a,b=p["x"],p["x"]+w
        c,f=p["z"],p["z"]+d
        g,h=p["y"],p["y"]+catalog["parts"][str(p["part"])]["h"]
        points=[project(x,z,y) for x in (a,b) for z in (c,f) for y in (g,h)]
        bounds.append(((a,b) if ax>=0 else (-b,-a),(c,f) if az>=0 else (-f,-c),(g,h)))
        frames.append(tuple((min(pt[i] for pt in points),max(pt[i] for pt in points)) for i in (0,1)))
    links=[[] for _ in pieces]
    deps=[0]*len(pieces)
    def behind(a,b):
        return any(far[1]<=near[0] for far,near in zip(a,b))
    for i in range(len(pieces)):
        for j in range(i):
            if any(a[1]<=b[0]+.001 or b[1]<=a[0]+.001 for a,b in zip(frames[i],frames[j])):
                continue
            ij,ji=behind(bounds[i],bounds[j]),behind(bounds[j],bounds[i])
            if ij!=ji:
                far,near=(i,j) if ij else (j,i)
                links[far].append(near)
                deps[near]+=1
    open_nodes=[i for i,n_dep in enumerate(deps) if n_dep==0]
    heapq.heapify(open_nodes)
    done=set()
    while len(done)<len(pieces):
        if not open_nodes:
            # A theoretical painter cycle can only involve mutually occluding parts.
            open_nodes.append(min(i for i in range(len(pieces)) if i not in done))
        node=heapq.heappop(open_nodes)
        if node in done:
            continue
        yield pieces[node]
        done.add(node)
        for linked in links[node]:
            deps[linked]-=1
            if not deps[linked]:
                heapq.heappush(open_nodes,linked)


def projection(camera):
    ax,ay,az=camera
    horizontal=math.hypot(ax,az)
    ax,az=ax/horizontal,az/horizontal
    elev=math.atan2(ay,horizontal)
    def project(x, z, y):
        return x*az-z*ax,(x*ax+z*az)*math.sin(elev)-y*.40*math.cos(elev)
    return ax,az,project


def iso_svg(pieces, catalog, camera, additions=None, ordering=None):
    # Illustrate the model for identification. The dimensioned plans govern placement.
    ax,az,project=projection(camera)
    points = []
    faces = []
    guides = []
    bordering = False
    def polygon(vertices, color, line):
        outline = [project(*vertex) for vertex in vertices]
        points.extend(outline)
        path = " ".join(f"{n(x)},{n(y)}" for x, y in outline)
        return f'<polygon points="{path}" fill="{color}" stroke="{line}" stroke-width="{".09" if bordering else ".043"}" stroke-linejoin="round"/>'
    heights = {}
    for p in pieces:
        top = p["y"]+catalog["parts"][str(p["part"])]["h"]
        for cell in footprint(p,catalog):
            heights[cell]=max(top,heights.get(cell,0))
    included={id(p) for p in pieces}
    ordered=painter_order(pieces,catalog,project,ax,az) if ordering is None else (p for p in ordering if id(p) in included)
    for p in ordered:
        x, z, y = p["x"], p["z"], p["y"]
        w, d = size(p, catalog)
        spec = catalog["parts"][str(p["part"])]
        top = y + spec["h"]
        base = catalog["colors"][p["color"]]["hex"]
        bordering = additions is not None and id(p) in additions
        if additions is not None and not bordering:
            base=mix(base,(223,230,230),.88)
        side1, side2 = mix(base,(9,32,46),.16), mix(base,(9,32,46),.30)
        lid, stroke = mix(base,(255,255,255),.11), mix(base,(20,42,48),.29)
        if bordering:
            stroke="#b94c1d"
        if is_round(p, spec) or str(p['part']) in CURVED_PARTS:
            if str(p['part']) in CURVED_PARTS:
                rim = curve_outline(p,w)
            else:
                rim = [(x+w/2+math.cos(i*math.pi/12)*w*.48, z+d/2+math.sin(i*math.pi/12)*d*.48) for i in range(24)]
            for i,a in enumerate(rim):
                b = rim[(i+1)%len(rim)]
                nx,nz=b[1]-a[1],a[0]-b[0]
                if nx*ax+nz*az>0:
                    shade = mix(base, (9,32,46), .22+.08*nx/max(.001,math.hypot(nx,nz)))
                    faces.append(polygon([(*a,y),(*b,y),(*b,top),(*a,top)], shade, shade))
            faces.append(polygon([(*v,top) for v in rim], lid, stroke))
        else:
            front=z+d if az>=0 else z
            side=x+w if ax>=0 else x
            faces.append(polygon([(x,front,y),(x+w,front,y),(x+w,front,top),(x,front,top)], side1, stroke))
            faces.append(polygon([(side,z,y),(side,z+d,y),(side,z+d,top),(side,z,top)], side2, stroke))
            rim=[(x,z),(x+w,z),(x+w,z+d),(x,z+d)]
            faces.append(polygon([(*v,top) for v in rim], lid, stroke))
        if bordering:
            # On visible parts this coincides with the solid edge. Hidden
            # sections remain traceable through already assembled higher walls.
            outline=" ".join(f"{n(tx)},{n(ty)}" for tx,ty in (project(*v,top) for v in rim))
            guides.append(f'<polygon points="{outline}" fill="none" stroke="#a43d16" stroke-width=".10" stroke-dasharray=".25 .20"/>')
        if spec.get("shape","").lower() in {"grille","tile","roundtile"}:
            continue
        for cell in sorted(footprint(p,catalog)):
            if heights[cell] == top:
                cx,cy=project(cell[0]+.5,cell[1]+.5,top+.17)
                faces.append(f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx=".29" ry=".17" fill="{lid}" stroke="{stroke}" stroke-width=".04"/>')
    xmin, xmax = min(x for x,_ in points)-1, max(x for x,_ in points)+1
    ymin, ymax = min(y for _,y in points)-1, max(y for _,y in points)+1
    return f'<svg class="iso" xmlns="http://www.w3.org/2000/svg" aria-label="積木成品示意圖" role="img" viewBox="{n(xmin)} {n(ymin)} {n(xmax-xmin)} {n(ymax-ymin)}">{"".join(faces)}{"".join(guides)}</svg>'


def stage_picture(model, catalog, all_pieces, prior, page, view_cache):
    """Use the side nearest the additions so earlier walls seldom conceal them."""
    import fitz
    from PIL import Image
    pieces=[p for _,p in page]
    ax,ay,az=model["camera"]
    for dim in ("x","z"):
        extent=model["width"] if dim=="x" else model["depth"]
        axis=0 if dim=="x" else 1
        centres=[p[dim]+size(p,catalog)[axis]/2 for p in pieces]
        offset=sum(centres)/len(centres)/extent-.5
        if abs(offset)>.12:
            if dim=="x":
                ax=math.copysign(abs(ax),offset)
            else:
                az=math.copysign(abs(az),offset)
    camera=(ax,ay,az)
    if camera not in view_cache:
        x,z,project=projection(camera)
        view_cache[camera]=list(painter_order(all_pieces,catalog,project,x,z))
    svg=iso_svg(prior+pieces,catalog,camera,{id(p) for p in pieces},view_cache[camera])
    with fitz.open(stream=svg.encode(),filetype="svg") as vector:
        sheet=vector[0]
        scale=min(510/sheet.rect.width,340/sheet.rect.height)
        pix=sheet.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
    img=Image.frombytes("RGB",(pix.width,pix.height),pix.samples).quantize(colors=80,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    data=io.BytesIO()
    img.save(data,format="PNG",optimize=True)
    uri=base64.b64encode(data.getvalue()).decode("ascii")
    side=("前" if az>0 else "後")+("右" if ax>0 else "左")
    return f'<figure><figcaption>立體進度 · {side}上方看<br>橘線標出新件，虛線為遮蔽處</figcaption><img class="stageimg" alt="由{side}上方觀看本頁完成後的高度與前後關係" src="data:image/png;base64,{uri}"></figure>'


def inventory_html(items, catalog):
    rows = []
    for (part, color), qty in sorted_inventory(count(items), catalog):
        rows.append(f'<tr><td>{swatch(catalog["colors"][color])}</td><td>{e(catalog["parts"][part]["name"])}</td><td class="mono">{e(part)}</td><td class="qty">{qty}</td></tr>')
    return '<table><thead><tr><th>顏色</th><th>零件</th><th>設計／庫號</th><th class="qty">件數</th></tr></thead><tbody>'+"".join(rows)+'</tbody></table>'


def inventory_md(items, catalog):
    lines = ["| 顏色 | 零件 | 設計／庫號 | 數量 |", "| --- | --- | --- | ---: |"]
    for (part, color), qty in sorted_inventory(count(items), catalog):
        lines.append(f'| {catalog["colors"][color]["name"]} | {catalog["parts"][part]["name"]} | {part} | {qty} |')
    return lines


def export_ldr(model, catalog, path, source_transforms):
    # LDraw uses right-handed X/Z on the base and negative Y up, in 1/20 stud units.
    lines = [f'0 {model["code"]} - {model["en"]}', '0 Name: model.ldr', '0 Author: pc007ya/TSMC_LEGO', '0 !LDRAW_ORG Unofficial_Model', '0 !CATEGORY Model']
    first = True
    for bag_no, bag in enumerate(model["bags"], 1):
        for step_no, step in enumerate(bag["steps"], 1):
            if not first:
                lines.append("0 STEP")
            first = False
            lines.append(f'0 // Bag {bag_no} - step {step_no} - {step["name"]}')
            for p in step["pieces"]:
                part = str(p["part"])
                spec = catalog["parts"][part]
                w, d = size(p, catalog)
                px, pz = (p["x"] + w/2)*20, -(p["z"] + d/2)*20
                py = -p["y"]*8
                rot = p.get("r", 0) % 4
                # The WebGL mesh uses X,-Y,-Z relative to the native bottom-centre.
                transform = source_transforms[part]
                if transform["nativeToLocal"] != [1,0,0,0,-1,0,0,0,-1]:
                    raise ValueError(f"unexpected native orientation for {part}")
                dx,dy,dz = (round(v,2) for v in transform["nativeOrigin"])
                cos, sin = [(1,0),(0,1),(-1,0),(0,-1)][rot]
                px, py, pz = px - cos*dx - sin*dz, py-dy, pz + sin*dx - cos*dz
                code = catalog["colors"][p["color"]]["ldraw"]
                matrix = f'{cos} 0 {sin} 0 1 0 {-sin} 0 {cos}'
                lines.append(f'1 {code} {n(px)} {n(py)} {n(pz)} {matrix} {part}.dat')
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")


def export_bom(model, catalog, path):
    bags = [count(merge_steps(bag["steps"])) for bag in model["bags"]]
    whole = sum(bags, Counter())
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["設計或LDraw庫號", "Rebrickable料號", "零件", "顏色", "LDraw色號", "總件數"]+[f"袋{i:02d}" for i in range(1,len(bags)+1)])
        for key, qty in sorted_inventory(whole, catalog):
            part, color = key
            writer.writerow([part, "6141" if part=="4073" else part, catalog["parts"][part]["name"], catalog["colors"][color]["name"], catalog["colors"][color]["ldraw"], qty]+[bag[key] for bag in bags])


def step_page(model, catalog, bag_no, step_no, global_no, step, page, prior, sub, total, stage):
    items = [p for _,p in page]
    rows=[]
    for number,p in page:
        part=str(p["part"])
        x,z,y=coord(p)
        rows.append(f'<tr><td><span class="num">{number}</span></td><td>{swatch(catalog["colors"][p["color"]])}</td><td>{e(catalog["parts"][part]["name"])} <span class="rowid">{e(part)}</span></td><td class="fixed">{x}, {z}</td><td>{y}</td><td class="fixed">{orientation(p,catalog)}</td></tr>')
    table='<table><thead><tr><th>圖號</th><th>顏色</th><th>零件</th><th>X, Z</th><th>底高</th><th>方向</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
    heading=f'{e(step["name"])}'
    picks=" ".join(f'<span>{e(labelpiece(part,color,catalog))} × {qty}</span>' for (part,color),qty in count(items).items())
    sheets=f'圖 {sub} / {total}' if total>1 else "定位圖"
    top=f'<figure><figcaption>俯視定位</figcaption>{plan_svg(model,prior,page,catalog)}</figure>'
    return f'<section class="sheet"><div class="stephead"><span class="eyebrow">{e(model["code"])} ／ 第 {bag_no:02d} 袋 · 袋內步驟 {step_no:02d}</span><span class="small">{sheets}</span></div><h2>{global_no:02d}　{heading}</h2><p>{e(step.get("hint",""))}</p><div class="views">{top}{stage}</div><p class="planhint">俯視圖中的編號對應本頁取件表。淡色為已裝部分，左上角是第 1 欄、第 1 列。</p><h3>本頁取件</h3><p class="picklist">{picks}</p>{table}<div class="signature"><span>{e(model["name"])}</span><span>步驟 {global_no:02d} · {sub}/{total}</span></div></section>'


def write_model(model, catalog, destination, transforms):
    destination.mkdir(parents=True, exist_ok=True)
    name, code, bags = model["name"], model["code"], model["bags"]
    all_steps = [step for bag in bags for step in bag["steps"]]
    all_pieces = merge_steps(all_steps)
    total = len(all_pieces)
    export_bom(model,catalog,destination/"bom.csv")
    export_ldr(model,catalog,destination/"model.ldr",transforms)
    totals=f'{total} 件 · {len(bags)} 袋 · {len(all_steps)} 步'
    guide="將底座較後的一側朝上，從左上角第 1 顆凸點開始數。X 由左向右，Z 由後向前。底高以薄板為單位，桌面是 0，一塊標準磚高 3 層薄板。每個位置均取零件佔地最左、最後的凸點。"
    bag_links="".join(f'<li><a href="#bag-{i}">第 {i:02d} 袋　{e(b["name"])}</a>　<span class="small">{len(merge_steps(b["steps"]))} 件</span></li>' for i,b in enumerate(bags,1))
    html = [f'<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(name)}｜組裝說明書</title><style>{CSS}</style><body><nav><a href="#front">說明書首頁</a><a href="#inventory">全套零件表</a><button onclick="window.print()">列印／儲存 PDF</button></nav><section id="front" class="sheet"><div class="eyebrow">{e(code)} ／ {e(model["en"])}</div><h1>{e(name)}</h1><p class="subtitle">模型組裝說明書</p>{iso_svg(all_pieces,catalog,model.get("camera",[1,.8,1]))}<p>{e(model["description"])}</p><div class="tags"><span>{totals}</span><span>底座 {model["width"]} × {model["depth"]} 凸點</span></div><h3>依袋號組裝</h3><ol class="contents">{bag_links}</ol><h3>閱讀定位圖</h3><p class="guidance">{guide}</p></section>']
    md = [f'# {name}｜組裝說明書', '', f'{code} · {model["en"]}', '', model["description"], '', totals, '', f'底座 {model["width"]} × {model["depth"]} 凸點。', '', guide, '', '圖號依每一步的安裝順序編列，回到下一個步驟時從 1 重新起算。[圖解說明書](manual.html) · [分袋 BOM](bom.csv) · [分步 LDraw 模型](model.ldr)', '']
    prior=[]
    view_cache={}
    global_no=0
    for bag_no, bag in enumerate(bags,1):
        items=merge_steps(bag["steps"])
        html.append(f'<section id="bag-{bag_no}" class="sheet"><div class="eyebrow">{e(code)} ／ 分袋清點</div><h2>第 {bag_no:02d} 袋　{e(bag["name"])}</h2><p>打開這一袋，依下表取出 {len(items)} 件。完成袋內 {len(bag["steps"])} 個步驟後再拆下一袋。</p>{inventory_html(items,catalog)}</section>' if bag_no < len(bags) else f'<section id="bag-{bag_no}" class="sheet"><div class="eyebrow">{e(code)} ／ 分袋清點</div><h2>第 {bag_no:02d} 袋　{e(bag["name"])}</h2><p>打開最後一袋，清點 {len(items)} 件。本袋有 {len(bag["steps"])} 個步驟。</p>{inventory_html(items,catalog)}</section>')
        md += [f'## 第 {bag_no:02d} 袋　{bag["name"]}', '', f'{len(items)} 件，共 {len(bag["steps"])} 步。', '', *inventory_md(items,catalog), '']
        for step_no,step in enumerate(bag["steps"],1):
            global_no+=1
            pages=list(paginate(step["pieces"],catalog))
            md += [f'### 步驟 {global_no:02d}　{step["name"]}', '', step.get("hint",""), '', '**本步取件**', '', *inventory_md(step["pieces"],catalog), '', '**安裝位置**', '', '| 圖號 | 零件與顏色 | X | Z | 底高（薄板） | 方向 |', '| ---: | --- | ---: | ---: | ---: | --- |']
            for sub,page in enumerate(pages,1):
                stage=stage_picture(model,catalog,all_pieces,prior,page,view_cache)
                html.append(step_page(model,catalog,bag_no,step_no,global_no,step,page,prior,sub,len(pages),stage))
                for number,p in page:
                    x,z,y=coord(p)
                    md.append(f'| {number} | {labelpiece(str(p["part"]),p["color"],catalog)} | {x} | {z} | {y} | {orientation(p,catalog)} |')
                    prior.append(p)
            md.append('')
    html += [f'<section id="inventory" class="sheet"><div class="eyebrow">{e(code)} ／ BOM</div><h2>全套零件表</h2><p>依顏色與零件號合計 {total} 件。</p>{inventory_html(all_pieces,catalog)}</section></body></html>']
    md += ['## 全套零件表', '', *inventory_md(all_pieces,catalog), '']
    (destination/'manual.html').write_text(''.join(html),encoding='utf-8')
    (destination/'manual.md').write_text('\n'.join(md),encoding='utf-8')


def print_pdfs(root,models):
    """Print the standalone pages with installed Chrome, then compress duplicate objects."""
    import fitz
    from playwright.sync_api import sync_playwright
    with sync_playwright() as engine:
        browser=engine.chromium.launch(channel="chrome",headless=True)
        context=browser.new_context(offline=True)
        for model in models:
            folder=root/"downloads"/model["id"]
            page=context.new_page()
            page.goto((folder/"manual.html").as_uri(),wait_until="load")
            page.evaluate("document.fonts.ready")
            page.evaluate("Promise.all(Array.from(document.images, img => img.decode()))")
            content=page.pdf(print_background=True,prefer_css_page_size=True)
            with fitz.open(stream=content,filetype="pdf") as document:
                pdf=folder/"manual.pdf"
                document.save(pdf,garbage=4,deflate=True,deflate_images=True,use_objstms=1)
                print(model["id"],len(document),"PDF pages",pdf.stat().st_size,"bytes",flush=True)
            page.close()
        browser.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--pdf-only',action='store_true',help='Render already generated HTML to A4 PDF using local Chrome and Playwright')
    args=parser.parse_args()
    root=args.root
    catalog=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
    models=json.loads((root/'data/models.json').read_text(encoding='utf-8'))
    if args.pdf_only:
        print_pdfs(root,models)
        return
    manifest=root/'assets/parts/index.json'
    transforms=json.loads(manifest.read_text(encoding='utf-8'))
    for model in models:
        write_model(model,catalog,root/'downloads'/model['id'],transforms)
        print(model['id'],len(merge_steps([s for b in model['bags'] for s in b['steps']])))


if __name__=='__main__':
    main()
