import os
import cv2
import time
import subprocess
import numpy as np
import pytesseract

from action import tap  # 引入 ADB 點擊功能 [cite: 1, 2]
import capture_screen as cs  # 引入截圖功能模組 

# ====================================================
# 1. 環境與路徑設定
# ====================================================
DEVICE_IP = "10.191.176.213:41335"  # 手機/模擬器 ADB 連線位址
IMG_PATH = r"D:\fgo_bot\capture_screen\screen.png" # 暫存截圖路徑 
TEMPLATE_DIR = r"D:\fgo_bot\capture_screen\templates" # 裁切後的卡片存放處 
ATTACK_TEMPLATE = r"D:\fgo_bot\capture_screen\attack.png" # Attack 按鈕模板 [cite: 1, 2]
BATTLE_DIR = r"D:\fgo_bot\capture_screen\battle" # 回合數辨識模板資料夾 [cite: 1, 2]

# 虛擬環境 Python 路徑與 Tesseract OCR 路徑 [cite: 3]
VENV_PY = r"D:\fgo_bot\venv\Scripts\python.exe"
pytesseract.pytesseract.tesseract_cmd = r"D:\fgo_bot\pytesseract\tesseract.exe"

# ====================================================
# 2. 座標參數設定 (根據螢幕解析度調整)
# ====================================================
# 五張指令卡中心點座標
CARD_CENTERS = [(500, 750), (900, 750), (1200, 750), (1500, 750), (1900, 750)]

# 從者技能位置: {從者編號: [技能1, 技能2, 技能3]}
SKILL_POS = {
    1: [(200, 850), (300, 850), (450, 850)],
    2: [(700, 850), (800, 850), (950, 850)],
    3: [(1100, 850), (1300, 850), (1400, 850)]
}

CONFIRM_BTN = (1500, 650)      # 技能確認按鈕
FAST_FORWARD_POS = (1200, 600) # 加速/關閉技能動畫點擊處

# 腳本排程: {回合數: [(從者, 技能)]}
TURN_SCRIPT = { 
    1: [(1, 1)],            # 第1回：施放從者1的技能1
    2: [(2, 1)],            # 第2回：施放從者2的技能1
    3: [(3, 1), (3, 2)]      # 第3回：施放從者3的技能1、2
}

# 寶具設定: {回合數: 施放哪位從者的寶具}
NP_SCRIPT = { 1: 1, 2: 2, 3: 3 }
NP_POS = { 1: (860, 350), 2: (1200, 350), 3: (1600, 350) }

# ====================================================
# 3. 核心工具函式
# ====================================================

def capture_screen(path):
    """呼叫 capture_screen 模組擷取畫面 """
    cs.capture_screen(path, device_id=DEVICE_IP)

def run_crop():
    """執行外部指令裁切 5 張指令卡 """
    subprocess.run([VENV_PY, r"D:/fgo_bot/capture_screen/auto_crop_cards.py"])

def run_classify():
    """執行外部指令分類卡片顏色 (R/B/G) """
    subprocess.run([VENV_PY, r"D:/fgo_bot/capture_screen/classify_cards.py"])

