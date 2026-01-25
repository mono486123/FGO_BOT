import time
import sys
import os

# 🔥 統一管理區：只要改這裡就好
DEVICE_IP = "10.70.53.213:37929" 

# 確保路徑正確
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_PATH, 'modules'))

# 引入核心模組
try:
    import modules.support_selector as su
    import modules.battle_manager as man
    import modules.battle_end_handler as han
    # 如果 action.py 在 card_processor 內
except ImportError as e:
    print(f"❌ 找不到子模組: {e}")
    sys.exit(1)

def sync_all_ips():
    """強制將 main.py 的 IP 寫入所有模組變數中"""
    modules_to_update = [su, man, han]
    print(f"⚙️ 正在強制同步裝置 IP: {DEVICE_IP}")
    for mod in modules_to_update:
        if hasattr(mod, 'DEVICE_IP'):
            mod.DEVICE_IP = DEVICE_IP
            print(f"   ✅ {mod.__name__} 同步完成")

def main():
    sync_all_ips() # 啟動時先同步 
    
    print(f"\n🤖 FGO 永動機啟動！目標: {DEVICE_IP}")
    quest_count = 1
    
    while True:
         try:
             print(f"\n===== 第 {quest_count} 場循環 =====")
             # 執行流程 
             if su.run_select_support():
                 time.sleep(5) # 進入戰鬥前的載入時間
                 man.main()    # 戰鬥模組（我們剛才修正的部分）
                 han.run_battle_end_process() # 結尾模組
                 quest_count += 1
             else:
                 print("⏳ 找不到好友，等待 10 秒後重試...")
                 time.sleep(10)
         except Exception as e:
             print(f"⚠️ 本場循環發生錯誤: {e}")
             print("🔄 5 秒後嘗試重啟下一場...")
             time.sleep(5)
             # 這裡可以加入一個回到大廳的動作，確保下一場能順利開始

if __name__ == "__main__":
    main()