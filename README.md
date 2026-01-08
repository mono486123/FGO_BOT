
---

# 🤖 FGO Auto Bot 全自動永動機開發指南 (2024 更新版)

本專案是一個基於 **Python + ADB** 開發的《Fate/Grand Order》自動化腳本，實現了從選支援、3T 戰鬥邏輯到自動吃果實的完整永動循環。

## 📂 專案檔案結構 (最新)

```text
D:\fgo_bot\
├── main.py                 # 【指揮官】串接所有流程，負責全域 IP 同步
├── requirements.txt        # Python 套件依賴清單 (opencv, numpy, pytesseract)
├── .gitignore              # 排除 venv 與暫存圖檔
│
├── modules\                # 【功能模組】各階段的自動化邏輯
│   ├── support_selector.py     # 選支援邏輯 (支援玩家名+從者名雙重比對)
│   ├── battle_manager.py       # 核心戰鬥模組 (整合了裁切、辨色、選卡邏輯)
│   ├── battle_end_handler.py   # 結算畫面跳過與自動吃果實邏輯
│   └── card_processor\         # 【工具單元】
│       └── capture_screen.py   # ADB exec-out 高速截圖工具
│
├── assets\                 # 【靜態資源】比對用的原始模板
│   ├── results\            # 結算 (羈絆、EXP、連續出擊按鈕)
│   └── support\            # 支援 (玩家名、從者名)
│
├── logs\                   # 【運作紀錄】
│   ├── battle\             # 回合數字模板 (battle_1_black.png 等)
│   ├── temp_cards\         # 裁切後的 5 張指令卡及辨色暫存
│   ├── screen.png          # 目前手機畫面即時截圖
│   └── attack.png          # Attack 按鈕特徵圖
│
└── platform-tools-...\     # ADB 工具包

```

## 🛠️ 環境配置

1. **Python 3.x**: 建議使用虛擬環境 `venv`。
2. **Tesseract OCR**: 位於 `D:\fgo_bot\pytesseract\tesseract.exe`。
3. **依賴安裝**: `pip install opencv-python numpy pytesseract Pillow`。

## 📡 啟動流程與連線

### 第一步：同步 DEVICE_IP

在 `main.py` 中修改 `DEVICE_IP`。程式啟動後會自動將此 IP 同步到所有子模組（選支援、戰鬥、結算）。

### 第二步：無線 ADB 連線 (PowerShell)

```powershell
adb kill-server
adb connect 10.191.176.213:38345 # 替換為手機當前 Port

```

### 第三步：執行程式

```powershell
python main.py

```

## 核心功能說明

* **自動 IP 同步**: `main.py` 具備 `sync_all_ips()` 功能，確保所有模組對準同一個裝置。
* **高速戰鬥辨識**: `battle_manager.py` 現在是整合體，直接在記憶體內處理卡片裁切與 HSV 辨色，不再依賴外部腳本呼叫，反應速度更快。
* **靈活的選卡優先級**: 預設優先選擇 **Buster (紅) > Arts (藍) > Quick (綠)**。
* **自動吃果實**: 當偵測到體力不足時，會自動點擊黃金果實並繼續出擊。

## ⚠️ 開發注意事項

1. **解析度限制**: 目前座標基於 2400x1080 解析度。
2. **路徑固定**: 專案內使用 `D:\fgo_bot\` 硬編碼路徑，移動資料夾後需檢查 `battle_manager.py` 等檔案內的路徑設定。
3. **OCR 偵測**: 若回合數偵測不準，請調整 `detect_battle_turn` 內的二值化閾值或 ROI 區域。

---
