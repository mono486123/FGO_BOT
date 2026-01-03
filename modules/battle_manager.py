import os
import cv2
import time
import subprocess
import numpy as np
import glob
import card_processor.capture_screen as cs  # 引入截圖功能模組

# ====================================================
# 1. 環境與路徑設定
# ====================================================
DEVICE_IP = ""
IMG_PATH = r"D:\fgo_bot\logs\screen.png"
OUT_DIR = r"D:\fgo_bot\logs\temp_cards" # 裁切卡片存放處
ATTACK_TEMPLATE = r"D:\fgo_bot\logs\attack.png"
BATTLE_DIR = r"D:\fgo_bot\logs\battle"
DEBUG_PATH = r"D:\fgo_bot\logs\debug_view.png"



# ====================================================
# 1-2. ADB 內建動作函式 (原 action.py 內容)
# ====================================================

def tap(x, y, delay=0.15):
    """執行點擊，強制指定當前的 DEVICE_IP"""
    subprocess.run(["adb", "-s", DEVICE_IP, "shell", "input", "tap", str(x), str(y)])
    time.sleep(delay)

def swipe(x1, y1, x2, y2, dur=150, delay=0.2):
    """執行滑動，強制指定當前的 DEVICE_IP"""
    subprocess.run([
        "adb", "-s", DEVICE_IP, "shell", "input", "swipe",
        str(x1), str(y1), str(x2), str(y2), str(dur)
    ])
    time.sleep(delay)

def capture_screen(path):
    """使用指定 IP 截圖"""
    cs.capture_screen(path, device_id=DEVICE_IP)





# ====================================================
# 2. 座標與排程設定
# ====================================================
CARD_CENTERS = [(500, 750), (900, 750), (1200, 750), (1500, 750), (1900, 750)]

SKILL_POS = {
    1: [(200, 850), (300, 850), (450, 850)],
    2: [(700, 850), (800, 850), (950, 850)],
    3: [(1100, 850), (1300, 850), (1400, 850)]
}

CONFIRM_BTN = (1500, 650)
FAST_FORWARD_POS = (1200, 600)

TURN_SCRIPT = { 
    1: [(1, 1)],            
    2: [(2, 1)],            
    3: [(3, 1), (3, 2)]      
}

NP_SCRIPT = { 1: 1, 2: 2, 3: 3 }
NP_POS = { 1: (860, 350), 2: (1200, 350), 3: (1600, 350) }

# ====================================================
# 3. 整合：裁切與分類邏輯 (不再呼叫外部腳本)
# ====================================================

def internal_auto_crop():
    """整合自 auto_crop_cards.py: 裁切 5 張指令卡"""
    img = cv2.imread(IMG_PATH)
    if img is None:
        print("❌ 無法讀取 screen.png")
        return False

    os.makedirs(OUT_DIR, exist_ok=True)
    # 清空舊卡片
    for f in os.listdir(OUT_DIR):
        if f.endswith(".png"): os.remove(os.path.join(OUT_DIR, f))
    
    h, w = img.shape[:2]
    top, bottom = int(h * 0.48), int(h * 0.82)
    card_ratios = [(0.13, 0.228), (0.3, 0.408), (0.45, 0.57), (0.61, 0.72), (0.7705, 0.885)]

    for i, (r1, r2) in enumerate(card_ratios):
        x1, x2 = int(w * r1), int(w * r2)
        card = img[top:bottom, x1:x2]
        cv2.imwrite(os.path.join(OUT_DIR, f"card{i+1}.png"), card)
    return True

