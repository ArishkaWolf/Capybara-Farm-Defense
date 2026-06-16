import pygame

from .constants import BUILDING_DEFS, COLORS, TILE
from .utils import draw_health, grid_to_world


class Building:
    def __init__(self, kind, cell):
        data = BUILDING_DEFS[kind]
        self.kind = kind
        self.cell = tuple(cell)
        self.level = 1
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.color = data["color"]
        self.cooldown = 0

    @property
    def rect(self):
        center = grid_to_world(self.cell)
        return pygame.Rect(center.x - TILE / 2 + 4, center.y - TILE / 2 + 4, TILE - 8, TILE - 8)

    @property
    def alive(self):
        return self.hp > 0

    def upgrade_cost(self):
        return {"wood": 18 * self.level, "coins": 12 * self.level}

    def upgrade(self):
        self.level += 1
        self.max_hp += 55
        self.hp = self.max_hp

    def update(self, dt, farm, enemies, particles):
        self.cooldown = max(0, self.cooldown - dt)
        if self.kind == "healing_pond" and self.cooldown <= 0:
            center = grid_to_world(self.cell)
            for capy in farm.capybaras:
                if capy.hp < capy.max_hp and center.distance_to(capy.pos) < TILE * (2.2 + self.level * 0.25):
                    capy.hp = min(capy.max_hp, capy.hp + 10 + self.level * 4)
                    particles.burst(capy.pos, COLORS["water"], 4)
                    self.cooldown = 1.1
                    break
        if self.kind == "wood_tower" and self.cooldown <= 0:
            center = grid_to_world(self.cell)
            target = None
            best = 9999
            for enemy in enemies:
                dist = center.distance_to(enemy.pos)
                if dist < TILE * (3.2 + self.level * 0.35) and dist < best:
                    target = enemy
                    best = dist
            if target:
                target.take_damage(18 + self.level * 7)
                particles.attack(center, target.pos, (247, 215, 112))
                self.cooldown = 0.85

    def draw(self, surface, font):
        rect = self.rect
        if self.kind == "house":
            pygame.draw.rect(surface, (142, 89, 54), rect.inflate(-4, -3), border_radius=5)
            roof = [(rect.left + 2, rect.top + 18), (rect.centerx, rect.top - 7), (rect.right - 2, rect.top + 18)]
            pygame.draw.polygon(surface, (112, 65, 48), roof)
            pygame.draw.rect(surface, (238, 202, 123), (rect.centerx - 7, rect.centery + 2, 14, 20), border_radius=3)
        elif self.kind == "grass_farm":
            pygame.draw.rect(surface, (112, 86, 48), rect, border_radius=4)
            for x in range(rect.left + 7, rect.right - 3, 10):
                pygame.draw.line(surface, (83, 196, 75), (x, rect.bottom - 6), (x + 5, rect.top + 8), 3)
        elif self.kind == "berry_bush":
            pygame.draw.circle(surface, (65, 143, 76), rect.center, 18)
            for ox, oy in [(-8, -6), (7, -8), (2, 7), (-3, 0)]:
                pygame.draw.circle(surface, COLORS["berry"], (rect.centerx + ox, rect.centery + oy), 4)
        elif self.kind == "wood_tower":
            pygame.draw.rect(surface, (126, 78, 39), rect.inflate(-10, -4), border_radius=3)
            pygame.draw.rect(surface, (86, 56, 36), (rect.left + 6, rect.top + 4, rect.width - 12, 10), border_radius=3)
            pygame.draw.circle(surface, (245, 218, 126), rect.center, 7)
        elif self.kind == "fence":
            for x in [rect.left + 7, rect.centerx, rect.right - 7]:
                pygame.draw.rect(surface, (113, 74, 42), (x - 4, rect.top + 4, 8, rect.height - 8), border_radius=2)
            pygame.draw.line(surface, (145, 91, 50), (rect.left + 4, rect.centery - 7), (rect.right - 4, rect.centery - 7), 6)
            pygame.draw.line(surface, (145, 91, 50), (rect.left + 4, rect.centery + 8), (rect.right - 4, rect.centery + 8), 6)
        elif self.kind == "healing_pond":
            pygame.draw.ellipse(surface, COLORS["water"], rect.inflate(-5, -10))
            pygame.draw.ellipse(surface, (180, 229, 218), rect.inflate(-16, -24), 2)
        draw_health(surface, rect, self.hp, self.max_hp)
        if self.level > 1:
            label = font.render(str(self.level), True, COLORS["white"])
            surface.blit(label, (rect.right - 11, rect.bottom - 15))
