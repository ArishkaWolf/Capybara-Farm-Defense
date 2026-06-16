import pygame

from .constants import COLORS, FPS, HEIGHT, MAP_W, WIDTH
from .farm import Farm
from .particles import ParticleSystem
from .save_manager import SaveManager
from .ui import Button, UI
from .utils import world_to_grid


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Capybara Farm Defense")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 15)
        self.big_font = pygame.font.SysFont("arial", 38, bold=True)
        self.particles = ParticleSystem()
        self.save_manager = SaveManager()
        self.ui = UI()
        self.ui.set_fonts(self.font, self.big_font, self.small_font)
        self.farm = Farm(self.particles)
        self.state = "menu"
        self.running = True
        self.fade = 0
        self.menu_buttons = [
            Button((WIDTH // 2 - 120, 250, 240, 44), "Новая игра", ("new", None)),
            Button((WIDTH // 2 - 120, 304, 240, 44), "Продолжить", ("continue", None)),
            Button((WIDTH // 2 - 120, 358, 240, 44), "Обучение", ("help", None)),
            Button((WIDTH // 2 - 120, 412, 240, 44), "Выход", ("quit", None)),
        ]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self._events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def new_game(self):
        self.particles = ParticleSystem()
        self.farm = Farm(self.particles)
        self.state = "playing"

    def load_game(self):
        data = self.save_manager.load_game()
        if data:
            self.particles = ParticleSystem()
            self.farm = Farm(self.particles)
            self.farm.from_json(data)
            self.state = "playing"
        else:
            self.new_game()
            self.farm.set_message("Сохранение не найдено")

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._click(event.pos, event.button)

    def _key(self, key):
        if key == pygame.K_ESCAPE:
            if self.state == "playing":
                self.state = "pause"
            elif self.state in ("pause", "help"):
                self.state = "playing" if self.state == "pause" else "menu"
        if self.state == "playing":
            if key == pygame.K_SPACE:
                self.farm.wave_manager.start_wave()
            elif key == pygame.K_F5:
                self.save_manager.save_game(self.farm)
                self.farm.set_message("Прогресс сохранен")
            elif key == pygame.K_F9:
                self.load_game()
            elif key == pygame.K_u:
                pos = pygame.mouse.get_pos()
                if pos[0] < MAP_W:
                    self.farm.upgrade_cell(world_to_grid(pos))

    def _click(self, pos, button):
        if self.state == "menu":
            for menu_button in self.menu_buttons:
                if menu_button.hit(pos):
                    action = menu_button.action[0]
                    if action == "new":
                        self.new_game()
                    elif action == "continue":
                        self.load_game()
                    elif action == "help":
                        self.state = "help"
                    elif action == "quit":
                        self.running = False
            return
        if self.state == "help":
            self.state = "menu"
            return
        if self.state in ("gameover", "victory"):
            self.state = "menu"
            return
        if self.state == "pause":
            self.state = "playing"
            return
        if self.state != "playing":
            return
        if button == 3 and pos[0] < MAP_W:
            self.farm.upgrade_cell(world_to_grid(pos))
            return
        if pos[0] >= MAP_W:
            self.ui.handle_click(pos, self)
        else:
            self.farm.handle_map_click(pos, self.ui.mode)

    def _update(self, dt):
        self.fade = max(0, self.fade - dt)
        if self.state == "playing":
            self.farm.update(dt)
            self.particles.update(dt)
            base = self.farm.base
            if not base or base.hp <= 0:
                self.save_manager.record_score(self.farm.wave_manager.wave)
                self.state = "gameover"
            elif self.farm.wave_manager.is_victory():
                self.save_manager.record_score(self.farm.wave_manager.wave)
                self.state = "victory"

    def _draw(self):
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "help":
            self._draw_help()
        else:
            self.farm.draw(self.screen, self.small_font)
            self.particles.draw(self.screen)
            self.ui.draw_hud(self.screen, self.farm, self.save_manager)
            if self.state == "pause":
                self._overlay("Пауза", ["Клик или Esc — продолжить", "F5 сохраняет прогресс во время игры"])
            elif self.state == "gameover":
                self._overlay("Ферма пала", [f"Вы продержались до волны {self.farm.wave_manager.wave}", "Клик — в меню"])
            elif self.state == "victory":
                self._overlay("Победа!", ["Капибары отстояли ферму до 15-й волны", "Клик — в меню"])
        pygame.display.flip()

    def _draw_menu(self):
        self.screen.fill((104, 160, 110))
        self._draw_capybara_logo()
        title = self.big_font.render("Capybara Farm Defense", True, COLORS["cream"])
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        subtitle = self.font.render("уютная стратегия о ферме, волнах и очень занятых капибарах", True, COLORS["white"])
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 143)))
        for button in self.menu_buttons:
            button.draw(self.screen, self.font)
        score = self.font.render(f"Лучший результат: волна {self.save_manager.data.get('best_wave', 0)}", True, COLORS["cream"])
        self.screen.blit(score, score.get_rect(center=(WIDTH // 2, 500)))
        scores = self.save_manager.data.get("top_scores", [])[:5]
        if scores:
            y = 532
            header = self.small_font.render("Таблица рекордов", True, COLORS["cream"])
            self.screen.blit(header, header.get_rect(center=(WIDTH // 2, y)))
            for i, item in enumerate(scores, start=1):
                row = self.small_font.render(f"{i}. волна {item.get('wave', 0)}", True, COLORS["white"])
                self.screen.blit(row, row.get_rect(center=(WIDTH // 2, y + 18 * i)))
        pygame.display.flip()

    def _draw_help(self):
        lines = [
            "Цель: защитить домик в центре карты от волн врагов.",
            "В фазе подготовки ставьте постройки и размещайте капибар.",
            "Собирайте круглые ресурсы кликом; фермы производят ресурсы сами.",
            "Башни стреляют, заборы задерживают, пруд лечит союзников.",
            "Капибары: защитник, лучник, строитель, лекарь и танк.",
            "Враги усиливаются; каждая 5-я волна приводит босса.",
            "ЛКМ — действие, ПКМ/U — улучшить клетку, Space — начать волну.",
            "F5 — сохранить, F9 — загрузить, Esc — пауза.",
            "Кликните, чтобы вернуться в меню.",
        ]
        self.ui.draw_center_screen(self.screen, "Обучение", lines)
        pygame.display.flip()

    def _overlay(self, title, lines):
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        layer.fill((26, 38, 32, 170))
        self.screen.blit(layer, (0, 0))
        draw_box = pygame.Rect(WIDTH // 2 - 240, HEIGHT // 2 - 120, 480, 240)
        pygame.draw.rect(self.screen, (94, 132, 98), draw_box, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["cream"], draw_box, 3, border_radius=10)
        title_img = self.big_font.render(title, True, COLORS["cream"])
        self.screen.blit(title_img, title_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 65)))
        y = HEIGHT // 2 - 12
        for line in lines:
            img = self.font.render(line, True, COLORS["white"])
            self.screen.blit(img, img.get_rect(center=(WIDTH // 2, y)))
            y += 34

    def _draw_capybara_logo(self):
        cx, cy = WIDTH // 2, 185
        pygame.draw.ellipse(self.screen, COLORS["capy"], (cx - 86, cy - 34, 160, 70))
        pygame.draw.circle(self.screen, COLORS["capy"], (cx + 64, cy - 18), 33)
        pygame.draw.circle(self.screen, COLORS["capy_dark"], (cx + 75, cy - 25), 4)
        pygame.draw.circle(self.screen, COLORS["capy_dark"], (cx + 87, cy - 14), 4)
        pygame.draw.arc(self.screen, COLORS["water"], (cx - 104, cy - 20, 180, 82), 0.2, 2.9, 4)