def find_attack_button(screen_path, templ_path, threshold=0.75):
    """比對 Attack 按鈕是否存在，返回座標 [cite: 2]"""
    screen = cv2.imread(screen_path)
    templ = cv2.imread(templ_path)
    if screen is None or templ is None: return None
    res = cv2.matchTemplate(screen, templ, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        # 計算中心點
        cx = pt[0] + templ.shape[1] // 2
        cy = pt[1] + templ.shape[0] // 2
        return (cx, cy)
    return None

def detect_battle_turn():
    img = cv2.imread(IMG_PATH) 
    if img is None: return None
    h, w = img.shape[:2] 

    # --- 調整後的精確座標 (往左放大並縮小範圍) ---
    # 原本 x1 可能太靠右，我們將 x1 往左移 (w * 0.70)
    # 縮窄寬度 (只看數字區，避開後面的 /3)
    x1 = int(w * 0.72)  
    x2 = int(w * 0.745)  
    y1 = int(h * 0.02)  
    y2 = int(h * 0.0571)  
    
    roi = img[y1:y2, x1:x2]

    # 影像處理：轉灰階並執行黑化 [cite: 1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # 使用較高的門檻 210 以確保背景全黑 [cite: 1]
    _, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    # 儲存目前的截圖供你確認位置
    #cv2.imwrite(r"D:\fgo_bot\capture_screen\debug_final_zoom.png", thresh)

    best_val = -1
    detected_turn = None

    for t in [1, 2, 3]:
        tmpl_path = os.path.join(BATTLE_DIR, f"battle_{t}_black.png")
        tmpl = cv2.imread(tmpl_path, cv2.IMREAD_GRAYSCALE)
        if tmpl is None: continue

        # 🔥 防錯機制：如果截圖範圍(thresh)比模板(tmpl)還小，會導致程式崩潰
        # 我們自動將模板縮小到搜尋區域的 90% 大小
        if tmpl.shape[0] > thresh.shape[0] or tmpl.shape[1] > thresh.shape[1]:
            scale = min(thresh.shape[0] / tmpl.shape[0], thresh.shape[1] / tmpl.shape[1]) * 0.9
            tmpl = cv2.resize(tmpl, (0, 0), fx=scale, fy=scale)

        # 執行模板比對 [cite: 1]
        res = cv2.matchTemplate(thresh, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        # 只要信心值超過 0.7 就算成功
        if max_val > 0.1 and max_val > best_val:
            best_val = max_val
            detected_turn = t

    if detected_turn:
        print(f"🔍 縮放偵測成功: Wave {detected_turn} (信心值: {best_val:.2f})")
        return detected_turn
    return None


def decide_order():
    """根據卡片顏色優先順序排序 (紅 > 藍 > 綠) """
    files = os.listdir(TEMPLATE_DIR)
    order = []
    for i in range(1, 6):
        for f in files:
            if f"card{i}" in f:
                if f.startswith("red_"): order.append((1, i))
                elif f.startswith("blue_"): order.append((2, i))
                elif f.startswith("green_"): order.append((3, i))
    order.sort(key=lambda x: x[0]) # 依權重排序
    return [idx for _, idx in order]

# ====================================================
# 4. 戰鬥操作邏輯
# ====================================================

def cast_skill(serv, skill):
    """點擊指定從者的技能並處理確認視窗"""
    x, y = SKILL_POS[serv][skill-1]
    print(f"👉 從者{serv} 技能{skill}")
    tap(x, y) # [cite: 2]
    time.sleep(0.5)
    tap(*CONFIRM_BTN)      # 點擊技能確認
    time.sleep(1.0)
    tap(*FAST_FORWARD_POS) # 加速動畫
    time.sleep(2)

def auto_cards_with_np(turn):
    """執行選卡邏輯：先放寶具，再選一般指令卡"""
    capture_screen(IMG_PATH)
    run_crop()      # 裁切卡片 
    run_classify()  # 分類顏色 

    chosen_count = 0
    # 判斷是否施放寶具
    np_serv = NP_SCRIPT.get(turn, 0)
    if np_serv != 0:
        print(f"💥 施放寶具：從者 {np_serv}")
        tap(*NP_POS[np_serv])
        chosen_count += 1
    
    # 補足剩餘的指令卡 (總共選 3 張)
    seq = decide_order()
    need = 3 - chosen_count
    for idx in seq[:need]:
        tap(*CARD_CENTERS[idx-1])
        time.sleep(0.25)

def wait_attack(timeout=15):
    """循環偵測直到 Attack 按鈕出現"""
    start = time.time()
    while time.time() - start < timeout:
        capture_screen(IMG_PATH)
        pos = find_attack_button(IMG_PATH, ATTACK_TEMPLATE)
        if pos: return pos
        time.sleep(0.5)
    return None

# ====================================================
# 5. 主流程控制
# ====================================================

def main():
    global last_turn
    print("🔥 自動 3T 腳本啟動")
    os.system(f"adb connect {DEVICE_IP}") # 確保 ADB 連線

    # 初始回合偵測
    while True:
        capture_screen(IMG_PATH)
        turn = detect_battle_turn()
        if turn:
            print(f"📌 偵測到起始回合 {turn}")
            last_turn = turn
            break
        time.sleep(0.5)

    # 戰鬥主循環
    while True:
        print(f"\n===== 🎯 Wave {last_turn} 開始 =====")
        
        # 1. 等待玩家回合開始 (Attack 出現)
        pos = wait_attack()
        if not pos: continue

        # 2. 施放腳本定義的技能
        for (serv, skill) in TURN_SCRIPT.get(last_turn, []):
            cast_skill(serv, skill)

        # 3. 進入選卡畫面
        tap(*pos) # 點擊 Attack
        time.sleep(1.0)

        # 4. 執行選卡與寶具
        auto_cards_with_np(last_turn)

        # 5. 若是第三回合則結束，否則等待下一波
        if last_turn == 3:
            print("🎉 三回合戰鬥完成！")
            break

        # 6. 等待畫面轉場並更新 Wave 數
        print("⏳ 等待下一波 (Wave) 更新…")
        while True:
            capture_screen(IMG_PATH)
            new_turn = detect_battle_turn()
            if new_turn and new_turn != last_turn:
                last_turn = new_turn
                break
            time.sleep(0.5)

if __name__ == "__main__":
    main()