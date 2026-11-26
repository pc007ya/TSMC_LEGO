"""Build TC 09's illustrated downloads using the existing collector book engine."""
from io import BytesIO
import json
from PIL import Image
from collector_manuals import Book, generate
from taichung_city_hall import ROOT, ID

folder=ROOT/'downloads'/ID
pkg=json.loads((ROOT/'data'/f'{ID}.json').read_text())
model,ref=pkg['model'],pkg['reference']
qa=json.loads((folder/'assembly-qa.json').read_text())
views=[
 ('','市政大樓・整體配置','此為西屯臺灣大道市政大樓。銀藍水平量體與兩側景觀，中央挑高川堂仍可穿越。'),
 ('-front','臺灣大道・正面','十道水平分層、前凹口、後置集會堂與暖色媒體牆。媒體牆依夜景照片縮尺近似，不複製畫面或標誌。'),
 ('-rear','府後廣場與集會堂','府後看向協調的高低跨梁與深灰川堂側牆。樓面由錯縫積木承住，不使用落地柱封住川堂。'),
 ('-plan','屋頂、前後主軸、林帶','頂部兩翼保持平直，技術層退縮；模型配置以市府場地圖與景觀團隊平面圖區分府前與府後。'),
 ('-courts','數位剖切・兩座中庭','惠中樓、文心樓各有一中庭，中心保留開放地板；切面只用於網頁及本導覽，不代表可以掀掉實體樓層。'),
]
def architecture():
    book=Book(model)
    for suffix,title,caption in views:
        book.new('建築與積木')
        book.chapter(1,title)
        y=book.wrap(36,91,title,520,25,32)
        book.wrap(36,y+5,caption,520,12,19)
        pic=Image.open(ROOT/'assets/previews'/(ID+suffix+'.webp')).convert('RGB')
        pic.thumbnail((1080,800))
        out=BytesIO();pic.save(out,'JPEG',quality=86,optimize=True)
        book.pic((36,158,558,585),out.getvalue())
        y=book.wrap(36,620,f'{qa["pieces"]:,} 件 ／ {qa["bags"]} 袋 ／ {qa["steps"]} 步　 底座 {model["width"]} × {model["depth"]} 凸點',520,14,21)
        book.wrap(36,y+12,'已檢查數位組裝步序、扣點及碰撞；未做實體拼裝、負重或運輸測試。完整安裝請用離線 HTML。',520,12,20)
        book.finish_page()
    book.save(folder/'architecture.pdf')
    lines=[f'# {model["name"]}','',ref['observation'],'',ref['interpretation'],'','## 拼裝與比例','',
          f'- 底座 {model["width"]} × {model["depth"]} 凸點，約 {model["width"]*.8:.1f} × {model["depth"]*.8:.1f} cm；最高約 {qa["maxLayer"]*.32:.1f} cm，不含凸點露出。',
          f'- 共 {qa["pieces"]:,} 件、{qa["bags"]} 袋、{qa["steps"]} 步，{qa["selectedPartColors"]} 組零件×顏色用 LEGO 官方料號表核對。',
          '- 川堂淨跨 22 凸點。前側上跨及後側較低的集會堂跨梁，先以兩側長板各自扣入，再用中央長板與交叉板鎖合，中央沒有落地結構柱。',
          '- 一樓剖切以場地圖中的兩中庭和穿越式川堂為參考，不是施工圖；平屋頂、玻璃反射、LED、景觀尺寸與樓高皆縮尺近似。',
          '- 數位檢查不等同實體承載；裝配時托住未鎖合的長板，完整上層未閉合前勿移動底座。','','## 來源','']
    lines+=['- ['+r['label']+']('+r['url']+')' for r in ref['sources']]
    (folder/'architecture.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    architecture()
    generate(model,ROOT,folder,ref,print_excerpts=True)
