# FABFORM · TSMC 晶圓建築積木

依五張單角度照片重構的五款獨立積木建築，共 1,958 件、20 袋、286 個組裝步驟。同一份逐件模型資料用於 3D 展示、說明書、分袋、BOM 和 LDraw 輸出。

[進入 GitHub Pages](https://pc007ya.github.io/TSMC_LEGO/) · [下載全系列採購表](downloads/collection-bom.csv)

| 模型 | 參考圖檔名前綴 | 底座（凸點） | 件數 | 袋數 | 步數 | 手冊與零件 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| FAB 01 雙塔研發大樓 | 925877080 | 24 × 24 | 454 | 4 | 68 | [PDF](downloads/twin/manual.pdf) · [圖解](downloads/twin/manual.html) · [MD](downloads/twin/manual.md) · [BOM](downloads/twin/bom.csv) · [LDraw](downloads/twin/model.ldr) |
| FAB 02 直柵晶圓廠 | 926523184 | 32 × 24 | 453 | 4 | 66 | [PDF](downloads/fins/manual.pdf) · [圖解](downloads/fins/manual.html) · [MD](downloads/fins/manual.md) · [BOM](downloads/fins/bom.csv) · [LDraw](downloads/fins/model.ldr) |
| FAB 03 JASM 水平窗帶廠 | 922961411 | 40 × 16 | 447 | 4 | 63 | [PDF](downloads/ribbon/manual.pdf) · [圖解](downloads/ribbon/manual.html) · [MD](downloads/ribbon/manual.md) · [BOM](downloads/ribbon/bom.csv) · [LDraw](downloads/ribbon/model.ldr) |
| FAB 04 石墨機電廠房 | 923365290 | 32 × 24 | 309 | 4 | 44 | [PDF](downloads/graphite/manual.pdf) · [圖解](downloads/graphite/manual.html) · [MD](downloads/graphite/manual.md) · [BOM](downloads/graphite/bom.csv) · [LDraw](downloads/graphite/model.ldr) |
| FAB 05 弧庭研發園區 | 920718279 | 32 × 24 | 295 | 4 | 45 | [PDF](downloads/arc/manual.pdf) · [圖解](downloads/arc/manual.html) · [MD](downloads/arc/manual.md) · [BOM](downloads/arc/bom.csv) · [LDraw](downloads/arc/model.ldr) |

## 在網頁上組裝

從上方選擇模型。用滑鼠或單指拖曳旋轉、滾輪或雙指縮放。「開始組裝」會顯示該款的盒裝。點盒蓋、拆開當前編號的零件袋，畫面會顯示本步的料號、取件數量以及橘色安裝框。點橘框或「裝上這一件」即可扣合，也可選「完成本步」一次裝上這一步的其餘零件。完成一袋後再拆下一袋。

各款的組裝進度分別存在目前瀏覽器，切換模型或重新整理後可從「繼續組裝」接續。「組裝手冊」可直接查看任何步驟，「設計檔案」可下載模型與手冊。缺少 WebGL 的裝置會顯示完成模型預覽及逐件俯視定位圖。

## 按說明書備料

每款的 BOM 按料號、顏色、整盒件數及各袋用量分類。全系列採購表將相同料號與顏色加總，可一次準備五款並同時展示。說明書以底座左後角為原點，X 往右、Z 往前，首格標為 1；底高以薄板層數表示，桌面為 0，標準磚高 3 層。底板先平放排齊，再覆上交錯的第二層跨接板縫。列印 PDF 或下載整本獨立 HTML，即可離線使用手冊。

模型名稱依照片外觀命名。圖片無法確定的背面、屋頂支撐和袋序均為本專案設計。驗證含數位碰撞、垂直安裝路徑、凸點承接、完工連通性、用色、LDraw 位置和分袋數量。接合力、承重及搬運耐受度仍待實體試拼。

## 檔案與重建

- `data/models.json` 保存每件積木的料號、色碼、位置、方向、袋號及步序。`data/catalog.json` 記錄零件尺寸與 LDraw 色號。
- `downloads/<模型>/` 含 PDF、獨立 HTML、Markdown、BOM CSV、分步 LDraw 模型。
- 從專案根目錄執行 `python3 tools/design.py` 重新產生模型並檢查連接與空間佔用，執行 `python3 tools/manuals.py` 重建說明書來源及單款 BOM，執行 `python3 tools/collection.py` 重建全系列 BOM。圖解產生器使用 Pillow 與 PyMuPDF。安裝 Playwright 與 Chrome 後，執行 `python3 tools/manuals.py --pdf-only` 可重新輸出五本 PDF。
- 在根目錄執行 `python3 -m http.server 8000`，即可由瀏覽器開啟本機網站。網頁與 Three.js 使用同站檔案；獨立 HTML 手冊可直接雙擊開啟。
- GitHub Pages 以 main 分支的根目錄為發布來源。

## 參考與授權

分袋目錄、逐步取件數及定位圖參考 LEGO Architecture 的閱讀方式。圖示、模型與組裝步驟由本專案重新產生。[LEGO Architecture 21028 說明書](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6172680.pdf)

3D 零件取自 LDraw 官方圖庫。零件配色依 Rebrickable 的盒組用料資料核對。網頁繪圖使用 Three.js r180。[LDraw 作者與授權](assets/parts/CREDITS.md) · [配色與盒組佐證](tools/stock.md) · [Three.js MIT 授權](assets/vendor/THREE-LICENSE.txt)
