import gym
import numpy as np
import time
import cv2

from env.vision import capture_game_window, extract_game_info
from env import actions
from env import macro_actions

SCREEN_W, SCREEN_H = 2560, 1440
NO_PROGRESS_THRESHOLD = 30  # Steps with no meaningful resource growth

cv2.namedWindow("AOE4 RL Agent", cv2.WINDOW_NORMAL)

class AOEEnv(gym.Env):
    def __init__(self):
        # 🔥 Updated Action Space:
        # First value: Action type (macro or primitive)
        # Others: x1, y1, x2, y2 (used when needed)
        self.action_space = gym.spaces.MultiDiscrete([14, SCREEN_W, SCREEN_H, SCREEN_W, SCREEN_H])
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(720, 1280, 3), dtype=np.uint8)

        self.last_food = 0
        self.last_wood = 0
        self.last_gold = 0
        self.last_stone = 0
        self.last_idle = 0
        self.last_population = 0
        self.no_progress_steps = 0
        self.total_reward = 0
        self.latest_full_frame = None
        self.last_visible_units = 0

    def reset(self):
        frame, _ = capture_game_window()
        info = extract_game_info(frame=frame)

        self.latest_full_frame = frame
        self.last_food = info.get("resources", {}).get("food", 0)
        self.last_wood = info.get("resources", {}).get("wood", 0)
        self.last_gold = info.get("resources", {}).get("gold", 0)
        self.last_stone = info.get("resources", {}).get("stone", 0)
        self.last_idle = info.get("resources", {}).get("idle_villagers", 0)
        self.last_population = info.get("resources", {}).get("current_population", 0)
        self.no_progress_steps = 0
        self.total_reward = 0

        print("\n🔄 Resetting environment")
        return cv2.resize(frame, (1280, 720))

    def step(self, action):
        self._execute_action(action)
        time.sleep(0.5)

        frame, _ = capture_game_window()
        info = extract_game_info(frame=frame)
        self.latest_full_frame = frame
        resized = cv2.resize(frame, (1280, 720))

        reward = self._calculate_reward(info)
        done = self.no_progress_steps >= NO_PROGRESS_THRESHOLD

        self._render_action(action, reward, self.no_progress_steps)

        if done:
            print(f"⚠️ No meaningful progress for {NO_PROGRESS_THRESHOLD} steps. Ending episode. Total reward: {self.total_reward}")

        return resized, reward, done, {}

    def _calculate_reward(self, info):
        # Extract resource values from the info dictionary
        food = info.get("resources", {}).get("food", 0)
        wood = info.get("resources", {}).get("wood", 0)
        gold = info.get("resources", {}).get("gold", 0)
        stone = info.get("resources", {}).get("stone", 0)
        idle = info.get("resources", {}).get("idle_villagers", 0)
        population = info.get("resources", {}).get("current_population", 0)
        detections = info.get("detections", [])
        visible_units = len([d for d in detections if d["class"] in ["Villager", "Scout", "TownCenter", "Sheep"]])

        # Reward based on resource changes
        reward = 0
        reward += (food - self.last_food) * 1.0
        reward += (wood - self.last_wood) * 0.8
        reward += (gold - self.last_gold) * 0.8
        reward += (stone - self.last_stone) * 0.8
        reward += (population - self.last_population) * 2.0
        reward += (self.last_idle - idle) * 0.5
        reward += (visible_units - self.last_visible_units) * 0.2

        # 🌑 Penalty for having no units visible
        if visible_units == 0:
            reward -= 5.0  # Big penalty for being lost in fog

        # Update last counts
        self.last_food = food
        self.last_wood = wood
        self.last_gold = gold
        self.last_stone = stone
        self.last_idle = idle
        self.last_population = population
        self.last_visible_units = visible_units

        # Check for meaningful progress
        if reward <= 0:
            self.no_progress_steps += 1
        else:
            self.no_progress_steps = 0

        self.total_reward += reward
        return reward

    def _execute_action(self, action):
        action_type, x1, y1, x2, y2 = map(int, action)

        frame, _ = capture_game_window()
        info = extract_game_info(frame=frame)
        detections = info.get("detections", [])

        # 📜 Macro actions (first 4)
        if action_type == 0:
            macro_actions.ungarrison_town_center(detections)
        elif action_type == 1:
            macro_actions.build_house(detections, target_x=x1, target_y=y1)
        elif action_type == 2:
            macro_actions.build_mill(detections, target_x=x1, target_y=y1)
        elif action_type == 3:
            macro_actions.queue_villager(detections)

        # 🎯 Primitive actions (the rest)
        else:
            match action_type:
                case 4: actions.left_click(x1, y1)
                case 5: actions.double_click(x1, y1)
                case 6: actions.right_click(x1, y1)
                case 7: actions.drag_from_to((x1, y1), (x2, y2))
                case 8: actions.pan_by_mouse_edge("up")
                case 9: actions.pan_by_mouse_edge("down")
                case 10: actions.pan_by_mouse_edge("left")
                case 11: actions.pan_by_mouse_edge("right")
                case 12: actions.rotate_camera("left")
                case 13: actions.rotate_camera("right")
                case _: print("❓ Unknown action")

    def _render_action(self, action, reward, no_progress):
        if self.latest_full_frame is None:
            return

        img = self.latest_full_frame.copy()
        cv2.putText(img, f"Action: {action}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, f"Reward: {reward:.2f}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if no_progress:
            cv2.putText(img, "⚠️ No progress!", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        display = cv2.resize(img, (960, 540))
        cv2.moveWindow("AOE4 RL Agent", -1500, 500)
        cv2.imshow("AOE4 RL Agent", display)
        cv2.waitKey(1)
