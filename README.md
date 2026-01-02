這是一份為你整合後的 **FGO Auto Bot 綜合開發指南 (`README.md`)**。我已經將你提供的檔案結構、ADB 連結步驟、以及虛擬環境（venv）的疑難排解全部混合在一起，讓你以後只需看這份文件就能完成所有操作。

---

# 🤖 FGO Auto Bot 全自動永動機開發指南

本專案是一個基於 **Python + ADB** 開發的《Fate/Grand Order》自動化腳本，旨在實現從「搜尋好友」到「3T 戰鬥」再到「吃果實續戰」的完整自動化循環。

## 📂 專案檔案結構

* **`main.py`**: 核心指揮官，負責串接選支援、戰鬥與結算流程。
* **`modules/support_selector.py`**: 搜尋特定玩家與從者，進入關卡。
* **`modules/battle_manager.py`**: 核心戰鬥模組，包含 Wave 偵測、技能/寶具施放與指令卡顏色優先級辨識。
* **`modules/battle_end_handler.py`**: 處理戰鬥後的羈絆、經驗值跳過，以及連續出擊與自動吃果實邏輯。
* **`capture_screen.py`**: 透過 ADB `exec-out` 快速擷取手機畫面，這是目前最快的純 ADB 截圖方式。
* **`action.py`**: 封裝 ADB 指令，提供穩定的 `tap`（點擊）與 `swipe`（滑動）功能。
* **`logs/`**: 存放執行中的截圖 (`screen.png`)、裁切後的卡片與 Debug 預覽圖。
```
D:\fgo_bot\
├── .gitignore              # Git 忽略清單 (排除 venv, __pycache__ 等)
├── README.md               # 專案說明文件 (包含連線步驟與操作說明)
├── config.py               # 全域設定檔 (管理 DEVICE_IP 與各項路徑參數)
├── main.py                 # 永動機指揮官 (串接所有自動化流程的主程式)
├── requirements.txt        # Python 依賴套件清單 (opencv, numpy, pytesseract)
│
├── assets\                 # 【靜態資源】存放比對用的原始模板圖
│   ├── results\            # 結算畫面模板 (羈絆、經驗值、連續出擊按鈕)
│   └── support\            # 選支援模板 (玩家名、從者名)
│
├── logs\                   # 【運作紀錄與暫存】存放執行中的截圖與 Debug 圖
│   ├── battle\             # 戰鬥回合數字模板 (battle_1_black.png 等)
│   ├── temp_cards\         # 裁切後的五張指令卡暫存區
│   ├── attack.png          # Attack 按鈕特徵圖
│   ├── screen.png          # 目前手機畫面即時截圖
│   └── debug_view.png      # 指令卡裁切範圍預覽圖
│
├── modules\                # 【功能模組】各階段的自動化邏輯
│   ├── battle_end_handler.py   # 結算與 AP 恢復邏輯
│   ├── battle_manager.py       # 3T 戰鬥邏輯 (含 Wave 偵測與選卡)
│   ├── support_selector.py     # 好友支援選取邏輯
│   │
│   └── card_processor\      # 【卡片處理單元】底層工具
│       ├── action.py           # ADB 點擊與滑動指令封裝
│       └── capture_screen.py   # ADB 高速截圖工具
│
├── venv\                   # Python 虛擬環境 (存放相關 Library)
├── platform-tools-latest-windows\  # ADB 工具包
└── __pycache__\            # Python 編譯暫存檔 (自動產生)


```
---

## 🛠️ 環境配置需求

1. **Python 3.x**: 必須在虛擬環境執行。
2. **虛擬環境路徑**: `D:\fgo_bot\venv`。
3. **ADB 工具**: 位於 `D:\fgo_bot\platform-tools-latest-windows`。
4. **Tesseract OCR**: 位於 `D:\fgo_bot\pytesseract\tesseract.exe`。
5. **必要套件**: `pip install opencv-python numpy pytesseract`。

---

## 📡 無線偵錯 (WiFi ADB) 連結步驟

為了確保連線穩定，請務必按照以下順序執行。若連線失敗，請先「關閉無線偵測」再重新啟用。

### 第一步：清理與重啟服務

有時候舊的連線資訊會導致衝突，請先執行：

```powershell
adb kill-server
adb start-server

```

### 第二步：配對裝置 (Pairing)

當手機顯示「配對碼」時，輸入以下指令：

```powershell
adb pair 10.191.176.213:[配對Port]
# 隨後輸入手機顯示的 6 位配對碼

```

### 第三步：正式連線 (Connect)

配對成功後，使用手機主頁面顯示的「連線 Port」進行連線：

```powershell
adb connect 10.191.176.213:41335

```

---

## 💻 虛擬環境與 VS Code 修復

若遇到 VS Code 選錯 Python 或抓不到 venv 的問題，請透過終端機啟動：

1. 開啟 PowerShell 並切換至專案目錄：`cd "D:\fgo_bot"`。
2. 啟動 venv：`.\venv\Scripts\activate`。
3. **透過此環境啟動 VS Code**：輸入 `code .` 讓 VS Code 直接繼承當前的環境路徑。

---

## 📋 ADB 指令速查表 (除錯用)

| 功能 | 指令 | 說明 |
| --- | --- | --- |
| **列出裝置** | `adb devices` | 確認是否出現 `device` 字樣 |
| **指定裝置點擊** | `adb -s [ID] shell input tap x y` | 多裝置環境下防止指令發錯對象 |
| **手動滑動** | `adb shell input swipe x1 y1 x2 y2 ms` | 測試下滑尋找支援的長度 |
| **快速截圖** | `adb exec-out screencap -p > test.png` | 檢查目前的畫面內容 |
| **解析度檢查** | `adb shell wm size` | 確保遊戲解析度與腳本座標邏輯相符 |

---

## ⚠️ 開發注意事項

* **解析度適配**: 座標基於特定解析度（2400x1080），若更換設備需調整 `CARD_CENTERS`。
* **路徑硬編碼**: 專案內含有多處 `D:\fgo_bot\` 路徑，搬移資料夾時務必同步檢查。
* **穩定性**: 如果發現截圖變慢，請確認是否透過 `capture_screen.py` 的 `exec-out` 資料流處理。

---

**下一步建議：**
我已經將所有開發細節整理完畢。現在你可以放心地進行 Git 提交。當你準備好進行第一次「永動機」實測時，我可以直接為你撰寫 **`config.py`**，將所有 Port 和路徑變數徹底分離出來。

需要我現在幫你寫那份 **`config.py`** 嗎？