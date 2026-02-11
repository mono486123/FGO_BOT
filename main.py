import os
import cv2
import time
import subprocess
import numpy as np
import platform
import glob
#
# ====================================================
# 1. 絕對路徑與配置 (鎖定手機路徑)
# ====================================================
DEVICE_IP = ""
# 針對 Termux 環境鎖定絕對路徑，解決目錄不存在報錯
BASE_PATH = "/sdcard/fgo_bot" if platform.system() != "Windows" else os.path.dirname(os.path.abspath(__file__))

LOG_DIR = os.path.join(BASE_PATH, "logs")
BATTLE_DIR = os.path.join(LOG_DIR, "battle")
OUT_DIR = os.path.join(LOG_DIR, "temp_cards")
IMG_PATH = os.path.join(LOG_DIR, "screen.png")

# 圖片資產路徑
ASSETS = {
    "player": os.path.join(BASE_PATH, "assets/support/player_name.png"),
    "servant": os.path.join(BASE_PATH, "assets/support/servant_name.png"),
    "attack": os.path.join(LOG_DIR, "attack.png"),
    "bond": os.path.join(BASE_PATH, "assets/results/bond_title.png"),
    "exp": os.path.join(BASE_PATH, "assets/results/exp_title.png"),
    "next": os.path.join(BASE_PATH, "assets/results/next_btn.png"),
    "cont": os.path.join(BASE_PATH, "assets/results/cont_yes.png"),
    "ap_window": os.path.join(BASE_PATH, "assets/results/ap_window.png")
}

# 戰鬥座標設定
CARD_CENTERS = [(500, 750), (900, 750), (1200, 750), (1500, 750), (1900, 750)]
SKILL_POS = {
    1: [(200, 850), (300, 850), (450, 850)],
    2: [(700, 850), (800, 850), (950, 850)],
    3: [(1100, 850), (1300, 850), (1400, 850)]
}
CONFIRM_BTN = (1500, 650)
NP_POS = { 1: (860, 350), 2: (1200, 350), 3: (1600, 350) }

# 3T 戰鬥腳本
TURN_SCRIPT = { 1: [(1, 1)], 2: [(2, 1)], 3: [(3, 1), (3, 2)] }
NP_SCRIPT = { 1: 1, 2: 2, 3: 3 }

# ====================================================
# 2. 核心通訊工具
# ====================================================

