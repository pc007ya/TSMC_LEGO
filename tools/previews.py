"""Capture high-resolution packaging views and the part tray from the local Three.js source."""
import argparse
import base64
import json
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tray-only', action='store_true')
parser.add_argument('--model', choices=[m['id'] for m in json.loads((root/'data/models.json').read_text())], help='Update only this packaging view and the shared part tray')
parser.add_argument('--series', choices=['collection','taichung'])
args = parser.parse_args()
origin = 'http://fabform.invalid/'

def local(route):
    url = route.request.url
    name = unquote(urlparse(url).path.strip('/')) or 'index.html'
    path = (root / name).resolve()
    if url.startswith(origin) and root in path.parents and path.is_file():
        route.fulfill(path=str(path), content_type=mimetypes.guess_type(path)[0] or 'application/octet-stream')
    else:
        route.abort()

with sync_playwright() as engine:
    with engine.chromium.launch(channel='chrome',headless=True,args=['--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']) as browser:
        page=browser.new_page(viewport={'width':1380,'height':930},device_scale_factor=1.8)
        page.route('**/*',local)
        page.goto(origin)
        page.wait_for_selector('html[data-renderer="three"]',timeout=60000)
        tray=page.evaluate("async ()=> (await import('./tools/tray.js')).renderTray()")
        (root/'assets/parts/tray.webp').write_bytes(base64.b64decode(tray.pop('data')))
        (root/'data/tray.json').write_text(json.dumps(tray,separators=(',',':'))+'\n')
        if not args.tray_only:
            for model in json.loads((root/'data/models.json').read_text()):
                if args.series and args.series!=model.get('series','collection'):
                    continue
                if args.model and args.model!=model['id']:
                    continue
                page.locator(f'[data-model="{model["id"]}"]').click()
                views=[None]+model.get('views',[])
                for view in views:
                    if view:page.locator(f'[data-view="{view["id"]}"]').click()
                    page.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
                    encoded=page.locator('#viewport canvas').evaluate("c=>c.toDataURL('image/webp', .92).split(',')[1]")
                    suffix='-'+view['id'] if view else ''
                    (root/'assets/previews'/f'{model["id"]}{suffix}.webp').write_bytes(base64.b64decode(encoded))
