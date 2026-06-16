import math
import random

import pygame

from .constants import GRID_H, GRID_W, MAP_W, TILE, TOP_BAR


def clamp(value, low, high):
    return max(low, min(high, value))


def grid_to_world(cell):
    gx, gy = cell
    return pygame.Vector2(gx * TILE + TILE / 2, TOP_BAR + gy * TILE + TILE / 2)


def world_to_grid(pos):
    x, y = pos
    return int(x // TILE), int((y - TOP_BAR) // TILE)


def in_grid(cell):
    x, y = cell
    return 0 <= x < GRID_W and 0 <= y < GRID_H


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def draw_text(surface, font, text, pos, color, center=False):
    img = font.render(str(text), True, color)
    rect = img.get_rect()
    rect.center = pos if center else rect.center
    if not center:
        rect.topleft = pos
    surface.blit(img, rect)
    return rect


def draw_health(surface, rect, hp, max_hp):
    if max_hp <= 0:
        return
    pct = clamp(hp / max_hp, 0, 1)
    bar = pygame.Rect(rect.left, rect.top - 8, rect.width, 5)
    pygame.draw.rect(surface, (75, 49, 45), bar, border_radius=2)
    fill = bar.copy()
    fill.width = max(1, int(bar.width * pct))
    color = (74, 192, 92) if pct > 0.45 else (225, 156, 58) if pct > 0.2 else (210, 74, 67)
    pygame.draw.rect(surface, color, fill, border_radius=2)


def random_edge_spawn():
    side = random.choice(["left", "right", "top", "bottom"])
    if side == "left":
        return pygame.Vector2(-24, TOP_BAR + random.randrange(GRID_H) * TILE + TILE / 2)
    if side == "right":
        return pygame.Vector2(MAP_W + 24, TOP_BAR + random.randrange(GRID_H) * TILE + TILE / 2)
    if side == "top":
        return pygame.Vector2(random.randrange(GRID_W) * TILE + TILE / 2, TOP_BAR - 24)
    return pygame.Vector2(random.randrange(GRID_W) * TILE + TILE / 2, TOP_BAR + GRID_H * TILE + 24)


def can_afford(resources, cost):
    return all(resources.get(k, 0) >= v for k, v in cost.items())


def pay(resources, cost):
    if not can_afford(resources, cost):
        return False
    for key, value in cost.items():
        resources[key] -= value
    return True
