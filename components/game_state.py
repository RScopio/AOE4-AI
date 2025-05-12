from dataclasses import dataclass, field
from typing import Dict, List
import time

@dataclass
class GameState:
    timestamp: float = field(default_factory=time.time)
    resources: Dict[str, int] = field(default_factory=dict)
    objects: List[Dict[str, object]] = field(default_factory=list)

    def update(self, info: Dict):
        self.timestamp = time.time()
        self.resources = info.get("resources", {})
        self.objects = info.get("detections", [])

    def get_objects_by_class(self, class_name: str) -> List[Dict[str, object]]:
        return [obj for obj in self.objects if obj["class"] == class_name]

    def __str__(self):
        #detected_classes = [obj["class"] for obj in self.objects]
        return (
            f"[{time.strftime('%H:%M:%S', time.localtime(self.timestamp))}] "
            f"Population: {self.resources.get('current_population', '?')}/{self.resources.get('max_population', '?')} "
            f"| idle_villagers: {self.resources.get('idle_villagers', '?')} "
            f"| food: {self.resources.get('food', '?')} " 
            f"| food_villagers: {self.resources.get('food_villagers', '?')} "
            f"| wood: {self.resources.get('wood', '?')} "
            f"| wood_villagers: {self.resources.get('wood_villagers', '?')} "
            f"| gold: {self.resources.get('gold', '?')} "
            f"| gold_villagers: {self.resources.get('gold_villagers', '?')} "
            f"| stone: {self.resources.get('stone', '?')} "
            f"| stone_villagers: {self.resources.get('stone_villagers', '?')} "
            #f"| Detected: {detected_classes}"
        )