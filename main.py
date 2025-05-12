import time
import cv2
from env.vision import extract_game_info, capture_game_window
from env.game_state import GameState

state = GameState()
target_fps = 30
frame_interval = 1 / target_fps

try:
    while True:
        start = time.time()

        frame, region = capture_game_window()
        if frame is None:
            print("🛑 Could not capture game window.")
            time.sleep(1)
            continue

        info = extract_game_info(frame=frame, show_window=True)
        state.update(info)
        print(state)

        elapsed = time.time() - start
        wait = max(0, frame_interval - elapsed)
        time.sleep(wait)

except KeyboardInterrupt:
    print("\n👋 Exiting.")
    cv2.destroyAllWindows()