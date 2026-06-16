WIDTH = 1048
HEIGHT = 648
FPS = 60

TILE = 48
GRID_W = 16
GRID_H = 12
MAP_W = GRID_W * TILE
TOP_BAR = 72
PANEL_W = WIDTH - MAP_W

SAVE_FILE = "savegame.json"

COLORS = {
    "bg": (169, 213, 142),
    "soil": (143, 105, 64),
    "grid": (118, 162, 96),
    "panel": (85, 124, 92),
    "panel_dark": (54, 86, 70),
    "cream": (250, 238, 203),
    "text": (48, 48, 42),
    "white": (255, 255, 255),
    "danger": (202, 75, 65),
    "grass": (87, 178, 82),
    "berry": (166, 62, 114),
    "berries": (166, 62, 114),
    "wood": (124, 82, 45),
    "coin": (229, 184, 67),
    "water": (78, 162, 194),
    "capy": (164, 112, 69),
    "capy_dark": (111, 71, 43),
}

RESOURCE_START = {"grass": 95, "berries": 55, "wood": 70, "coins": 35}

BUILDING_DEFS = {
    "house": {
        "name": "Домик",
        "cost": {},
        "hp": 520,
        "color": (185, 134, 79),
        "desc": "сердце фермы",
    },
    "grass_farm": {
        "name": "Ферма травы",
        "cost": {"wood": 20, "coins": 8},
        "hp": 160,
        "color": (93, 190, 86),
        "desc": "+трава",
    },
    "berry_bush": {
        "name": "Ягодник",
        "cost": {"grass": 22, "wood": 12},
        "hp": 130,
        "color": (154, 74, 128),
        "desc": "+ягоды",
    },
    "wood_tower": {
        "name": "Башня",
        "cost": {"wood": 45, "coins": 20},
        "hp": 210,
        "color": (141, 93, 50),
        "desc": "стреляет",
    },
    "fence": {
        "name": "Забор",
        "cost": {"wood": 18},
        "hp": 250,
        "color": (119, 77, 43),
        "desc": "блокирует",
    },
    "healing_pond": {
        "name": "Пруд",
        "cost": {"berries": 25, "coins": 18},
        "hp": 180,
        "color": (80, 166, 197),
        "desc": "лечит",
    },
}

CAPYBARA_DEFS = {
    "defender": {
        "name": "Защитник",
        "cost": {"grass": 28, "berries": 8},
        "hp": 115,
        "range": 1.2,
        "speed": 54,
        "damage": 13,
        "role": "melee",
        "color": (164, 112, 69),
    },
    "archer": {
        "name": "Лучник",
        "cost": {"grass": 32, "wood": 18},
        "hp": 75,
        "range": 4.3,
        "speed": 48,
        "damage": 15,
        "role": "ranged",
        "color": (190, 132, 73),
    },
    "builder": {
        "name": "Строитель",
        "cost": {"grass": 26, "wood": 22},
        "hp": 80,
        "range": 2.8,
        "speed": 52,
        "damage": 6,
        "role": "support",
        "color": (173, 125, 78),
    },
    "healer": {
        "name": "Лекарь",
        "cost": {"berries": 38, "coins": 12},
        "hp": 72,
        "range": 3.1,
        "speed": 50,
        "damage": 0,
        "role": "healer",
        "color": (203, 151, 112),
    },
    "tank": {
        "name": "Танк",
        "cost": {"grass": 48, "wood": 30, "coins": 10},
        "hp": 235,
        "range": 1.0,
        "speed": 34,
        "damage": 10,
        "role": "blocker",
        "color": (130, 92, 62),
    },
}

ENEMY_DEFS = {
    "normal": {"hp": 54, "speed": 44, "damage": 8, "coins": 3, "color": (116, 79, 117)},
    "fast": {"hp": 36, "speed": 74, "damage": 6, "coins": 4, "color": (88, 102, 168)},
    "heavy": {"hp": 120, "speed": 29, "damage": 13, "coins": 7, "color": (88, 73, 93)},
    "raider": {"hp": 72, "speed": 48, "damage": 15, "coins": 6, "color": (177, 84, 66)},
    "boss": {"hp": 430, "speed": 26, "damage": 22, "coins": 40, "color": (96, 40, 78)},
}
