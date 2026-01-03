import cv2
import numpy as np
import subprocess
import time
import os

# ====================================================
# 1. 環境配置
# ====================================================
DEVICE_IP = ""
TEMP_DIR = r"D:\fgo_bot\assets\results"
SCREEN_PATH = os.path.join(TEMP_DIR, "screen_end.png")

# 模板路徑 (請根據下方說明準備這些圖片)
T_BOND = os.path.join(TEMP_DIR, "bond_title.png")      # 與從者的羈絆
T_EXP = os.path.join(TEMP_DIR, "exp_title.png")        # 獲得EXP
T_NEXT = os.path.join(TEMP_DIR, "next_btn.png")        # 下一步按鈕
T_CONT_YES = os.path.join(TEMP_DIR, "cont_yes.png")    # 連續出擊的「是」
T_AP_WINDOW = os.path.join(TEMP_DIR, "ap_window.png")  # 恢復AP視窗特徵

def adb_call(cmd):
    """執行 ADB 指令"""
    subprocess.run(f"adb -s {DEVICE_IP} {cmd}", shell=True)

def find_template(template_path, threshold=0.85):
    """截圖並尋找模板座標"""
    adb_call(f"exec-out screencap -p > {SCREEN_PATH}")
    screen = cv2.imread(SCREEN_PATH)
    temp = cv2.imread(template_path)
    if screen is None or temp is None: return None
    
    res = cv2.matchTemplate(screen, temp, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    
    if max_val >= threshold:
        h, w = temp.shape[:2]
        return (max_loc[0] + w // 2, max_loc[1] + h // 2)
    return None

# ====================================================
# 2. 結尾處理主邏輯
# ====================================================

def run_battle_end_process():
    print("🤖 結尾自動化偵測啟動... 正在監控畫面")

    # --- 步驟 1: 羈絆畫面 ---
    print("⏳ 等待『與從者的羈絆』標題...")
    while not find_template(T_BOND):
        time.sleep(1.5)
    print("✅ 發現羈絆畫面，點擊跳過")
    adb_call("shell input tap 1200 540") # 點擊螢幕中心
    time.sleep(2)

    # --- 步驟 2: EXP 畫面 ---
    print("⏳ 等待『獲得EXP』標題...")
    while not find_template(T_EXP):
        time.sleep(1)
    print("✅ 發現經驗值畫面，點擊跳過")
    adb_call("shell input tap 1200 540")
    time.sleep(2)

    # --- 步驟 3: 下一步 (掉落物) ---
    print("⏳ 等待『下一步』按鈕...")
    while not find_template(T_NEXT):
        time.sleep(1)
    print("✅ 點擊『下一步』")
    adb_call("shell input tap 2100 1000")
    time.sleep(3) # 等待切換到連續出擊視窗

    # --- 步驟 4: 連續出擊與 AP 恢復 ---
    print("⏳ 偵測『連續出擊』按鈕...")
    while True:
        if find_template(T_CONT_YES):
            print("🚀 點擊『連續出擊：是』")
            adb_call("shell input tap 1500 800")
            time.sleep(2) # 暫停以檢查是否彈出 AP 視窗

            # 檢查是否跳出 AP 恢復視窗
            if find_template(T_AP_WINDOW):
                print("🍎 偵測到體力不足！執行吃果實流程")
                adb_call("shell input tap 1200 500")  # 點擊黃金果實位置
                time.sleep(1)
                adb_call("shell input tap 1500 800") # 點擊『確定』
                print("✅ AP 已恢復")
            else:
                print("✅ 體力充足，直接進入下一場選人")
            
            print("🏁 結尾流程處理完畢！")
            break
        time.sleep(1)

if __name__ == "__main__":
    run_battle_end_process()