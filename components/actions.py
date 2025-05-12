import pyautogui
import time

# ========================
# 🧠 Utility functions
# ========================

def get_box_center(box):
    x1, y1, x2, y2 = box
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))

def move_and_click(x, y, clicks=1, interval=0.2, button='left'):
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click(clicks=clicks, interval=interval, button=button)
    print(f"🖱️ {button.capitalize()} click ({clicks}x) at ({x}, {y})")

# ========================
# 🎯 Micro Actions
# ========================

def left_click(x, y):
    move_and_click(x, y)

def double_click(x, y):
    move_and_click(x, y, clicks=2)

def right_click(x, y):
    move_and_click(x, y, button='right')

def drag_from_to(start, end, duration=0.5, screen_w=2560, screen_h=1440, margin=50):
    # Clamp start and end points inside safe screen margins
    sx, sy = start
    ex, ey = end

    sx = max(margin, min(screen_w - margin, sx))
    sy = max(margin, min(screen_h - margin, sy))
    ex = max(margin, min(screen_w - margin, ex))
    ey = max(margin, min(screen_h - margin, ey))

    pyautogui.moveTo(sx, sy)
    pyautogui.dragTo(ex, ey, duration=duration, button='left')
    print(f"📦 Safe Drag from ({sx}, {sy}) to ({ex}, {ey})")

def pan(direction, duration=0.01):
    keys = {"up": "up", "down": "down", "left": "left", "right": "right"}
    key = keys.get(direction)
    if key:
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        print(f"🕹️ Panned {direction}")

def pan_by_mouse_edge(direction, screen_width=2560, screen_height=1440, duration=0.01):
    edges = {
        "left": (1, screen_height // 2),
        "right": (screen_width - 1, screen_height // 2),
        "up": (screen_width // 2, 1),
        "down": (screen_width // 2, screen_height - 1),
    }
    if direction in edges:
        x, y = edges[direction]
        pyautogui.moveTo(x, y, duration=0.1)
        time.sleep(duration)
        print(f"🕹️ Panned to {direction} edge")
    pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=0.1)

def rotate_camera(direction, drag_distance=27):
    x, y = pyautogui.position()
    pyautogui.keyDown('altleft')
    time.sleep(0.05)
    if direction == "left":
        pyautogui.moveTo(x + drag_distance, y, duration=0.3)
    elif direction == "right":
        pyautogui.moveTo(x - drag_distance, y, duration=0.3)
    pyautogui.keyUp('altleft')
    print(f"🌀 Rotated camera {direction}")

# ========================
# 🔗 ActionChain
# ========================
class ActionChain:
    def __init__(self):
        self.steps = []

    def add_move_click(self, x, y, clicks=1, interval=0.2, button='left'):
        self.steps.append(('move_click', (x, y, clicks, interval, button)))

    def add_keypress(self, key):
        self.steps.append(('keypress', key))

    def add_sleep(self, seconds):
        self.steps.append(('sleep', seconds))

    def execute(self):
        for action, params in self.steps:
            match action:
                case 'move_click':
                    x, y, clicks, interval, button = params
                    move_and_click(x, y, clicks, interval, button)
                case 'keypress':
                    pyautogui.press(params)
                    print(f"⌨️ Pressed key: {params}")
                case 'sleep':
                    time.sleep(params)
                    print(f"⏳ Slept {params}s")
