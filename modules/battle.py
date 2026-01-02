import cv2
import os

# 路徑設定
BATTLE_DIR = r"D:\fgo_bot\capture_screen\battle"

def preprocess_battle_templates():
    for i in range(1, 4):
        file_path = os.path.join(BATTLE_DIR, f"battle_{i}.png")
        img = cv2.imread(file_path)
        
        if img is None:
            print(f"❌ 找不到 {file_path}")
            continue
            
        # 1. 轉灰階
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. 二值化：將高亮度的白色數字留下，其餘變黑
        # 門檻值設定在 180~200 左右，視數字亮度調整
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        
        # 儲存覆蓋原本的圖，或是另存新檔測試
        out_path = os.path.join(BATTLE_DIR, f"battle_{i}_black.png")
        cv2.imwrite(out_path, thresh)
        print(f"✅ 已轉換: {out_path}")

if __name__ == "__main__":
    preprocess_battle_templates()