"""Build the separate TGM model's official-ID BOM, LDraw, and manuals."""
from io import BytesIO
import json
from pathlib import Path
from PIL import Image
from collector_manuals import Book, generate

ROOT=Path(__file__).resolve().parents[1]
MODEL='green-museumbrary'
folder=ROOT/'downloads'/MODEL
pkg=json.loads((ROOT/'data'/f'{MODEL}.json').read_text())
model,ref=pkg['model'],pkg['reference']
qa=json.loads((folder/'assembly-qa.json').read_text())
img=ROOT/'assets/previews'
scenes=[
 ('','八座量體・總覽','依設計團隊 A2-07 的量體關係轉為積木：斜置、錯開、不齊高。白色板帶和透明窗分別表現擴張網與玻璃內層。'),
 ('-plan','配置與方向','俯視可核對 A、B、C 美術館側和圖書館量體的節奏，以及兩側開放空間。最上方是圖面方向，並非正北方向。'),
 ('-park','中央公園側','地面保持柱間通道與矮植栽。長板承托窗牆，屋頂板帶和採光條分開表現。'),
 ('-terrace','文化之森','白色環道、透明內側欄板、植栽、屋頂露臺。弧線以可扣合的積木轉角近似，沒有把樹當結構支撐。'),
 ('-under','首層／橋下數位剖切','以高度剖切看柱位、廣場和水景。三段主要跨件的左右端都有實際凸點；這不是可由實體一件提起的剖切組。'),
]
def render_architecture():
    book=Book(model)
    for suffix,title,caption in scenes:
        book.new('建築與積木')
        book.chapter(1,title)
        y=book.wrap(36,91,title,520,26,34)
        book.wrap(36,y+1,caption,520,12,19)
        pic=Image.open(img/(MODEL+suffix+'.webp')).convert('RGB')
        pic.thumbnail((1080,800))
        out=BytesIO();pic.save(out,'JPEG',quality=86,optimize=True)
        book.pic((36,160,558,585),out.getvalue())
        if suffix=='':
            y=book.wrap(36,625,f'{qa["pieces"]:,} 件 ／ {qa["bags"]} 袋 ／ {qa["steps"]} 步　 底座 {model["width"]} × {model["depth"]} 凸點',520,14,21)
            book.wrap(36,y+14,'數位拼裝已查核逐件支撐、相撞和組合連通。未做實體承重、運送或材料耐久測試。',520,12,20)
        else:book.wrap(36,625,'設計依據與取捨另見 architecture.md。逐件安裝使用 manual.html 或 LDraw，不以這一頁代替。',520,12,20)
        book.finish_page()
    book.save(folder/'architecture.pdf')
def write_notes():
    lines=[f'# {model["name"]}','',ref['observation'],'',ref['interpretation'],'','## 模型規格','',
           f'- {qa["pieces"]:,} 件、{qa["bags"]} 袋、{qa["steps"]} 步；底座 {model["width"]} × {model["depth"]} 凸點，即 {model["width"]*.8:.1f} × {model["depth"]*.8:.1f} 公分。最高約 {qa["maxLayer"]*.32:.1f} 公分（不含凸點露出）。',
           '- A–H 輪廓取自設計團隊平面圖；白色帷幕以細薄框格與玻璃透明件表達。模型未複製實際網片孔距。',
           '- 白色屋頂環道與有中庭視線的架空層分開，三段代表性連橋用白色板同時扣住兩端。',
           f'- 採購表 {qa["selectedPartColors"]} 組零件×顏色均有 LEGO 官方設計及元素料號紀錄。這不表示即時有貨、零件已購買或實體已拼過。',
           '- 通過逐步凸點支撐與佔位、垂直裝入順序、組裝連通；不宣稱承重工程分析、物理測試或實體抗彎性能。','',
           '## 觀看方式','','- 首層／橋下用數位剖切呈現；屋頂輪廓與高度是讀圖後的縮尺近似。','- 組裝以完整 HTML、線上逐件指引或 LDraw 步序為準。PDF 是摘要。','',
           '## 來源','']+['- ['+s['label']+']('+s['url']+')' for s in ref['sources']]
    (folder/'architecture.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':
    render_architecture()
    write_notes()
    generate(model,ROOT,folder,ref,print_excerpts=True)
