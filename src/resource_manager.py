import random

import pygame

from .constants import COLORS, RESOURCE_START, TILE, TOP_BAR


class ResourceDrop:
    def __init__(self, kind, pos, amount):
        self.kind = kind
        self.pos = pygame.Vector2(pos)
        self.amount = amount
        self.radius = 13
        self.pulse = random.random() * 6

    @property
    def rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self, dt):
        self.pulse += dt * 4

    def draw(self, surface, font):
        color = COLORS.get(self.kind, COLORS["coin"])
        r = self.radius + int(2 * abs(__import__("math").sin(self.pulse)))
        pygame.draw.circle(surface, color, self.pos, r)
        pygame.draw.circle(surface, (255, 255, 255), self.pos, r, 2)


class ResourceManager:
    def __init__(self):
        self.resources = dict(RESOURCE_START)
        self.drops = []
        self.production_timer = 0
        self.drop_timer = 2.0
        self.production_bonus = 0

    def update(self, dt, farm):
        self.production_bonus = 0.2 if any(c.kind == "builder" and c.alive for c in farm.capybaras) else 0
        self.production_timer += dt
        self.drop_timer -= dt
        for drop in self.drops:
            drop.update(dt)
        if self.production_timer >= 1:
            self.production_timer -= 1
            bonus = 1 + self.production_bonus
            self.resources["grass"] += int((1 + farm.count_buildings("grass_farm") * 1.4) * bonus)
            self.resources["berries"] += int((farm.count_buildings("berry_bush") * 0.9) * bonus)
            self.resources["wood"] += int((0.7 + farm.count_buildings("wood_tower") * 0.15) * bonus)
            self.resources["coins"] += 1 if farm.wave_manager.phase == "prepare" else 0
        if self.drop_timer <= 0:
            self.drop_timer = random.uniform(4.0, 7.5)
            kind = random.choice(["grass", "berries", "wood", "coins"])
            x = random.randint(1, 14) * TILE + TILE / 2
            y = TOP_BAR + random.randint(1, 10) * TILE + TILE / 2
            self.drops.append(ResourceDrop(kind, (x, y), random.randint(3, 8)))

    def collect_at(self, pos, particles):
        for drop in list(self.drops):
            if drop.rect.collidepoint(pos):
                self.resources[drop.kind] += drop.amount
                particles.resource_collect(drop.pos, drop.kind)
                self.drops.remove(drop)
                return True
        return False

    def add_reward(self, wave):
        self.resources["coins"] += 18 + wave * 5
        self.resources["berries"] += 10 + wave * 2
        self.resources["grass"] += 18 + wave * 4

    def to_json(self):
        return {"resources": self.resources}

    def from_json(self, data):
        self.resources.update(data.get("resources", {}))
