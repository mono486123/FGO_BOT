#測試是否可讀取回合數

import cv2
import pytesseract
import re

IMG_PATH = r"D:\fgo_bot\capture_screen\screen.png"

# 設定 Tesseract 路徑
pytesseract.pytesseract.tesseract_cmd = r"D:\fgo_bot\pytesseract\tesseract.exe"


def detect_battle_turn():
    img = cv2.imread(IMG_PATH)
    if img is None:
        print("❌ 無法讀取 screen.png")
        return None

    h, w = img.shape[:2]

    # 右上角 ROI（包含 battle x/3）
    x1 = int(w * 0.72)
    y1 = 0
    x2 = int(w*0.76)
    y2 = int(h * 0.06)

    roi = img[y1:y2, x1:x2]

    # OCR 讀取，只允許 123/ 這些字
    config = '--psm 7 -c tessedit_char_whitelist=123/'
    text = pytesseract.image_to_string(roi, config=config)

    text = text.replace(" ", "").strip()

    print("📖 OCR讀取文字：", repr(text))

    if "1/3" in text:
        return 1
    if "2/3" in text:
        return 2
    if "3/3" in text:
        return 3

    return None


def main():
    turn = detect_battle_turn()
    print("🔍 偵測結果 →", turn)


if __name__ == "__main__":
    main()



