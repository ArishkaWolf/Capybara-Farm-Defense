import math

import pygame

from .constants import CAPYBARA_DEFS, COLORS, TILE
from .utils import draw_health, grid_to_world


class Capybara:
    def __init__(self, kind, cell):
        data = CAPYBARA_DEFS[kind]
        self.kind = kind
        self.role = data["role"]
        self.cell = tuple(cell)
        self.home = grid_to_world(cell)
        self.pos = pygame.Vector2(self.home)
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.range = data["range"] * TILE
        self.speed = data["speed"]
        self.damage = data["damage"]
        self.color = data["color"]
        self.attack_cd = 0
        self.step = 0

    @property
    def alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        self.hp -= amount

    def update(self, dt, farm, enemies, particles):
        self.attack_cd = max(0, self.attack_cd - dt)
        self.step += dt * (4 if self.speed > 40 else 2.5)
        if self.kind == "healer":
            self._heal_ally(dt, farm, particles)
            self._return_home(dt)
            return

        target = self._find_enemy(enemies)
        if target and self.attack_cd <= 0:
            target.take_damage(self.damage)
            particles.attack(self.pos, target.pos, (255, 235, 153) if self.kind == "archer" else (235, 185, 109))
            self.attack_cd = 0.75 if self.kind == "archer" else 0.58
        elif target and self.kind in ("defender", "tank") and self.pos.distance_to(target.pos) > TILE * 0.55:
            self._move_towards(target.pos, dt)
        else:
            self._return_home(dt)

    def _find_enemy(self, enemies):
        best = None
        best_dist = 99999
        for enemy in enemies:
            dist = self.pos.distance_to(enemy.pos)
            if dist <= self.range and dist < best_dist:
                best = enemy
                best_dist = dist
        return best

    def _heal_ally(self, dt, farm, particles):
        if self.attack_cd > 0:
            return
        wounded = [c for c in farm.capybaras if c is not self and c.hp < c.max_hp and self.pos.distance_to(c.pos) <= self.range]
        if wounded:
            target = min(wounded, key=lambda c: c.hp / c.max_hp)
            target.hp = min(target.max_hp, target.hp + 14)
            particles.attack(self.pos, target.pos, (143, 225, 180))
            self.attack_cd = 0.9

    def _return_home(self, dt):
        if self.pos.distance_to(self.home) > 3:
            self._move_towards(self.home, dt)

    def _move_towards(self, target, dt):
        direction = pygame.Vector2(target) - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt

    def draw(self, surface, font):
        bob = math.sin(self.step) * 2
        rect = pygame.Rect(self.pos.x - 17, self.pos.y - 11 + bob, 34, 22)
        pygame.draw.ellipse(surface, self.color, rect)
        pygame.draw.circle(surface, self.color, (int(self.pos.x + 15), int(self.pos.y - 5 + bob)), 10)
        pygame.draw.circle(surface, COLORS["capy_dark"], (int(self.pos.x + 19), int(self.pos.y - 7 + bob)), 2)
        pygame.draw.circle(surface, COLORS["capy_dark"], (int(self.pos.x + 22), int(self.pos.y - 2 + bob)), 2)
        for ox in (-9, 8):
            pygame.draw.ellipse(surface, COLORS["capy_dark"], (self.pos.x + ox - 3, self.pos.y + 8 + bob, 7, 6))
        if self.kind == "archer":
            pygame.draw.arc(surface, (88, 55, 37), (self.pos.x - 21, self.pos.y - 21 + bob, 24, 34), -1.2, 1.1, 3)
        elif self.kind == "builder":
            pygame.draw.rect(surface, (228, 190, 72), (self.pos.x - 9, self.pos.y - 20 + bob, 18, 6), border_radius=2)
        elif self.kind == "healer":
            pygame.draw.circle(surface, (157, 223, 177), (int(self.pos.x - 4), int(self.pos.y - 17 + bob)), 5)
        elif self.kind == "tank":
            pygame.draw.rect(surface, (101, 76, 60), (self.pos.x - 19, self.pos.y - 7 + bob, 9, 18), border_radius=2)
        elif self.kind == "defender":
            pygame.draw.line(surface, (210, 205, 174), (self.pos.x - 16, self.pos.y - 14 + bob), (self.pos.x - 5, self.pos.y + 2 + bob), 3)
        draw_health(surface, rect, self.hp, self.max_hp)
