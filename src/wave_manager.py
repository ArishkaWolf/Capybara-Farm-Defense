import random

from .constants import ENEMY_DEFS
from .enemy import Enemy
from .utils import random_edge_spawn


class WaveManager:
    def __init__(self):
        self.wave = 0
        self.phase = "prepare"
        self.prepare_time = 25
        self.timer = self.prepare_time
        self.spawn_queue = []
        self.spawn_timer = 0
        self.enemies_alive = 0
        self.victory_wave = 15

    def start_wave(self):
        if self.phase == "wave":
            return
        self.wave += 1
        self.phase = "wave"
        self.timer = 0
        self.spawn_queue = self._make_wave()
        self.spawn_timer = 0

    def update(self, dt, farm):
        if self.phase == "prepare":
            self.timer -= dt
            if self.timer <= 0:
                self.start_wave()
            return
        self.spawn_timer -= dt
        if self.spawn_queue and self.spawn_timer <= 0:
            kind = self.spawn_queue.pop(0)
            farm.enemies.append(Enemy(kind, random_edge_spawn(), self.wave))
            self.spawn_timer = max(0.28, 1.0 - self.wave * 0.035)
        if not self.spawn_queue and not farm.enemies:
            self.phase = "prepare"
            self.timer = max(10, self.prepare_time - self.wave)
            farm.resource_manager.add_reward(self.wave)

    def _make_wave(self):
        count = 5 + self.wave * 3
        queue = []
        types = ["normal"]
        if self.wave >= 2:
            types.append("fast")
        if self.wave >= 3:
            types.append("raider")
        if self.wave >= 4:
            types.append("heavy")
        for _ in range(count):
            queue.append(random.choice(types))
        if self.wave % 5 == 0:
            queue.append("boss")
        random.shuffle(queue)
        return queue

    def is_victory(self):
        return self.wave >= self.victory_wave and self.phase == "prepare"

    def to_json(self):
        return {"wave": self.wave, "phase": "prepare", "timer": max(8, self.timer)}

    def from_json(self, data):
        self.wave = data.get("wave", 0)
        self.phase = "prepare"
        self.timer = data.get("timer", self.prepare_time)
