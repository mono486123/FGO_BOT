這是一個非常完整的 FGO 自動化腳本開發專案。根據你提供的檔案結構與程式碼，我為你整理了一份 **README.md**。

這份文件能幫助你記錄目前的開發進度、環境需求以及各個模組的功能，方便日後維護或上傳 GitHub。

---

# FGO Auto Bot (Python + ADB)

這是一個基於 Python 與 ADB (Android Debug Bridge) 開發的《Fate/Grand Order》自動化腳本，旨在實現基本的 **3T (3-Turn)** 自動通關。

## 📂 檔案結構

* **`main_auto_select_cards.py`**: 主程式，控制整體戰鬥流程、回合偵測與卡片選擇。
* **`capture_screen.py`**: 透過 ADB 擷取手機畫面並儲存為 `screen.png`。
* **`auto_crop_cards.py`**: 從 `screen.png` 中裁切出五張指令卡。
* **`classify_cards.py`**: 使用 HSV 顏色空間將卡片分類為紅 (Buster)、藍 (Arts)、綠 (Quick)。
* **`action.py`**: 封裝 ADB 指令，提供點擊 (tap) 與滑動 (swipe) 功能。
* **`test_detect_turn.py`**: 回合數偵測測試工具。
* **`templates/`**: 存放裁切後與分類後的指令卡暫存圖。
* **`battle/`**: 存放用於比對回合數 (1/3, 2/3, 3/3) 的模板圖片。

---

## 🛠️ 環境準備

1. **Python 3.x**: 建議使用虛擬環境 (`venv`)。
2. **ADB 工具**: 需放置於 `D:\fgo_bot\platform-tools-latest-windows`。
3. **Tesseract OCR**: 需安裝於 `D:\fgo_bot\pytesseract\tesseract.exe` 以進行文字辨識。
4. **必要套件**:
```bash
pip install opencv-python numpy pytesseract

```



---

## 🚀 核心功能說明

### 1. 回合偵測 (OCR + Template Matching)

系統會先擷取畫面右上角的「Battle x/3」區域。

* **OCR**: 使用 `pytesseract` 識別數字。
* **Fallback**: 若 OCR 失敗，會使用 `cv2.matchTemplate` 與 `battle/` 資料夾內的圖片進行比對。

### 2. 卡片分類與選擇

* **顏色辨識**: 透過 HSV 濾波計算每個色域的像素點，判定卡片顏色。
* **排序邏輯**: 預設優先選擇順序：**紅色 (Buster) > 藍色 (Arts) > 綠色 (Quick)**。

### 3. 戰鬥腳本 (`TURN_SCRIPT` & `NP_SCRIPT`)

在 `main_auto_select_cards.py` 中可以自定義每一回合要釋放的技能與寶具：

* **技能**: 透過座標點擊從者技能。
* **寶具**: 在選卡階段點擊寶具卡位置。

---

## 📝 使用方式

1. 開啟手機/模擬器的 **ADB 偵錯**。
2. 修改 `main_auto_select_cards.py` 中的 `DEVICE_IP` 為你的裝置位址。
3. 在戰鬥開始介面執行：
```bash
python main_auto_select_cards.py

```



---

## ⚠️ 注意事項

* **座標適配**: 目前座標基於固定解析度，若螢幕比例不同需重新調整 `CARD_CENTERS` 與 `SKILL_POS`。
* **路徑固定**: 目前程式碼內含大量硬編碼路徑 (Hardcoded paths)，搬移資料夾時需同步更新。

---

**需要我幫你將這些路徑重構成「相對路徑」，讓你在不同電腦上跑起來更方便嗎？**



```
D:\fgo_bot\
├── main.py                     # 【入口】一鍵啟動永動機（串接所有流程）
├── config.py                   # 【設定】存放 IP、所有路徑與座標設定
├── capture_screen.py           # 【工具】底層截圖與 ADB 基礎通訊
│
├── modules/                    # 【模組】存放各階段的邏輯
│   ├── support_selector.py     # 原 test_detect_support.py (選好友)
│   ├── battle_manager.py       # 原 battle.py + action.py (放技能/點卡)
│   ├── battle_end_handler.py   # 原 battle_end_handler.py (結算/吃果實)
│   ├── card_processor.py       # 原 auto_crop_cards.py + classify_cards.py
│   └── adb_commands.py         # 統一管理所有 adb -s 指令
│
├── assets/                     # 【素材】存放所有比對用的圖片
│   ├── support/                # 好友模板 (player_name, servant_name)
│   ├── battle/                 # 戰鬥模板 (attack.png)
│   └── results/                # 結算模板 (bond_title, exp_title, next_btn, cont_yes, ap_window)
│
└── logs/                       # 【輸出】存放產生的截圖與 Debug 圖
    ├── screen.png              # 運作中的即時截圖
    ├── debug_view.png          # 裁切預覽圖
    └── temp_cards/             # 存放裁切出來的五張卡片
```