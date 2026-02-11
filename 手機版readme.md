這份 `README.md` 整理了你今天在 Android 手機 (Termux) 上開發 FGO 自動化腳本時，從遇到的所有報錯到最終解決方案的完整紀錄。這份文件可以幫助你未來回顧，或是讓其他人接手時知道如何避坑。

---

# FGO Auto Bot - Termux Android Native Version

這是專為 **Android 手機 (Realme GT 5G)** 透過 **Termux** 環境直接運行的 FGO 自動化腳本。不依賴電腦，直接在手機上實現 ADB 無線連線與 OpenCV 影像辨識。

## 🛠️ 開發環境與需求

* **裝置**: Android 手機 (測試於 Realme GT 5G)
* **環境**: Termux
* **語言**: Python 3
* **必要套件**: `opencv-python`, `numpy`, `android-tools` (ADB)
* **權限**: 必須開啟「允許管理所有檔案」權限給 Termux。

---

## 📂 專案結構

為解決路徑讀取問題，採用 **絕對路徑** 鎖定策略。請確保檔案放置於以下位置：

```text
/sdcard/fgo_bot/
│
├── main.py              # 核心執行檔 (整合連線、戰鬥、結算)
│
├── assets/              # 靜態資源資料夾
│   ├── support/         # 好友辨識 (player_name.png, servant_name.png)
│   └── results/         # 結算畫面 (bond_title.png, next_btn.png, ap_window.png 等)
│
└── logs/                # 執行時自動產生
    ├── screen.png       # 當前截圖
    ├── attack.png       # 藍色 Attack 按鈕模板
    └── battle/          # Wave 偵測模板 (battle_1_black.png 等)

```

---

## 🐛 故障排除紀錄 (Troubleshooting Log)

以下紀錄了開發過程中遇到的關鍵錯誤代碼與解決方案：

### 1. 輸入格式錯誤

* **錯誤訊息**: `/data/data/com.termux/.../sh: Syntax error: end of file unexpected`
* **原因**: 使用 `input()` 獲取 Port 時，手機鍵盤輸入可能帶有隱藏的換行符或空格，導致傳入 `subprocess` 時指令斷裂。
* **解決方案**: 在所有 `input()` 後面加上 `.strip()` 去除首尾空白。
```python
port = input("Enter Port: ").strip()

```



### 2. 截圖存檔失敗 (權限與路徑)

* **錯誤訊息**: `cannot create: Directory nonexistent` 或 `[WARN:0] imread_("): can't open/read file`
* **原因**:
1. Android 系統對 Termux 的寫入權限限制。
2. 在 Termux Shell 中使用 `>` (重導向符號) 輸出檔案到 `/sdcard` 時，路徑解析失敗。


* **解決方案**:
1. **棄用 Shell 重導向**：改用 Python 直接接收 ADB 的二進位數據並寫入檔案。
2. **鎖定絕對路徑**：將 `BASE_PATH` 強制設為 `/sdcard/fgo_bot`。


```python
# 修正後的截圖函式
cmd = ["adb", "-s", ip, "exec-out", "screencap", "-p"]
data = subprocess.check_output(cmd)
with open(path, "wb") as f: f.write(data)

```



### 3. OpenCV 尺寸錯誤 (ROI)

* **錯誤訊息**: `cv2.error: (-215:Assertion failed) _img.size().height <= _templ.size().height`
* **原因**: 在 `detect_battle_turn` 中，設定的 ROI (感興趣區域) 切割範圍過小，導致切割出來的圖片比「Wave 1」的模板圖片還要小，OpenCV 無法進行匹配。
* **解決方案**: 擴大 ROI 搜尋範圍，改為搜尋螢幕右上角 1/4 的區域，確保能容納任何尺寸的 Wave 模板。
```python
roi = img[0:int(h*0.2), int(w*0.5):w] # 擴大範圍

```



### 4. 結算流程卡住 (AP 恢復失效)

* **現象**: 點擊「連續出擊」後，畫面停留在吃蘋果視窗，但程式沒有反應或直接結束。
* **原因**: 點擊按鈕後**沒有重新截圖**。程式讀取的是點擊前的舊畫面 (Old Frame)，因此偵測不到新跳出來的 AP 視窗。
* **解決方案**: 在點擊 `ASSETS["cont"]` 後，強制執行 `capture_screen()` 刷新畫面緩存。

### 5. 模組引用災難

* **現象**: `ModuleNotFoundError` 或檔案路徑混亂。
* **原因**: 在手機上維護多個 `.py` 檔案並進行 `import`，容易因為執行目錄不同而找不到檔案。
* **解決方案**: **All-in-One 策略**。將 `support_selector`, `battle_manager`, `battle_end_handler` 全部整合進單一的 `main.py`，變數共用，維護最簡單。

---

## 🚀 如何使用

1. **開啟無線偵錯**: 確保手機開發者選項中的「無線偵錯」已開啟。
2. **執行腳本**:
```bash
python main.py

```


3. **互動配對**:
* 若為首次連線，輸入 `y` 並填入配對碼與配對 Port。
* 若已配對過，輸入 `n` 並直接填入連線 Port。



---

## ✨ 目前功能狀態

* ✅ **自動配對/連線**: 內建 `adb pair` 與 `adb connect`。
* ✅ **好友選擇**: 支援雙重圖片辨識 (玩家名 + 從者名)。
* ✅ **3T 戰鬥**: 支援 Wave 偵測、自訂技能腳本、寶具施放、紅卡優先選卡。
* ✅ **結算循環**: 自動跳過羈絆/EXP 畫面、自動點擊連續出擊。
* ✅ **體力監控**: 偵測 AP 不足時自動吃金蘋果並繼續循環。