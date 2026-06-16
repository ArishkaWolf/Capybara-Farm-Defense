import pygame

from .building import Building
from .capybara import Capybara
from .constants import BUILDING_DEFS, CAPYBARA_DEFS, COLORS, GRID_H, GRID_W, MAP_W, TILE, TOP_BAR
from .resource_manager import ResourceManager
from .utils import grid_to_world, in_grid, pay, world_to_grid
from .wave_manager import WaveManager


class Farm:
    def __init__(self, particles):
        self.particles = particles
        self.resource_manager = ResourceManager()
        self.wave_manager = WaveManager()
        self.buildings = {}
        self.capybaras = []
        self.enemies = []
        self.base_cell = (GRID_W // 2, GRID_H // 2)
        self.base_position = grid_to_world(self.base_cell)
        self.selected_building = "grass_farm"
        self.selected_capybara = "defender"
        self.message = ""
        self.message_time = 0
        self.place_building("house", self.base_cell, free=True)

    def update(self, dt):
        self.message_time = max(0, self.message_time - dt)
        self.resource_manager.update(dt, self)
        self.wave_manager.update(dt, self)
        for building in list(self.buildings.values()):
            building.update(dt, self, self.enemies, self.particles)
            if not building.alive and building.kind != "house":
                del self.buildings[building.cell]
        for capy in list(self.capybaras):
            capy.update(dt, self, self.enemies, self.particles)
        for enemy in list(self.enemies):
            enemy.update(dt, self, self.particles)
            if not enemy.alive:
                self.resource_manager.resources["coins"] += enemy.coins
                self.particles.burst(enemy.pos, COLORS["coin"], 6)
        self.capybaras = [c for c in self.capybaras if c.alive]
        self.enemies = [e for e in self.enemies if e.alive]

    @property
    def base(self):
        return self.buildings.get(self.base_cell)

    def count_buildings(self, kind):
        return sum(1 for b in self.buildings.values() if b.kind == kind)

    def set_message(self, text):
        self.message = text
        self.message_time = 2.2

    def place_building(self, kind, cell, free=False):
        if not in_grid(cell):
            return False
        if cell in self.buildings:
            if not free:
                self.set_message("Клетка занята")
            return False
        if self.wave_manager.phase != "prepare" and not free:
            self.set_message("Строить можно между волнами")
            return False
        cost = BUILDING_DEFS[kind]["cost"]
        if free or pay(self.resource_manager.resources, cost):
            self.buildings[cell] = Building(kind, cell)
            self.particles.burst(grid_to_world(cell), BUILDING_DEFS[kind]["color"], 10)
            return True
        self.set_message("Не хватает ресурсов")
        return False

    def place_capybara(self, kind, cell):
        if not in_grid(cell):
            return False
        if self.wave_manager.phase != "prepare":
            self.set_message("Капибары выходят в фазе подготовки")
            return False
        if cell in self.buildings and self.buildings[cell].kind != "house":
            self.set_message("Клетка занята постройкой")
            return False
        if sum(1 for c in self.capybaras if c.cell == cell) >= 2:
            self.set_message("На клетке тесно")
            return False
        if pay(self.resource_manager.resources, CAPYBARA_DEFS[kind]["cost"]):
            capy = Capybara(kind, cell)
            self.capybaras.append(capy)
            self.particles.burst(capy.pos, COLORS["capy"], 9)
            return True
        self.set_message("Не хватает ресурсов")
        return False

    def upgrade_cell(self, cell):
        building = self.buildings.get(cell)
        if not building:
            return False
        if building.kind == "house" or pay(self.resource_manager.resources, building.upgrade_cost()):
            if building.kind == "house":
                cost = {"wood": 35 * building.level, "coins": 22 * building.level}
                if not pay(self.resource_manager.resources, cost):
                    self.set_message("Не хватает ресурсов")
                    return False
            building.upgrade()
            self.particles.burst(grid_to_world(cell), COLORS["coin"], 14)
            return True
        self.set_message("Не хватает ресурсов")
        return False

    def handle_map_click(self, pos, mode):
        if self.resource_manager.collect_at(pos, self.particles):
            return
        if pos[0] >= MAP_W or pos[1] < TOP_BAR:
            return
        cell = world_to_grid(pos)
        if mode == "building":
            self.place_building(self.selected_building, cell)
        elif mode == "capybara":
            self.place_capybara(self.selected_capybara, cell)

    def draw(self, surface, font):
        surface.fill(COLORS["bg"])
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = pygame.Rect(x * TILE, TOP_BAR + y * TILE, TILE, TILE)
                color = (153, 203, 125) if (x + y) % 2 == 0 else (145, 195, 119)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, COLORS["grid"], rect, 1)
        for drop in self.resource_manager.drops:
            drop.draw(surface, font)
        for building in self.buildings.values():
            building.draw(surface, font)
        for capy in self.capybaras:
            capy.draw(surface, font)
        for enemy in self.enemies:
            enemy.draw(surface, font)
        if self.message_time > 0:
            label = font.render(self.message, True, COLORS["white"])
            box = label.get_rect(center=(MAP_W // 2, TOP_BAR + 22))
            pygame.draw.rect(surface, (64, 76, 58), box.inflate(28, 14), border_radius=8)
            surface.blit(label, box)

    def to_json(self):
        return {
            "resources": self.resource_manager.to_json(),
            "wave": self.wave_manager.to_json(),
            "buildings": [
                {"kind": b.kind, "cell": b.cell, "level": b.level, "hp": b.hp}
                for b in self.buildings.values()
            ],
            "capybaras": [
                {"kind": c.kind, "cell": c.cell, "hp": c.hp}
                for c in self.capybaras
            ],
        }

    def from_json(self, data):
        self.resource_manager.from_json(data.get("resources", {}))
        self.wave_manager.from_json(data.get("wave", {}))
        self.buildings = {}
        for item in data.get("buildings", []):
            building = Building(item["kind"], tuple(item["cell"]))
            while building.level < item.get("level", 1):
                building.upgrade()
            building.hp = min(item.get("hp", building.max_hp), building.max_hp)
            self.buildings[building.cell] = building
        if self.base_cell not in self.buildings:
            self.place_building("house", self.base_cell, free=True)
        self.capybaras = []
        for item in data.get("capybaras", []):
            capy = Capybara(item["kind"], tuple(item["cell"]))
            capy.hp = min(item.get("hp", capy.max_hp), capy.max_hp)
            self.capybaras.append(capy)
        self.enemies = []
