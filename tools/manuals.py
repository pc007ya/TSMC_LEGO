#!/usr/bin/env python3
"""Build self-contained field manuals and inventory files from the exhibit data."""
import argparse
import re
import numpy as np
import base64
import csv
import json
import math
from collections import Counter
from html import escape
from pathlib import Path

import plan_shapes
from print_scene import open_studio
from stickers import collect, details, dimensions, callout, write_sheet, ldraw_shapes

ROOT = Path(__file__).resolve().parents[1]
PER_PAGE = 8
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


CSS+="""
.coverphoto{object-fit:contain}.decal-note{display:flex;align-items:center;gap:12px;background:#f5f1e9;border-left:3px solid #bc4232;margin:8px 0;padding:7px 10px;font-size:.87em}.decal-note img{width:58px;height:32px;object-fit:contain}
@media print{.decal-note{margin:1mm 0;padding:1.3mm 2mm;gap:3mm;border-left:1mm solid #bc4232;font-size:8.5pt}.decal-note img{width:18mm;height:8mm}}
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


def footprint(piece, catalog):
    spec=catalog["parts"][piece["part"]]
    w,d=spec["w"],spec["d"]
    mask=spec.get("body")
    cells={(x,z) for z in range(d) for x in range(w) if not mask or mask[z][x]=="#"}
    for _ in range(piece.get("r",0)%4):
        cells={(d-1-z,x) for x,z in cells}
        w,d=d,w
    return {(piece["x"]+x,piece["z"]+z) for x,z in cells}

def axis_for(model,piece):
    return piece.get("pivotAt") or (model.get("pivot") if piece.get("pivoted") else None)

def yaw(model,piece):
    axis=axis_for(model,piece)
    return piece.get("r",0)*90 + (axis["degrees"] if axis else 0)

def pivot_point(model, piece, x, z):
    pivot=axis_for(model,piece)
    if not pivot:return x,z
    rad=math.radians(pivot["degrees"]);dx=x-pivot["x"];dz=z-pivot["z"]
    return pivot["x"]+dx*math.cos(rad)-dz*math.sin(rad), pivot["z"]+dx*math.sin(rad)+dz*math.cos(rad)

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
    if piece.get("pivotAt"):
        head=["沿 X","沿 Z","沿 X（180°）","沿 Z（270°）"][piece.get("r",0)%4]
        return f'{head}，旋 {piece["pivotAt"]["degrees"]:+.2f}°'
    part = catalog["parts"][str(piece["part"])]
    if "directions" in part:
        return part["directions"][piece.get("r",0)%4]
    if str(piece["part"]) in CURVED_PARTS:
        return ["圓心左後", "圓心右後", "圓心右前", "圓心左前"][piece.get("r", 0) % 4]
    if part["shape"] in {"arcWall","arcTile","curvedSlope","handle","leaves"}:
        return "依圖 " + str(piece.get("r",0)*90) + "°"
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


def plan_svg(model, prior, page, catalog, labels):
    w,d=model["width"],model["depth"]
    back=model.get("rearOverhang",{}).get("rows",0)
    svg=[f'<svg class="figure" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="俯視位置與本頁零件編號" viewBox="-2.4 {-2-back} {w+3.4} {d+back+3.1}"><rect width="{w}" height="{d}" fill="#f4f7f7" stroke="#9aafb2" stroke-width=".07"/>']
    for x in range(w+1):svg.append(line_svg(x,0,x,d,'stroke="#d6e1e2" stroke-width=".035"'))
    for z in range(d+1):svg.append(line_svg(0,z,w,z,'stroke="#d6e1e2" stroke-width=".035"'))
    tops={}
    for i,p in enumerate(prior):
        h=p["y"]+catalog["parts"][p["part"]]["h"]
        for x,z in footprint(p,catalog):
            xx,zz=pivot_point(model,p,x+.5,z+.5)
            key=(math.floor(xx),math.floor(zz))
            if h>=tops.get(key,(-1,-1))[0]:tops[key]=(h,i)
    visible=sorted(set(tops.values()))
    def drawpiece(p,active):
        part=p["part"];a,b=size(p,catalog)
        cx,cz=pivot_point(model,p,p["x"]+a/2,p["z"]+b/2)
        angle=yaw(model,p)
        hue=catalog["colors"][p["color"]]["hex"]
        if not active:hue=mix(hue,(219,229,229),.82)
        color="#086773" if active else "#a3b4b4"
        return f'<use href="#part{part}" transform="translate({n(cx)} {n(cz)}) rotate({n(angle)})" fill="{hue}" stroke="{color}" stroke-linejoin="round" stroke-width="{".10" if active else ".045"}"/>'
    for _,i in visible:svg.append(drawpiece(prior[i],False))
    centres=[]
    for number,p in page:
        svg.append(drawpiece(p,True))
        a,b=size(p,catalog);lx,lz=labels[p["part"]];turn=math.radians(p.get("r",0)*90)
        px=p["x"]+a/2+lx*math.cos(turn)-lz*math.sin(turn)
        pz=p["z"]+b/2+lx*math.sin(turn)+lz*math.cos(turn)
        centres.append((number,*pivot_point(model,p,px,pz)))
    for number,x,z in centres:
        svg.append(f'<circle cx="{n(x)}" cy="{n(z)}" r=".46" fill="#113e48" stroke="#fff" stroke-width=".06"/><text x="{n(x)}" y="{n(z+.19)}" text-anchor="middle" font-size=".59" fill="white" font-weight="700">{number}</text>')
    svg.append('<g fill="#385661" font-size=".58" font-family="Arial,sans-serif" text-anchor="middle">')
    stride=2 if max(w,d)<=40 else 3
    for i in range(0,w,stride):svg.append(f'<text x="{n(i+.5)}" y="{-.4-back}">{i+1}</text>')
    for i in range(0,d,stride):svg.append(f'<text x="-.72" y="{n(i+.68)}">{i+1}</text>')
    svg+= [f'<text x="{n(w/2)}" y="{-1.24-back}">X</text><text x="-1.75" y="{n(d/2+.2)}">Z</text></g></svg>']
    return "".join(svg)

def mount_map(model):
    pivot=model['pivot'];w=model['width'];d=model['depth'];x=pivot['x'];z=pivot['z']
    rows=pivot.get('rows',[pivot['mounts']]);last=rows[0][-1]
    pts=pivot['mounts']
    diagrams=[f'<svg xmlns="http://www.w3.org/2000/svg" class="figure" role="img" aria-label="斜廊固定支點俯視圖" viewBox="-3 -3 {w+5} {d+5}"><rect width="{w}" height="{d}" fill="#f4f7f6" stroke="#82969b" stroke-width=".1"/>']
    for a in range(w+1):
        diagrams.append(line_svg(a,0,a,d,'stroke="#cedbdc" stroke-width=".04"'))
        if a%5==0 and a<w:diagrams.append(f'<text x="{a+.5}" y="-.6" text-anchor="middle" font-size=".85">{a+1}</text>')
    for b in range(d+1):
        diagrams.append(line_svg(0,b,w,b,'stroke="#cedbdc" stroke-width=".04"'))
        if b%5==0 and b<d:diagrams.append(f'<text x="-1.2" y="{b+.8}" text-anchor="middle" font-size=".85">{b+1}</text>')
    for row in rows:
        diagrams.append(line_svg(*row[0],*row[-1],'stroke="#c7542e" stroke-width=".25"'))
    if len(rows)==2:
        for left,right in zip(*rows):diagrams.append(line_svg(*left,*right,'stroke="#819c94" stroke-width=".18"'))
    for n_line,(a,b) in enumerate(pts,1):
        diagrams.append(f'<circle cx="{a}" cy="{b}" r=".65" fill="#154f57"/><text x="{a+1.15}" y="{b-.4}" font-size="1.15" fill="#154f57">P{n_line}</text>')
    length=math.dist((x,z),last)
    diagrams.append(line_svg(x,z,x,z+length,'stroke="#447d85" stroke-width=".2" stroke-dasharray=".5 .4"'))
    return ''.join(diagrams)+'</svg>'

def stage_picture(studio,start,end):
    image=studio.evaluate("([start,end])=>studio.render(start,end)",[start,end])
    caption='貼花細部' if image.get('detail') else '立體安裝圖'
    return f'<figure><figcaption>{caption} · {image["side"]}上方看<br>橘框為本頁新件</figcaption><img class="stageimg" alt="橘框標出安裝位置" src="{image["jpeg"]}"></figure>'

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


def export_ldr(model, catalog, path, source_transforms, stickers):
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
                cx,cz=pivot_point(model,p,p["x"]+w/2,p["z"]+d/2)
                rad=math.radians(yaw(model,p))
                co,si=math.cos(rad),math.sin(rad)
                world_rot=np.array([[co,0,-si],[0,1,0],[si,0,co]])
                origin=np.array([cx*20,-p["y"]*8,-cz*20])
                transform=source_transforms[part]
                native=np.array(transform["nativeToLocal"]).reshape(3,3)
                matrix3=np.diag([1,-1,-1])@world_rot@native
                px,py,pz=origin-matrix3@np.array(transform["nativeOrigin"])
                code=catalog["colors"][p["color"]]["ldraw"]
                matrix=' '.join(n(round(val,6)) for val in matrix3.flat)
                if id(p) in stickers:
                    rec=stickers[id(p)];dec=rec["decal"]
                    lines.append(f'0 // {rec["id"]} decal {dec["art"]} on following part, face {dec["face"]}, {dimensions(rec)}, offset ({dec.get("du",0)}, {dec.get("dv",0)}) mm. {dec["label"]}')
                lines.append(f'1 {code} {n(px)} {n(py)} {n(pz)} {matrix} {part}.dat')
                if id(p) in stickers:
                    lines.extend(ldraw_shapes(model,p,catalog,pivot_point))
    if any(p['part'] == '3224' for bag in model['bags'] for step in bag['steps'] for p in step['pieces']):
        # Include the licensed part definition for LDraw editors with the standard library.
        definition = ROOT / 'assets/parts/supplemental/3224.dat'
        lines = ['0 FILE model.ldr', *lines, '0 FILE 3224.dat', definition.read_text().rstrip(), '0 NOFILE']
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


def pivot_notes(pieces):
    axes={tuple(axis[k] for k in ('label','x','z','degrees')) for p in pieces if (axis:=p.get('pivotAt'))}
    return [f'{label}的定位支點 ({math.floor(x)+1}, {math.floor(z)+1})，轉 {angle:+.2f}°' for label,x,z,angle in sorted(axes)]


def step_page(model, catalog, bag_no, step_no, global_no, step, page, prior, sub, total, stage, labels, stickers):
    items = [p for _,p in page]
    rows=[]
    for number,p in page:
        part=str(p["part"])
        x,z,y=coord(p)
        rows.append(f'<tr><td><span class="num">{number}</span></td><td>{swatch(catalog["colors"][p["color"]])}</td><td>{e(catalog["parts"][part]["name"])} <span class="rowid">{e(part)}</span></td><td class="fixed">{x}, {z}</td><td>{y}</td><td class="fixed">{orientation(p,catalog)}</td></tr>')
    table='<table><thead><tr><th>圖號</th><th>顏色</th><th>零件</th><th>X, Z</th><th>底高</th><th>方向</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
    notes=''.join(callout(stickers[id(p)]) for _,p in page if id(p) in stickers)
    if any(p.get("pivoted") for _,p in page):notes+='<p class="planhint">斜廊的座標取轉向前的格線；俯視圖與立體圖均顯示轉向後的位置。沿斜廊自身格線定位，Z 為 0 時在第一排後方一格，Z 為 −1 時在後方兩格。</p>'
    axes=pivot_notes(items)
    if axes:
        notes+='<p class="planhint">'+'。'.join(e(v) for v in axes)+'。表中為轉向前座標，由上方看正數順時針。</p>'
    heading=f'{e(step["name"])}'
    picks=" ".join(f'<span>{e(labelpiece(part,color,catalog))} × {qty}</span>' for (part,color),qty in count(items).items())
    sheets=f'圖 {sub} / {total}' if total>1 else "定位圖"
    top=f'<figure><figcaption>俯視定位</figcaption>{plan_svg(model,prior,page,catalog,labels)}</figure>'
    return f'<section class="sheet"><div class="stephead"><span class="eyebrow">{e(model["code"])} ／ 第 {bag_no:02d} 袋 · 袋內步驟 {step_no:02d}</span><span class="small">{sheets}</span></div><h2>{global_no:02d}　{heading}</h2><p>{e(step.get("hint",""))}</p><div class="views">{top}{stage}</div><p class="planhint">俯視圖中的編號對應本頁取件表。淡色為已裝部分，左上角是第 1 欄、第 1 列。</p><h3>本頁取件</h3><p class="picklist">{picks}</p>{table}{notes}<div class="signature"><span>{e(model["name"])}</span><span>步驟 {global_no:02d} · {sub}/{total}</span></div></section>'


def write_model(model, catalog, destination, transforms, plans, studio):
    destination.mkdir(parents=True, exist_ok=True)
    name, code, bags = model["name"], model["code"], model["bags"]
    all_steps = [step for bag in bags for step in bag["steps"]]
    all_pieces = merge_steps(all_steps)
    total = len(all_pieces)
    export_bom(model,catalog,destination/"bom.csv")
    stickers=collect(model)
    export_ldr(model,catalog,destination/"model.ldr",transforms,stickers)
    write_sheet(model,catalog,stickers,destination/"stickers.pdf")
    print(model["id"], "rendering illustrated sheets",flush=True)
    symbols,labels=plans
    studio.evaluate("m=>studio.load(m)",model)
    cover=base64.b64encode((ROOT/'assets/previews'/(model['id']+'.webp')).read_bytes()).decode()
    cover_markup=f'<img class="iso coverphoto" alt="{e(name)}完成模型" src="data:image/webp;base64,{cover}">'

    totals=f'{total} 件 · {len(bags)} 袋 · {len(all_steps)} 步'
    guide="將底座較後的一側朝上，從左上角第 1 顆凸點開始數。X 由左向右，Z 由後向前。底高以薄板為單位，桌面是 0，一塊標準磚高 3 層薄板。每個位置均取零件佔地最左、最後的凸點。"
    bag_links="".join(f'<li><a href="#bag-{i}">第 {i:02d} 袋　{e(b["name"])}</a>　<span class="small">{len(merge_steps(b["steps"]))} 件</span></li>' for i,b in enumerate(bags,1))
    html = [f'<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(name)}｜組裝說明書</title><style>{CSS}</style><body>{symbols}<nav><a href="#front">說明書首頁</a><a href="#inventory">全套零件表</a><button onclick="window.print()">列印／儲存 PDF</button></nav><section id="front" class="sheet"><div class="eyebrow">{e(code)} ／ {e(model["en"])}</div><h1>{e(name)}</h1><p class="subtitle">模型組裝說明書</p>{cover_markup}<p>{e(model["description"])}</p><div class="tags"><span>{totals}</span><span>底座 {model["width"]} × {model["depth"]} 凸點</span></div><h3>依袋號組裝</h3><ol class="contents">{bag_links}</ol><h3>閱讀定位圖</h3><p class="guidance">{guide}</p></section>']
    md = [f'# {name}｜組裝說明書', '', f'{code} · {model["en"]}', '', model["description"], '', totals, '', f'底座 {model["width"]} × {model["depth"]} 凸點。', '', guide, '', '圖號依每一步的安裝順序編列，回到下一個步驟時從 1 重新起算。[圖解說明書](manual.html) · [分袋 BOM](bom.csv) · [分步 LDraw 模型](model.ldr)', '']
    ref=json.loads((ROOT/'data/references.json').read_text())[model['id']]
    view_title='建築方位與配置' if model['id']!='arc' else '園區方位、支撐與外環'
    if model.get('series')=='taichung':
        ref_title=ref['edition']
        summary=f'本版 {total} 件，另附 {len(stickers)} 枚貼紙。'
        sources=[(v['label'],v['url']) for v in ref['sources']]
        evidence=ref['observation']+' '+ref['interpretation']
    else:
        ref_title='原盒資料與本版用量'
        summary=f'原盒 {ref["boxCode"]} · {ref["boxPieces"]} 件 · {ref["dimensionsCm"]} 公分。本版 {total} 件，另附 {len(stickers)} 枚貼紙。'
        sources=[('原盒規格',ref['product']),('商品三視圖',ref['photo']),(ref['buildingCredit'],ref['buildingSource'])]
        evidence=ref['observation']
    md+=[f'## {ref_title}','',evidence,'',summary,'',
         ' · '.join(f'[{title}]({url})' for title,url in sources),'',f'## {view_title}','']
    source_links=' · '.join(f'<a href="{e(url)}">{e(title)}</a>' for title,url in sources)
    for index,view in enumerate(model.get('views',[])):
        if index%2==0:
            html.append(f'<section class="sheet"><div class="eyebrow">{e(code)} ／ 構造</div><h2>{view_title}</h2>')
            if index==0:
                html.append(f'<p>{e(summary)}</p><p class="guidance">{e(evidence)} {source_links}</p>')
        fn=model['id']+'-'+view['id']+'.webp'
        pic=base64.b64encode((ROOT/'assets/previews'/fn).read_bytes()).decode()
        html.append(f'<h3>{e(view["name"])}</h3><p>{e(view["note"])}</p><img class="iso coverphoto" style="height:67mm" src="data:image/webp;base64,{pic}" alt="{e(view["name"])}">')
        md+=[f'**{view["name"]}**　{view["note"]}',f'![{view["name"]}](../../assets/previews/{fn})','']
        if index%2==1 or index==len(model['views'])-1:html.append('</section>')
    if stickers:
        text=f'本款有 {len(stickers)} 張貼紙。請以 100% 列印原寸貼紙 PDF，依步驟中的 S 編號貼在指定磚面，再把該件扣入。'
        html.append(f'<section id="decals" class="sheet"><div class="eyebrow">{e(code)} ／ 建築識別</div><h2>標誌與字牌</h2><p>{text}</p><p><a href="stickers.pdf">開啟 A4 原寸貼紙</a></p>')
        md+=['## 原寸貼紙','',text,'','[下載 A4 可列印貼紙](stickers.pdf)','']
        for rec in stickers.values():
            global_no=next(i for i,s in enumerate(all_steps,1) if s is rec['step'])
            html.append(f'<h3>袋 {rec["bag"]:02d} · 步驟 {global_no:02d}</h3>'+callout(rec))
            md.append(f'- {rec["id"]}　{rec["decal"]["label"]} · 袋 {rec["bag"]:02d}／步驟 {global_no:02d} · {dimensions(rec)} · {details(rec)}')
        html.append('</section>');md.append('')
    pivot=model.get('pivot')
    if pivot:
        mounts='、'.join(f'({math.floor(x)+1}, {math.floor(z)+1})' for x,z in pivot['mounts'])
        direction='順時針' if pivot['degrees']>=0 else '逆時針'
        instruction=f'先把灰色支腳扣在底座凸點 {mounts}。每座斜撐的左右底板由上方看{direction}轉 {abs(pivot["degrees"]):.2f}°，對準同一橫排的兩個支腳，再按順序加上斜撐與樓板。轉向前的座標均以長廊自身格線表示。'
        html.append(f'<section class="sheet"><div class="eyebrow">{e(code)} ／ 斜向組裝</div><h2>架設斜廊</h2><p>{instruction}</p>{mount_map(model)}<p>綠色圓點為底座支點。藍色虛線標示長廊直放的方向，橘線連接轉向後的支點。</p></section>')
        md+=['## 斜廊安裝','',instruction,'']
    prior=[]
    global_no=0
    for bag_no, bag in enumerate(bags,1):
        items=merge_steps(bag["steps"])
        html.append(f'<section id="bag-{bag_no}" class="sheet"><div class="eyebrow">{e(code)} ／ 分袋清點</div><h2>第 {bag_no:02d} 袋　{e(bag["name"])}</h2><p>打開這一袋，依下表取出 {len(items)} 件。完成袋內 {len(bag["steps"])} 個步驟後再拆下一袋。</p>{inventory_html(items,catalog)}</section>' if bag_no < len(bags) else f'<section id="bag-{bag_no}" class="sheet"><div class="eyebrow">{e(code)} ／ 分袋清點</div><h2>第 {bag_no:02d} 袋　{e(bag["name"])}</h2><p>打開最後一袋，清點 {len(items)} 件。本袋有 {len(bag["steps"])} 個步驟。</p>{inventory_html(items,catalog)}</section>')
        md += [f'## 第 {bag_no:02d} 袋　{bag["name"]}', '', f'{len(items)} 件，共 {len(bag["steps"])} 步。', '', *inventory_md(items,catalog), '']
        for step_no,step in enumerate(bag["steps"],1):
            global_no+=1
            if global_no%50==0: print(model["id"],"step",global_no,"/",len(all_steps),flush=True)
            pages=list(paginate(step["pieces"],catalog))
            md += [f'### 步驟 {global_no:02d}　{step["name"]}', '', step.get("hint",""), '', '**本步取件**', '', *inventory_md(step["pieces"],catalog), '', '**安裝位置**', '', '| 圖號 | 零件與顏色 | X | Z | 底高（薄板） | 方向 |', '| ---: | --- | ---: | ---: | ---: | --- |']
            for sub,page in enumerate(pages,1):
                stage=stage_picture(studio,len(prior),len(prior)+len(page))
                html.append(step_page(model,catalog,bag_no,step_no,global_no,step,page,prior,sub,len(pages),stage,labels,stickers))
                for number,p in page:
                    x,z,y=coord(p)
                    md.append(f'| {number} | {labelpiece(str(p["part"]),p["color"],catalog)} | {x} | {z} | {y} | {orientation(p,catalog)} |')
                    prior.append(p)
            for p in step["pieces"]:
                if id(p) in stickers:
                    rec=stickers[id(p)]
                    md+=['',f'**貼紙 {rec["id"]}**　{rec["decal"]["label"]}。圖號 {rec["number"]}，{details(rec)}貼好再扣入。尺寸 {dimensions(rec)}。']
            axes=pivot_notes(step['pieces'])
            if axes:md+=['','本步為轉向前座標。從上方看，正數順時針。','']+['- '+v for v in axes]
            if any(p.get('pivoted') for p in step['pieces']):md+=['','本步的座標為斜廊轉向前的格線。Z 為 0 代表第一排後方一格，Z 為 −1 代表後方兩格。']
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
            # The website preview and printed cover must use the same final scene.
            html=folder/"manual.html"
            source=html.read_text()
            cover=base64.b64encode((root/'assets/previews'/(model['id']+'.webp')).read_bytes()).decode()
            source=re.sub(r'(<img class="iso coverphoto"[^>]*src="data:image/webp;base64,)[^"]+',lambda m:m[1]+cover,source,count=1)
            html.write_text(source)
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
    parser.add_argument('--model',help='Render one model id')
    parser.add_argument('--series',choices=['collection','taichung'])
    args=parser.parse_args()
    root=args.root
    catalog=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
    models=json.loads((root/'data/models.json').read_text(encoding='utf-8'))
    if args.model: models=[next(m for m in models if m['id']==args.model)]
    if args.series: models=[m for m in models if m.get('series','collection')==args.series]
    if args.pdf_only:
        print_pdfs(root,models)
        return
    manifest=root/'assets/parts/index.json'
    transforms=json.loads(manifest.read_text(encoding='utf-8'))
    plans=plan_shapes.build(catalog,transforms,root/"assets/parts/geometry.bin")
    with open_studio(root) as studio:
        studio.evaluate("async c=>{window.studio=await (await import('/tools/print-scene.js')).paperStudio(c)}",catalog)
        for model in models:
            write_model(model,catalog,root/'downloads'/model['id'],transforms,plans,studio)
            print(model['id'],sum(len(s['pieces']) for b in model['bags'] for s in b['steps']),flush=True)

if __name__=='__main__':
    main()
