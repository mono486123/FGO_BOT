import cv2
import os

# 配置路徑
IMG_PATH = r"D:\fgo_bot\logs\screen.png"
OUT_DIR = r"D:\fgo_bot\logs\temp_cards"
DEBUG_PATH = r"D:\fgo_bot\logs\debug_view.png"

def auto_crop_cards():
    img = cv2.imread(IMG_PATH)
    if img is None:
        print("❌ 無法讀取 screen.png")
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    # 清空舊卡片
    for f in os.listdir(OUT_DIR):
        if f.endswith(".png"):
            os.remove(os.path.join(OUT_DIR, f))
    
    h, w = img.shape[:2]
    debug_img = img.copy() # 用於畫框預覽

    # ====================================================
    # 🎯 精確座標參數 (針對 2400x1080 優化)
    # ====================================================
    # 垂直範圍：避開上方的技能圖示與下方的職階字樣
    top = int(h * 0.48)
    bottom = int(h * 0.82)

    # 五張卡片的橫向起點比例 (每張寬度約 18%)
    # 這裡微調了間距，確保每張卡都在正中央
    card_ratios = [
        (0.13, 0.228), # Card 1
        (0.3, 0.408), # Card 2
        (0.45, 0.57), # Card 3
        (0.61, 0.72), # Card 4
        (0.7705, 0.885)  # Card 5
    ]

    print(f"📸 正在裁切卡片 (解析度: {w}x{h})...")

    for i, (r1, r2) in enumerate(card_ratios):
        x1 = int(w * r1)
        x2 = int(w * r2)
        
        # 裁切
        card = img[top:bottom, x1:x2]
        
        # 儲存
        save_path = os.path.join(OUT_DIR, f"card{i+1}.png")
        cv2.imwrite(save_path, card)
        
        # 在 Debug 圖上畫框 (紅框)
        cv2.rectangle(debug_img, (x1, top), (x2, bottom), (0, 0, 255), 3)
        print(f"✔ [Card {i+1}] 輸出成功")

    # 儲存預覽圖供手動確認
    cv2.imwrite(DEBUG_PATH, debug_img)
    print(f"\n💡 請檢查 {DEBUG_PATH} 確認紅框範圍是否正確！")

if __name__ == "__main__":
    auto_crop_cards()