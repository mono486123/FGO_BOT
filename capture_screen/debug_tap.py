import subprocess
import os

# 基礎連線設定
DEVICE_IP = "10.191.176.213:40523" 

# 原始座標資料庫
CARD_CENTERS = [(500, 750), (900, 750), (1200, 750), (1500, 750), (1900, 750)]
SKILL_POS = {
    1: [(300, 850), (400, 850), (500, 850)],
    2: [(800, 850), (900, 850), (1000, 850)],
    3: [(1300, 850), (1400, 850), (1500, 850)]
}
NP_POS = { 1: (860, 350), 2: (1200, 350), 3: (1600, 350) }
CONFIRM_BTN = (1500, 650)
FAST_FORWARD_POS = (1200, 600)

def adb_tap(x, y):
    """執行單次 ADB 點擊"""
    cmd = ["adb", "-s", DEVICE_IP, "shell", "input", "tap", str(x), str(y)]
    subprocess.run(cmd)
    print(f"-> 💥 Clicked: ({x}, {y})")

def show_help():
    print("\n[ 快速指令表 ]")
    print("技能: s11, s12, s13 (從者1技能1-3) ... s31, s32, s33")
    print("指令卡: c1, c2, c3, c4, c5")
    print("寶具: n1, n2, n3")
    print("功能: ok (確認鍵), ff (加速鍵)")
    print("自訂: 直接輸入 x y (例如: 1000 500)")
    print("退出: exit")

def main():
    os.system(f"adb connect {DEVICE_IP}") #
    print(f"🎯 進入快速微調模式 (裝置: {DEVICE_IP})")
    show_help()
    
    while True:
        cmd = input("\n請輸入指令: ").lower().strip()
        
        if cmd == 'exit': break
        
        try:
            # 1. 測試技能 (s11 ~ s33)
            if cmd.startswith('s') and len(cmd) == 3:
                serv = int(cmd[1])
                sk = int(cmd[2])
                adb_tap(*SKILL_POS[serv][sk-1])
            
            # 2. 測試指令卡 (c1 ~ c5)
            elif cmd.startswith('c') and len(cmd) == 2:
                idx = int(cmd[1])
                adb_tap(*CARD_CENTERS[idx-1])
            
            # 3. 測試寶具 (n1 ~ n3)
            elif cmd.startswith('n') and len(cmd) == 2:
                idx = int(cmd[1])
                adb_tap(*NP_POS[idx])
            
            # 4. 測試功能鍵
            elif cmd == 'ok': adb_tap(*CONFIRM_BTN)
            elif cmd == 'ff': adb_tap(*FAST_FORWARD_POS)
            
            # 5. 直接輸入座標 (X Y)
            elif ' ' in cmd:
                x, y = map(int, cmd.split())
                adb_tap(x, y)
                
            else:
                print("❌ 指令格式錯誤！")
                show_help()
        except Exception as e:
            print(f"⚠️ 發生錯誤: {e}")

if __name__ == "__main__":
    main()