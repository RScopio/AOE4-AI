import pyautogui
import keyboard
import datetime
import os
import csv

# Folders
FULL_IMG_DIR = "./data/screenshots"
MINIMAP_DIR = "./data/minimap"
LOG_FILE = "./data/screenshot_log.csv"

os.makedirs(FULL_IMG_DIR, exist_ok=True)
os.makedirs(MINIMAP_DIR, exist_ok=True)

# Game UI constants (you can tune these)
MINIMAP_OFFSET = (1974, 810, 585, 606) 

AUTO_CAPTURE_INTERVAL = 3.0 # Set to >0 for automatic screenshots every X seconds

print("🎯 Screenshot Tool Active")
print("🕹️  Press [SPACE] to capture")
print("⏱️  Auto-capture:", "OFF" if AUTO_CAPTURE_INTERVAL == 0 else f"every {AUTO_CAPTURE_INTERVAL}s")

def save_screenshot():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"aoe4_{timestamp}"

    # Fullscreen
    img = pyautogui.screenshot()
    full_path = os.path.join(FULL_IMG_DIR, f"{base_filename}.png")
    img.save(full_path)

    # Minimap crop
    x, y, w, h = MINIMAP_OFFSET
    minimap = img.crop((x, y, x + w, y + h))
    minimap_path = os.path.join(MINIMAP_DIR, f"{base_filename}_minimap.png")
    minimap.save(minimap_path)

    # Log
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, full_path, minimap_path])

    print(f"✅ Screenshot saved: {base_filename}")

# Optional: time-based auto-capture
last_capture = datetime.datetime.now()

try:
    while True:
        now = datetime.datetime.now()

        if keyboard.is_pressed("space"):
            save_screenshot()
            while keyboard.is_pressed("space"):
                pass  # avoid rapid spam

        elif AUTO_CAPTURE_INTERVAL > 0 and (now - last_capture).total_seconds() > AUTO_CAPTURE_INTERVAL:
            save_screenshot()
            last_capture = now

except KeyboardInterrupt:
    print("\n💀 Interrupted. Exiting.")
