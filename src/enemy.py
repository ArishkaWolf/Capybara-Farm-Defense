import math

import pygame

from .constants import COLORS, ENEMY_DEFS, TILE, TOP_BAR
from .utils import draw_health, in_grid, world_to_grid


class Enemy:
    def __init__(self, kind, pos, wave):
        data = ENEMY_DEFS[kind]
        scale = 1 + wave * 0.13
        self.kind = kind
        self.pos = pygame.Vector2(pos)
        self.max_hp = int(data["hp"] * scale)
        self.hp = self.max_hp
        self.speed = data["speed"] * (1 + min(wave, 20) * 0.015)
        self.damage = data["damage"] * (1 + wave * 0.07)
        self.coins = data["coins"]
        self.color = data["color"]
        self.attack_cd = 0
        self.step = 0
        self.radius = 16 if kind != "boss" else 25

    @property
    def alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        self.hp -= amount

    def update(self, dt, farm, particles):
        self.attack_cd = max(0, self.attack_cd - dt)
        self.step += dt * 7
        target = self._attack_target(farm)
        if target:
            if self.attack_cd <= 0:
                target.hp -= self.damage
                particles.burst(self.pos, COLORS["danger"], 3)
                self.attack_cd = 0.9 if self.kind != "fast" else 0.55
            return
        self._move_to_base(dt, farm)

    def _attack_target(self, farm):
        candidates = []
        for capy in farm.capybaras:
            if self.pos.distance_to(capy.pos) < self.radius + 20:
                candidates.append(capy)
        for building in farm.buildings.values():
            if building.alive and self.pos.distance_to(pygame.Vector2(building.rect.center)) < self.radius + 23:
                candidates.append(building)
        if not candidates:
            return None
        if self.kind == "raider":
            buildings = [c for c in candidates if hasattr(c, "kind") and c.__class__.__name__ == "Building"]
            if buildings:
                return min(buildings, key=lambda b: b.hp)
        return min(candidates, key=lambda item: item.hp)

    def _move_to_base(self, dt, farm):
        base = pygame.Vector2(farm.base_position)
        direction = base - self.pos
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()
        desired = self.pos + direction * self.speed * dt
        if not self._blocked(desired, farm):
            self.pos = desired
            return

        # Simple obstacle avoidance: try horizontal, vertical, then side slips.
        options = [
            pygame.Vector2(direction.x, 0),
            pygame.Vector2(0, direction.y),
            pygame.Vector2(-direction.y, direction.x),
            pygame.Vector2(direction.y, -direction.x),
        ]
        for option in options:
            if option.length_squared() == 0:
                continue
            pos = self.pos + option.normalize() * self.speed * dt
            if not self._blocked(pos, farm):
                self.pos = pos
                return

    def _blocked(self, pos, farm):
        cell = world_to_grid(pos)
        if not in_grid(cell):
            return False
        building = farm.buildings.get(cell)
        return bool(building and building.kind in ("fence", "wood_tower", "berry_bush", "grass_farm") and building.alive)

    def draw(self, surface, font):
        bob = math.sin(self.step) * 2
        body = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius * 0.7 + bob, self.radius * 2, self.radius * 1.4)
        pygame.draw.ellipse(surface, self.color, body)
        pygame.draw.circle(surface, (45, 32, 45), (int(self.pos.x + self.radius * 0.35), int(self.pos.y - 3 + bob)), 3)
        pygame.draw.circle(surface, (45, 32, 45), (int(self.pos.x + self.radius * 0.65), int(self.pos.y - 2 + bob)), 3)
        if self.kind == "fast":
            pygame.draw.line(surface, (210, 220, 255), (self.pos.x - 18, self.pos.y + 13), (self.pos.x - 31, self.pos.y + 18), 3)
        elif self.kind == "heavy":
            pygame.draw.rect(surface, (65, 58, 65), body.inflate(-8, -6), 2, border_radius=6)
        elif self.kind == "raider":
            pygame.draw.rect(surface, (220, 154, 88), (self.pos.x - 7, self.pos.y - 22 + bob, 14, 8), border_radius=2)
        elif self.kind == "boss":
            pygame.draw.polygon(surface, (233, 197, 70), [(self.pos.x - 15, self.pos.y - 25), (self.pos.x, self.pos.y - 38), (self.pos.x + 15, self.pos.y - 25)])
        draw_health(surface, body, self.hp, self.max_hp)
