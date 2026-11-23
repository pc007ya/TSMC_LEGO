"""Route only repository-owned assets to an offline Chrome renderer."""
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

@contextmanager
def open_studio(root):
    origin='http://fabform.invalid'
    allowed={
        '/tools/print-scene.js','/placement.js','/assets/vendor/three.module.min.js','/assets/vendor/three.core.min.js',
        '/assets/parts/library.js','/assets/parts/index.json','/assets/parts/geometry.bin'
    }
    allowed.update('/assets/decals/'+p.name for p in (root/'assets/decals').glob('*.svg'))
    with sync_playwright() as engine:
        browser=engine.chromium.launch(channel='chrome',headless=True,args=['--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        context=browser.new_context(offline=True)
        def route(r):
            path=urlparse(r.request.url).path
            if r.request.url==origin+'/':
                r.fulfill(content_type='text/html',body='<html lang="zh-Hant"><title>Fabform print studio</title></html>')
            elif r.request.url.startswith(origin+'/') and path in allowed:
                file=root/path.lstrip('/')
                r.fulfill(path=str(file),content_type={'.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.bin':'application/octet-stream'}[file.suffix])
            else:r.abort()
        context.route('**/*',route);page=context.new_page();page.goto(origin+'/')
        yield page
        browser.close()