def capture_screen(path=IMG_PATH):
    """二進位截圖，避開 Shell 重導向報錯"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # 直接獲取數據流寫入，不透過 Shell 的 > 符號
        cmd = ["adb", "-s", DEVICE_IP.strip(), "exec-out", "screencap", "-p"]
        png_data = subprocess.check_output(cmd)
        with open(path, "wb") as f:
            f.write(png_data)
        return True
    except Exception: return False

def tap(x, y, delay=0.2):
    subprocess.run(["adb", "-s", DEVICE_IP.strip(), "shell", "input", "tap", str(x), str(y)])
    time.sleep(delay)

def find_img(screen, path, threshold=0.8):
    temp = cv2.imread(path)
    if temp is None or screen is None: return None
    res = cv2.matchTemplate(screen, temp, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val >= threshold:
        return (max_loc[0] + temp.shape[1]//2, max_loc[1] + temp.shape[0]//2)
    return None

# ====================================================
# 3. 功能流程模組
# ====================================================

def run_support():
    print("\n🔍 [1/3] 正在選擇好友...")
    swipe_cnt = 0
    while True:
        capture_screen()
        screen = cv2.imread(IMG_PATH)
        p = find_img(screen, ASSETS["player"])
        s = find_img(screen, ASSETS["servant"])
        if p and s and abs(p[1]-s[1]) < 250:
            print("✅ 匹配成功")
            tap(p[0], p[1])
            time.sleep(2); tap(2200, 1000); return True
        if swipe_cnt < 4:
            subprocess.run(["adb", "-s", DEVICE_IP.strip(), "shell", "input", "swipe", "1200", "800", "1200", "350", "600"])
            swipe_cnt += 1; time.sleep(2)
        else:
            tap(1500, 150); time.sleep(1); tap(1550, 850); time.sleep(5); swipe_cnt = 0

def detect_battle_turn():
    """偵測 Wave (優化 ROI 範圍)"""
    img = cv2.imread(IMG_PATH)
    if img is None: return None
    h, w = img.shape[:2]
    # 擴大 ROI 以相容不同尺寸模板
    roi = img[0:int(h*0.2), int(w*0.5):w] 
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    best_val, detected_turn = -1, None
    for t in [1, 2, 3]:
        tmpl = cv2.imread(os.path.join(BATTLE_DIR, f"battle_{t}_black.png"), 0)
        if tmpl is None or thresh.shape[0] < tmpl.shape[0]: continue
        res = cv2.matchTemplate(thresh, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > 0.65 and max_val > best_val:
            best_val, detected_turn = max_val, t
    return detected_turn

def run_battle():
    print("⚔️ [2/3] 戰鬥開始")
    last_turn = 0
    while True:
        capture_screen()
        turn = detect_battle_turn()
        if turn:
            if turn != last_turn:
                print(f"🎯 Wave {turn}"); last_turn = turn
            screen = cv2.imread(IMG_PATH)
            att = find_img(screen, ASSETS["attack"], threshold=0.75)
            if att:
                for (serv, skill) in TURN_SCRIPT.get(turn, []):
                    tap(*SKILL_POS[serv][skill-1]); tap(*CONFIRM_BTN); time.sleep(2.5)
                tap(*att); time.sleep(2); capture_screen()
                img = cv2.imread(IMG_PATH); h, w = img.shape[:2]
                top, bottom = int(h * 0.48), int(h * 0.82)
                ratios = [(0.13, 0.228), (0.3, 0.408), (0.45, 0.57), (0.61, 0.72), (0.77, 0.885)]
                order = []
                for i, (r1, r2) in enumerate(ratios):
                    card = img[top:bottom, int(w*r1):int(w*r2)]
                    # 顏色辨識邏輯
                    hsv = cv2.cvtColor(card, cv2.COLOR_BGR2HSV)
                    red = cv2.inRange(hsv, np.array([0, 80, 50]), np.array([10, 255, 255]))
                    blue = cv2.inRange(hsv, np.array([90, 80, 50]), np.array([130, 255, 255]))
                    order.append((1 if np.sum(red > 0) >= np.sum(blue > 0) else 2, i+1))
                order.sort(key=lambda x: x[0])
                chosen = 0
                if NP_SCRIPT.get(turn): tap(*NP_POS[NP_SCRIPT[turn]]); chosen += 1
                for _, idx in order[:(3-chosen)]: tap(*CARD_CENTERS[idx-1])
                if turn == 3: break
                time.sleep(15)
        time.sleep(2)

def run_finish():
    """修正後的結算處理：包含 AP 恢復與即時重新截圖"""
    print("💰 [3/3] 結算處理與體力監控中...")
    while True:
        capture_screen()
        screen = cv2.imread(IMG_PATH)
        if find_img(screen, ASSETS["bond"]) or find_img(screen, ASSETS["exp"]):
            tap(1200, 540)
        elif find_img(screen, ASSETS["next"]):
            tap(2100, 1000)
        elif find_img(screen, ASSETS["cont"]):
            print("🔄 點擊『連續出擊』")
            tap(1500, 800)
            time.sleep(3) # 等待動畫
            
            # 🔥 關鍵修正：必須重新截圖，否則會讀到舊畫面
            capture_screen()
            check_screen = cv2.imread(IMG_PATH)
            
            if find_img(check_screen, ASSETS["ap_window"]):
                print("🍎 偵測到體力不足！執行吃果實流程")
                tap(1200, 500); time.sleep(1); tap(1500, 800)
                print("✅ AP 已恢復")
                time.sleep(2)
            else:
                print("✅ 體力充足，進入下一場")
            return 
        time.sleep(1.5)

# ====================================================
# 4. 互動式配對與主程序入口
# ====================================================

def main():
    global DEVICE_IP
    local_ip = "127.0.0.1"
    
    print("\n" + "═"*40 + "\n 📱 FGO 永動機 (手機整合版) \n" + "═"*40)
    
    # 互動式連線/配對
    is_pair = input("\n❓ 是否需要重新配對？(y/n): ").lower().strip()
    if is_pair == 'y':
        pair_port = input("👉 請輸入『配對埠號』: ").strip()
        pair_code = input("👉 請輸入『6 位數配對碼』: ").strip()
        print(f"🔄 正在配對 {local_ip}:{pair_port}...")
        subprocess.run(["adb", "pair", f"{local_ip}:{pair_port}", pair_code])

    print("-" * 30)
    c_port = input("👉 請輸入『連線埠號』: ").strip()
    DEVICE_IP = f"{local_ip}:{c_port}"
    
    print(f"🔄 正在連線至 {DEVICE_IP}...")
    subprocess.run(["adb", "connect", DEVICE_IP])

    # 驗證連線狀態
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if DEVICE_IP in result.stdout:
        print(f"✅ 連線成功！")
    else:
        print("❌ 連線失敗，請檢查埠號。")
        return

    # 確保資料夾存在
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(BATTLE_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    count = 1
    while True:
        print(f"\n===== 🚀 第 {count} 場循環 =====")
        if run_support():
            time.sleep(10); run_battle(); time.sleep(5); run_finish()
            count += 1
        time.sleep(5)

if __name__ == "__main__":
    main()