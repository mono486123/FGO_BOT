import cv2
import numpy as np
import os
import glob

class CardProcessor:
    def __init__(self, screen_path, output_dir, debug_path):
        self.screen_path = screen_path
        self.output_dir = output_dir
        self.debug_path = debug_path
        # 建立輸出資料夾
        os.makedirs(self.output_dir, exist_ok=True)

    def crop_cards(self):
        """步驟 1: 裁切卡片 (針對 2400x1080 優化)"""
        img = cv2.imread(self.screen_path)
        if img is None:
            print("❌ CardProcessor: 無法讀取截圖")
            return False

        # 清空舊資料
        for f in os.listdir(self.output_dir):
            if f.endswith(".png"): os.remove(os.path.join(self.output_dir, f))

        h, w = img.shape[:2]
        debug_img = img.copy()

        # 精確比例
        top, bottom = int(h * 0.48), int(h * 0.82)
        card_ratios = [
            (0.13, 0.228), (0.3, 0.408), (0.45, 0.57), 
            (0.61, 0.72), (0.7705, 0.885)
        ]

        for i, (r1, r2) in enumerate(card_ratios):
            x1, x2 = int(w * r1), int(w * r2)
            card = img[top:bottom, x1:x2]
            cv2.imwrite(os.path.join(self.output_dir, f"card{i+1}.png"), card)
            cv2.rectangle(debug_img, (x1, top), (x2, bottom), (0, 0, 255), 3)

        cv2.imwrite(self.debug_path, debug_img)
        print(f"✔ 卡片裁切完成，Debug 圖已存至 {self.debug_path}")
        return True

    def _get_color(self, img):
        """色彩辨識核心核心邏輯"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 定義 HSV 範圍
        masks = {
            "blue": cv2.inRange(hsv, np.array([90, 80, 50]), np.array([130, 255, 255])),
            "red": cv2.inRange(hsv, np.array([0, 80, 50]), np.array([10, 255, 255])) | 
                   cv2.inRange(hsv, np.array([160, 80, 50]), np.array([180, 255, 255])),
            "green": cv2.inRange(hsv, np.array([40, 80, 50]), np.array([80, 255, 255]))
        }
        
        counts = {color: np.sum(mask > 0) for color, mask in masks.items()}
        # 回傳數量最多的顏色
        return max(counts, key=counts.get)

    def classify_and_rename(self):
        """步驟 2: 辨識顏色並重新命名"""
        png_list = sorted(glob.glob(os.path.join(self.output_dir, "card[1-5].png")))
        results = []

        for file in png_list:
            img = cv2.imread(file)
            if img is None: continue

            color = self._get_color(img)
            results.append(color)
            
            # 重新命名以便手動檢查 (例如 blue_card1.png)
            new_path = os.path.join(self.output_dir, f"{color}_{os.path.basename(file)}")
            cv2.imwrite(new_path, img)
            print(f"📄 {os.path.basename(file)} -> {color}")
            
        return results

# --- 測試代碼 ---
if __name__ == "__main__":
    # 使用你原本的路徑
    processor = CardProcessor(
        screen_path=r"D:\fgo_bot\logs\screen.png",
        output_dir=r"D:\fgo_bot\logs\temp_cards",
        debug_path=r"D:\fgo_bot\logs\debug_view_cards.png"
    )
    if processor.crop_cards():
        colors = processor.classify_and_rename()
        print(f"🎉 最終辨識結果序列: {colors}")