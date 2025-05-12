import cv2
import pyautogui
import numpy as np

def main():
    print("🖱️ Select the ROI for your target region (e.g. resources or villager counts).")
    print("🔒 Press ENTER or SPACE when done, ESC to cancel.")

    # Take full screenshot (or you could capture the game window here instead)
    screenshot = pyautogui.screenshot()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Select ROI
    roi = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=True)

    # Clean up
    cv2.destroyWindow("Select ROI")

    if roi:
        x, y, w, h = roi
        print(f"\n📏 Selected ROI: (x={x}, y={y}, width={w}, height={h})")
        print(f"👉 Use this in your code as: ({x}, {y}, {w}, {h})")

if __name__ == "__main__":
    main()