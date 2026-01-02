import subprocess

def capture_screen(path=r"D:\fgo_bot\logs\screen.png", device_id=None):
    """
    擷取手機螢幕。
    :param path: 儲存圖片的路徑
    :param device_id: 指定的 ADB 裝置 IP (例如 10.191.176.213:40523)
    """
    try:
        # 建立 ADB 指令
        # 如果有提供 device_id，就加上 -s 參數來指定特定的裝置
        cmd = ["adb"]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["exec-out", "screencap", "-p"])
        
        # 執行指令並取得圖片數據
        png = subprocess.check_output(cmd)
        
        with open(path, "wb") as f:
            f.write(png)
        return True
    except Exception as e:
        print(f"❌ 截圖出錯: {e}")
        return False

# ⚠️ 注意：原本這裡的 capture_screen(...) 呼叫已經刪除！
# 這樣 import 時才不會立刻執行截圖，而是等主程式連線後才由主程式呼叫。