def internal_classify_card(img):
    """整合自 classify_cards.py: 辨識單張卡片顏色"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 定義顏色範圍
    blue_mask = cv2.inRange(hsv, np.array([90, 80, 50]), np.array([130, 255, 255]))
    red_mask = cv2.inRange(hsv, np.array([0, 80, 50]), np.array([10, 255, 255])) | \
               cv2.inRange(hsv, np.array([160, 80, 50]), np.array([180, 255, 255]))
    green_mask = cv2.inRange(hsv, np.array([40, 80, 50]), np.array([80, 255, 255]))

    b, r, g = np.sum(blue_mask > 0), np.sum(red_mask > 0), np.sum(green_mask > 0)
    if b >= r and b >= g: return "blue"
    if r >= b and r >= g: return "red"
    return "green"

def internal_process_all_cards():
    """整合自 classify_cards.py: 分類所有裁切出的卡片並重新命名"""
    png_list = sorted(glob.glob(os.path.join(OUT_DIR, "card*.png")))
    for file in png_list:
        img = cv2.imread(file)
        if img is None: continue
        ctype = internal_classify_card(img)
        # 重新命名以便 decide_order 辨識
        new_name = f"{ctype}_{os.path.basename(file)}"
        cv2.imwrite(os.path.join(OUT_DIR, new_name), img)

# ====================================================
# 4. 戰鬥核心工具
# ====================================================

def capture_screen(path):
    cs.capture_screen(path, device_id=DEVICE_IP)

def detect_battle_turn():
    img = cv2.imread(IMG_PATH)
    if img is None: return None
    h, w = img.shape[:2]
    # 使用你調整過的精確座標
    roi = img[int(h*0.02):int(h*0.0571), int(w*0.72):int(w*0.745)]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)

    best_val, detected_turn = -1, None
    for t in [1, 2, 3]:
        tmpl = cv2.imread(os.path.join(BATTLE_DIR, f"battle_{t}_black.png"), 0)
        if tmpl is None: continue
        res = cv2.matchTemplate(thresh, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > 0.6 and max_val > best_val: # 稍微提高門檻避免誤判
            best_val, detected_turn = max_val, t
    return detected_turn

def decide_order():
    """原本的 decide_order 邏輯"""
    files = os.listdir(OUT_DIR)
    order = []
    for i in range(1, 6):
        for f in files:
            if f"card{i}" in f:
                if f.startswith("red_"): order.append((1, i))
                elif f.startswith("blue_"): order.append((2, i))
                elif f.startswith("green_"): order.append((3, i))
    order.sort(key=lambda x: x[0])
    return [idx for _, idx in order]

# ====================================================
# 5. 操作流程
# ====================================================

def cast_skill(serv, skill):
    x, y = SKILL_POS[serv][skill-1]
    print(f"👉 從者{serv} 技能{skill}")
    tap(x, y)
    time.sleep(0.5)
    tap(*CONFIRM_BTN)
    time.sleep(2.5) # 稍微增加等待動畫時間

def auto_cards_with_np(turn):
    """整合後的選卡邏輯"""
    capture_screen(IMG_PATH)
    if internal_auto_crop(): # 內部裁切
        internal_process_all_cards() # 內部辨識顏色
    
    chosen_count = 0
    np_serv = NP_SCRIPT.get(turn, 0)
    if np_serv != 0:
        print(f"💥 施放寶具：從者 {np_serv}")
        tap(*NP_POS[np_serv])
        chosen_count += 1
    
    seq = decide_order()
    for idx in seq[:(3 - chosen_count)]:
        tap(*CARD_CENTERS[idx-1])
        time.sleep(0.2)

def main():
    print("🔥 整合版 3T 戰鬥管理員啟動")
    os.system(f"adb connect {DEVICE_IP}")
    last_turn = 0
    
    # 初始偵測
    while last_turn == 0:
        capture_screen(IMG_PATH)
        last_turn = detect_battle_turn() or 0
        time.sleep(1)

    while True:
        print(f"\n===== 🎯 Wave {last_turn} 開始 =====")
        
        # 等待 Attack 按鈕 (由 wait_attack 提供)
        while True:
            capture_screen(IMG_PATH)
            screen = cv2.imread(IMG_PATH)
            templ = cv2.imread(ATTACK_TEMPLATE)
            res = cv2.matchTemplate(screen, templ, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.75:
                attack_pos = (max_loc[0] + templ.shape[1]//2, max_loc[1] + templ.shape[0]//2)
                break
            time.sleep(1)

        # 執行技能
        for (serv, skill) in TURN_SCRIPT.get(last_turn, []):
            cast_skill(serv, skill)

        tap(*attack_pos) # 進入選卡
        time.sleep(1.5)
        auto_cards_with_np(last_turn) # 選卡

        if last_turn == 3:
            print("🎉 戰鬥完成！")
            break

        print("⏳ 等待 Wave 更新…")
        while True:
            capture_screen(IMG_PATH)
            new_turn = detect_battle_turn()
            if new_turn and new_turn != last_turn:
                last_turn = new_turn
                break
            time.sleep(2)

if __name__ == "__main__":
    main()