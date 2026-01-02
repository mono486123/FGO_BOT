import cv2
import numpy as np
import subprocess
import time

# ====================================================
# 1. 核心配置
# ====================================================
DEVICE_IP = "10.191.176.213:41335"
PLAYER_TEMP = r"D:\fgo_bot\assets\support\player_name.png"
SERVANT_TEMP = r"D:\fgo_bot\assets\support\servant_name.png"
SCREEN_PATH = r"D:\fgo_bot\logs\screen.png"

def adb_call(cmd_str):
    """鎖定裝置 ID，解決 more than one device 問題"""
    subprocess.run(f"adb -s {DEVICE_IP} {cmd_str}", shell=True)

def find_template(screen_img, template_path, threshold=0.8):
    """尋找單一模板，回傳座標與匹配度"""
    template = cv2.imread(template_path)
    if template is None: return None
    
    h, w = template.shape[:2]
    res = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        # 回傳中心點座標 (x, y)
        return (max_loc[0] + w // 2, max_loc[1] + h // 2)
    return None

# ====================================================
# 2. 核心搜尋邏輯
# ====================================================

def run_select_support():
    swipe_count = 0
    while True:
        print(f"📸 [第 {swipe_count+1} 輪] 同步比對玩家與從者中...")
        
        # 截圖
        adb_call(f"exec-out screencap -p > {SCREEN_PATH}")
        screen = cv2.imread(SCREEN_PATH)
        if screen is None: continue

        # 找玩家與從者座標
        player_pos = find_template(screen, PLAYER_TEMP)
        servant_pos = find_template(screen, SERVANT_TEMP)

        if player_pos and servant_pos:
            # 判斷邏輯：兩者的 Y 座標差距是否在一個支援欄位內 (通常 200~300 像素)
            if abs(player_pos[1] - servant_pos[1]) < 250:
                print(f"✅ 雙重匹配成功！玩家位於 {player_pos}, 從者位於 {servant_pos}")
                # 點擊該欄位的中心 (以玩家位置為準稍微向右偏移)
                adb_call(f"shell input tap {player_pos[0]} {player_pos[1]}")
                time.sleep(2)
                # 點擊右下角「任務開始」
                adb_call("shell input tap 2200 1000")
                return True

        # 如果沒找到，執行下滑
        if swipe_count < 4:
            print("👋 未發現目標組合，執行下滑...")
            adb_call(f"shell input swipe 1200 800 1200 350 600")
            swipe_count += 1
            time.sleep(2)
        else:
            print("⚠️ 刷新好友列表...")
            adb_call("shell input tap 1500 150") # 列表更新座標
            time.sleep(1.5)
            adb_call("shell input tap 1550 850") # 確認「是」
            time.sleep(5)
            swipe_count = 0

if __name__ == "__main__":
    run_select_support()