# action.py
import subprocess
import time

# 指定你要操作的裝置 ID
DEVICE_ID = "10.191.176.213:41335" 

def tap(x, y, delay=0.15):
    """執行指定裝置的點擊操作 """
    # 關鍵：加上 -s {DEVICE_ID}
    subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "tap", str(x), str(y)])
    time.sleep(delay)

def swipe(x1, y1, x2, y2, dur=150, delay=0.2):
    """執行指定裝置的滑動操作 """
    subprocess.run([
        "adb", "-s", DEVICE_ID, "shell", "input", "swipe",
        str(x1), str(y1), str(x2), str(y2), str(dur)
    ])
    time.sleep(delay)