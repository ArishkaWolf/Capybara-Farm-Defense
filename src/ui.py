import pygame

from .constants import BUILDING_DEFS, CAPYBARA_DEFS, COLORS, HEIGHT, MAP_W, PANEL_W, TOP_BAR, WIDTH
from .utils import can_afford, draw_text


class Button:
    def __init__(self, rect, text, action, small=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.small = small
        self.enabled = True

    def draw(self, surface, font, selected=False):
        color = (244, 220, 150) if selected else (237, 205, 131)
        if not self.enabled:
            color = (150, 143, 119)
        pygame.draw.rect(surface, color, self.rect, border_radius=7)
        pygame.draw.rect(surface, (70, 73, 57), self.rect, 2, border_radius=7)
        draw_text(surface, font, self.text, self.rect.center, COLORS["text"], center=True)

    def hit(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class UI:
    def __init__(self):
        self.font = None
        self.big_font = None
        self.small_font = None
        self.mode = "building"
        self.buttons = []
        self._build_buttons()

    def set_fonts(self, font, big_font, small_font):
        self.font = font
        self.big_font = big_font
        self.small_font = small_font

    def _build_buttons(self):
        x = MAP_W + 16
        y = TOP_BAR + 18
        self.buttons = []
        self.buttons.append(Button((x, y, 116, 34), "Постройки", ("mode", "building"), True))
        self.buttons.append(Button((x + 126, y, 116, 34), "Капибары", ("mode", "capybara"), True))
        y += 48
        for key, data in BUILDING_DEFS.items():
            if key == "house":
                continue
            self.buttons.append(Button((x, y, 242, 36), data["name"], ("building", key)))
            y += 42
        y += 10
        for key, data in CAPYBARA_DEFS.items():
            self.buttons.append(Button((x, y, 242, 36), data["name"], ("capybara", key)))
            y += 42
        self.buttons.append(Button((x, HEIGHT - 92, 116, 34), "Волна", ("start_wave", None), True))
        self.buttons.append(Button((x + 126, HEIGHT - 92, 116, 34), "Сохр.", ("save", None), True))

    def draw_hud(self, surface, farm, save_manager):
        pygame.draw.rect(surface, (100, 151, 102), (0, 0, WIDTH, TOP_BAR))
        pygame.draw.rect(surface, COLORS["panel"], (MAP_W, 0, PANEL_W, HEIGHT))
        r = farm.resource_manager.resources
        parts = [
            ("трава", r["grass"], COLORS["grass"]),
            ("ягоды", r["berries"], COLORS["berry"]),
            ("дерево", r["wood"], COLORS["wood"]),
            ("монеты", r["coins"], COLORS["coin"]),
        ]
        x = 16
        for name, value, color in parts:
            pygame.draw.circle(surface, color, (x + 10, 22), 9)
            draw_text(surface, self.font, f"{name}: {value}", (x + 25, 12), COLORS["white"])
            x += 160
        base = farm.base
        hp = int(base.hp) if base else 0
        draw_text(surface, self.font, f"Волна {farm.wave_manager.wave} | Домик {hp}", (16, 43), COLORS["white"])
        phase = "подготовка" if farm.wave_manager.phase == "prepare" else "атака"
        draw_text(surface, self.font, f"{phase}  {max(0, int(farm.wave_manager.timer))}с", (315, 43), COLORS["white"])
        draw_text(surface, self.small_font, f"рекорд: {save_manager.data.get('best_wave', 0)}", (560, 46), COLORS["white"])
        self._draw_panel(surface, farm)

    def _draw_panel(self, surface, farm):
        draw_text(surface, self.big_font, "Capybara Farm", (MAP_W + 18, 17), COLORS["cream"])
        for button in self.buttons:
            action, value = button.action
            if action == "building":
                button.enabled = self.mode == "building" and can_afford(farm.resource_manager.resources, BUILDING_DEFS[value]["cost"])
            elif action == "capybara":
                button.enabled = self.mode == "capybara" and can_afford(farm.resource_manager.resources, CAPYBARA_DEFS[value]["cost"])
            elif action == "start_wave":
                button.enabled = farm.wave_manager.phase == "prepare"
            selected = (
                (action == "mode" and value == self.mode)
                or (action == "building" and value == farm.selected_building)
                or (action == "capybara" and value == farm.selected_capybara)
            )
            if action in ("building", "capybara") and (
                (action == "building" and self.mode != "building") or (action == "capybara" and self.mode != "capybara")
            ):
                continue
            button.draw(surface, self.small_font, selected)
            if action == "building" and self.mode == "building":
                cost = " ".join(f"{v}{k[0]}" for k, v in BUILDING_DEFS[value]["cost"].items())
                draw_text(surface, self.small_font, cost, (button.rect.right - 82, button.rect.top + 10), COLORS["text"])
            if action == "capybara" and self.mode == "capybara":
                cost = " ".join(f"{v}{k[0]}" for k, v in CAPYBARA_DEFS[value]["cost"].items())
                draw_text(surface, self.small_font, cost, (button.rect.right - 88, button.rect.top + 10), COLORS["text"])
        hints = ["ЛКМ: поставить/собрать", "ПКМ или U: улучшить", "F5: сохранить  F9: загрузить", "Esc: пауза"]
        y = HEIGHT - 50
        for hint in hints:
            draw_text(surface, self.small_font, hint, (MAP_W + 18, y), COLORS["cream"])
            y += 14

    def handle_click(self, pos, game):
        for button in self.buttons:
            if not button.hit(pos):
                continue
            action, value = button.action
            if action == "mode":
                self.mode = value
            elif action == "building":
                game.farm.selected_building = value
            elif action == "capybara":
                game.farm.selected_capybara = value
            elif action == "start_wave":
                game.farm.wave_manager.start_wave()
            elif action == "save":
                game.save_manager.save_game(game.farm)
                game.farm.set_message("Прогресс сохранен")
            return True
        return False

    def draw_center_screen(self, surface, title, lines, buttons=None):
        surface.fill((112, 165, 117))
        draw_text(surface, self.big_font, title, (WIDTH // 2, 86), COLORS["cream"], center=True)
        y = 145
        for line in lines:
            draw_text(surface, self.font, line, (WIDTH // 2, y), COLORS["white"], center=True)
            y += 30
        if buttons:
            for btn in buttons:
                btn.draw(surface, self.font)
