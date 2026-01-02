#classify_cards.py
#templates資料夾的card1..N進行顏色分類，步驟3


import cv2
import numpy as np
import glob
import os


def classify_card(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    blue_lower = np.array([90, 80, 50])
    blue_upper = np.array([130, 255, 255])

    red_lower1 = np.array([0, 80, 50])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 80, 50])
    red_upper2 = np.array([180, 255, 255])

    green_lower = np.array([40, 80, 50])
    green_upper = np.array([80, 255, 255])

    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
    red_mask = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)

    blue_count = np.sum(blue_mask > 0)
    red_count = np.sum(red_mask > 0)
    green_count = np.sum(green_mask > 0)

    if blue_count >= red_count and blue_count >= green_count:
        return "blue"
    elif red_count >= blue_count and red_count >= green_count:
        return "red"
    else:
        return "green"


def main():

    # 🔥 你的模板資料夾（真正路徑）
    template_dir = r"D:\fgo_bot\logs\temp_cards"

    # 只讀取原始 card1.png ~ card5.png
    png_list = sorted(glob.glob(os.path.join(template_dir, "card*.png")))

    if not png_list:
        print("❌ 讀不到任何 card*.png，請確認路徑是否正確")
        print("目前搜尋路徑：", os.path.join(template_dir, "card*.png"))
        return

    for file in png_list:
        img = cv2.imread(file)
        if img is None:
            print("❌ 讀圖失敗：", file)
            continue

        ctype = classify_card(img)
        print(f"{file} → {ctype}")

        base = os.path.basename(file)
        new_name = f"{ctype}_{base}"
        out_path = os.path.join(template_dir, new_name)

        cv2.imwrite(out_path, img)

    print("🎉 完成分類輸出！")


if __name__ == "__main__":
    main()
