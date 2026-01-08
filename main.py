import time
import sys
import os

# 🔥 統一管理區：只要改這裡就好
DEVICE_IP = "10.178.123.213:41361" 

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
        print(f"\n===== 第 {quest_count} 場循環 =====")
        # 執行流程 
        if su.run_select_support():
            time.sleep(15) 
            man.main() 
            han.run_battle_end_process()
            quest_count += 1
        else:
            time.sleep(10)

if __name__ == "__main__":
    main()