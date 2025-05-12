import numpy as np
from env.actions import ActionChain, get_box_center

# 🛡️ Macro 1: Ungarrison All from Town Center
def ungarrison_town_center(detections):
    town_centers = [d for d in detections if d["class"] == "TownCenter"]
    if not town_centers:
        print("❌ No Town Center detected.")
        return

    tc = np.random.choice(town_centers)
    tc_x, tc_y = get_box_center(tc["box"])

    chain = ActionChain()
    chain.add_move_click(tc_x, tc_y) # Click Town Center   
    chain.add_keypress('f') # Press F to ungarrison
    chain.execute()

# 🏠 Macro 2: Build House
def build_house(detections, target_x, target_y):
    villagers = [d for d in detections if d["class"] == "Villager"]
    if not villagers:
        print("❌ No Villager detected.")
        return

    villager = np.random.choice(villagers)
    v_x, v_y = get_box_center(villager["box"])

    chain = ActionChain()
    chain.add_move_click(v_x, v_y) # Click Villager
    chain.add_keypress('q') # Open Build Menu
    chain.add_keypress('q') # Select House
    chain.add_move_click(target_x, target_y) # Place Building
    chain.execute()

# 🌾 Macro 3: Build Mill
def build_mill(detections, target_x, target_y):
    villagers = [d for d in detections if d["class"] == "Villager"]
    if not villagers:
        print("❌ No Villager detected.")
        return

    villager = np.random.choice(villagers)
    v_x, v_y = get_box_center(villager["box"])

    chain = ActionChain()
    chain.add_move_click(v_x, v_y) # Select Villager
    chain.add_keypress('q') # Open Build Menu
    chain.add_keypress('w') # Select Mill
    chain.add_move_click(target_x, target_y) # Place Building
    chain.execute()

# 👷 Macro 4: Queue New Villager from Town Center
def queue_villager(detections):
    town_centers = [d for d in detections if d["class"] == "TownCenter"]
    if not town_centers:
        print("❌ No Town Center detected.")
        return

    tc = np.random.choice(town_centers)
    tc_x, tc_y = get_box_center(tc["box"])

    chain = ActionChain()
    chain.add_move_click(tc_x, tc_y) # Select Town Center
    chain.add_keypress('q') # Queue new villager
    chain.execute()
