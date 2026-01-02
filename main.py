import time
import sys
import os
import config # 引入剛剛建立的設定檔

# 確保可以引用 modules 資料夾內的檔案
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# 引入你的三個核心模組 (假設這些檔案都放在 modules 資料夾下，或與 main.py 同層)
# 如果你的檔案都在 D:\fgo_bot\ 下，直接 import 即可
try:
    import modules.support_selector
    import modules.battle_manager
    import modules.battle_end_handler
except ImportError as e:
    print("❌ 找不到模組，請確認 support_selector.py, battle_manager.py 等檔案是否在同一目錄或 modules 資料夾內。")
    print(f"錯誤訊息: {e}")
    sys.exit(1)

def update_modules_ip():
    """強制將 config.py 的 IP 更新到各個模組中"""
    modules.support_selector.DEVICE_ID = config.DEVICE_IP
    modules.battle_manager.DEVICE_IP = config.DEVICE_IP
    modules.battle_end_handler.DEVICE_ID = config.DEVICE_IP

def main():
    print(f"🤖 FGO 永動機啟動！目標裝置: {config.DEVICE_IP}")
    
    # 強制更新所有模組的 IP，避免你忘記去改各個檔案
    update_modules_ip()

    quest_count = 1
    
    while True:
        print(f"\n==========================================")
        print(f"       🔄 第 {quest_count} 場戰鬥循環開始")
        print(f"==========================================")

        # -------------------------------------------
        # 階段 1: 選取支援 (Support Selection)
        # -------------------------------------------
        print("\n[Step 1] 正在搜尋好友支援...")
        if modules.support_selector.run_select_support():
            print("✅ 支援選取成功，等待進入戰鬥 (Loading)...")
            # 這裡給 15-20 秒等待轉場 (視手機速度調整)
            time.sleep(15) 
            
            # -------------------------------------------
            # 階段 2: 執行戰鬥 (3-Turn Battle)
            # -------------------------------------------
            print("\n[Step 2] 戰鬥開始！轉交給 Battle Manager...")
            # 呼叫 battle_manager 的 main 函式來跑那一整套 detect -> attack -> win 的流程
            # 注意：這裡會執行直到 Wave 3 結束並 break
            modules.battle_manager.main() 
            
            # -------------------------------------------
            # 階段 3: 結算處理 (End Handler)
            # -------------------------------------------
            print("\n[Step 3] 戰鬥結束，進入結算流程...")
            # 這裡會處理 羈絆 -> EXP -> 掉落 -> 連續出擊 -> (吃果實)
            modules.battle_end_handler.run_battle_end_process()
            
            print(f"🎉 第 {quest_count} 場完整結束！稍作休息...")
            quest_count += 1
            time.sleep(2) 

        else:
            print("⚠️ 選取支援失敗（或找不到目標），等待刷新後重試...")
            time.sleep(5)

if __name__ == "__main__":
    main()