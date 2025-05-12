import cv2
import numpy as np
import pyautogui
from ultralytics import YOLO
import pytesseract
import pygetwindow as gw

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

YOLO_MODEL_PATH = "data/models/best.pt"
WINDOW_NAME = "AOE4 Game View"

POPULATION_REGION = (48, 1139, 103, 39)
IDLE_VILLAGER_REGION = (186, 1132, 56, 45)

FOOD_COUNT_REGION = (51, 1210, 104, 48)
FOOD_VILLAGER_REGION = (186, 1210, 62, 44)

WOOD_COUNT_REGION = (51, 1265, 101, 43)
WOOD_VILLAGER_REGION = (189, 1261, 63, 43)

GOLD_COUNT_REGION = (52, 1319, 105, 39)
GOLD_VILLAGER_REGION = (187, 1317, 62, 38)

STONE_COUNT_REGION = (50, 1370, 104, 38)
STONE_VILLAGER_REGION = (186, 1367, 63, 39)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 960, 540)
cv2.moveWindow(WINDOW_NAME, -1500, 500)

try:
    yolo_model = YOLO(YOLO_MODEL_PATH)
except Exception as e:
    print(f"[Vision] Could not load YOLO model: {e}")
    yolo_model = None

def capture_game_window(title_keyword="Age of Empires IV "):
    windows = gw.getWindowsWithTitle(title_keyword)
    if not windows:
        print("[Vision] Game window not found.")
        return None, None
    win = windows[0]
    if win.isMinimized:
        win.restore()
    region = (win.left, win.top, win.width, win.height)
    screenshot = pyautogui.screenshot(region=region)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return frame, region

def detect_objects_with_yolo(frame, target_classes=None, conf_threshold=0.25):
    if yolo_model is None:
        return []
    results = yolo_model.predict(source=frame, conf=conf_threshold, verbose=False)[0]
    detections = []
    for box in results.boxes:
        cls_id = int(box.cls)
        class_name = yolo_model.names[cls_id]
        conf = float(box.conf)
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        if (target_classes is None) or (class_name in target_classes):
            detections.append({"class": class_name, "box": [x1, y1, x2, y2], "conf": conf})
    return detections

def extract_ocr_number(frame, region, label_name="", expect_fraction=False):
    x, y, w, h = region
    crop = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, config='--psm 7 -c tessedit_char_whitelist=0123456789/')

    if label_name:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 1)
        cv2.putText(frame, label_name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    if expect_fraction:
        if '/' in text:
            parts = text.strip().split('/')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return int(parts[0]), int(parts[1])
        # 🛡️ Fallback if parsing fails
        return 0, 0
    else:
        digits = ''.join(filter(str.isdigit, text))
        return int(digits) if digits else 0



def extract_game_info(frame=None, show_window=False):
    if frame is None:
        frame, _ = capture_game_window()
        if frame is None:
            print("[Vision] No frame captured.")
            return {}

    detections = detect_objects_with_yolo(frame)
    current_pop, max_pop = extract_ocr_number(frame, POPULATION_REGION, "Population", expect_fraction=True)
    idle_count = extract_ocr_number(frame, IDLE_VILLAGER_REGION, "Idle")
    food_count = extract_ocr_number(frame, FOOD_COUNT_REGION, "Food Count")
    food_villagers = extract_ocr_number(frame, FOOD_VILLAGER_REGION, "Food Villagers")
    wood_count = extract_ocr_number(frame, WOOD_COUNT_REGION, "Wood Count")
    wood_villagers = extract_ocr_number(frame, WOOD_VILLAGER_REGION, "Wood Villagers")
    gold_count = extract_ocr_number(frame, GOLD_COUNT_REGION, "Gold Count")
    gold_villagers = extract_ocr_number(frame, GOLD_VILLAGER_REGION, "Gold Villagers")
    stone_count = extract_ocr_number(frame, STONE_COUNT_REGION, "Stone Count")
    stone_villagers = extract_ocr_number(frame, STONE_VILLAGER_REGION, "Stone Villagers")

    if show_window and frame is not None:
        annotated = frame.copy()
        for obj in detections:
            x1, y1, x2, y2 = obj["box"]
            label = f"{obj['class']} {obj['conf']:.2f}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imshow(WINDOW_NAME, annotated)
        cv2.waitKey(1)

    return {
        "detections": detections,
        "resources": {
            "current_population": current_pop,
            "max_population": max_pop,
            "idle_villagers": idle_count,
            "food": food_count,
            "food_villagers": food_villagers,
            "wood": wood_count,
            "wood_villagers": wood_villagers,
            "gold": gold_count,
            "gold_villagers": gold_villagers,
            "stone": stone_count,
            "stone_villagers": stone_villagers,
        }
    }

