import pygame
from game.player import Player
from game.world import generate_platforms, draw_lava, PLATFORM_COLOR, CRUMBLING_COLOR, SPRING_COLOR

WIDTH, HEIGHT = 500, 640
FPS = 60
BG = (20, 15, 30)
GROUND_Y = HEIGHT + 200

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Lava Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 20, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 42, bold=True)
        self.surge_font = pygame.font.SysFont("monospace", 18, bold=True)
        self.reset()

    def reset(self):
        self.platforms = generate_platforms(WIDTH, GROUND_Y)
        self.player = Player(WIDTH // 2 - 16, GROUND_Y - 50)
        # Center camera on player at start
        self.cam_y = self.player.rect.centery - HEIGHT // 2
        self.lava_y = GROUND_Y + 60
        self.lava_base_rise = 0.4
        self.score = 0
        self.game_over = False
        self.won = False
        self.top_y = self.platforms[-1].y
        self.frame = 0

        # Task 4 Surge Mechanics
        self.is_surging = False
        self.surge_timer = 0
        self.surge_interval = 300  # Surge occurs every ~5 seconds
        self.surge_duration = 120  # Surge lasts ~2 seconds

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
        return True

    def update(self):
        if self.game_over or self.won:
            return
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms, WIDTH)

        # Task 2: Update platform timers and remove disintegrated ones
        for p in self.platforms:
            if hasattr(p, 'update'):
                p.update()
        self.platforms = [p for p in self.platforms if not getattr(p, 'destroyed', False)]

        target = self.player.rect.centery - HEIGHT // 2
        if target < self.cam_y:
            self.cam_y = target

        # Gradually scale base lava ascent rate
        self.lava_base_rise = min(1.2, self.lava_base_rise + 0.0003)

        # Task 4: Manage periodic lava surge state
        self.surge_timer += 1
        if not self.is_surging and self.surge_timer >= self.surge_interval:
            self.is_surging = True
            self.surge_timer = 0
        elif self.is_surging and self.surge_timer >= self.surge_duration:
            self.is_surging = False
            self.surge_timer = 0

        current_rise = self.lava_base_rise * 2.5 if self.is_surging else self.lava_base_rise
        self.lava_y -= current_rise

        self.score = max(0, (GROUND_Y - self.player.rect.y) // 10)
        self.frame += 1

        if self.player.rect.bottom >= self.lava_y:
            self.game_over = True
        if self.player.rect.top <= self.top_y - 20:
            self.won = True

    def draw(self):
        self.screen.fill(BG)
        for p in self.platforms:
            dr = p.get_draw_rect(self.cam_y) if hasattr(p, 'get_draw_rect') else p.move(0, -int(self.cam_y))
            
            # Task 3 & 2: Platform color differentiation
            ptype = getattr(p, 'ptype', 'normal')
            if ptype == 'crumbling':
                color = CRUMBLING_COLOR
            elif ptype == 'spring':
                color = SPRING_COLOR
            else:
                color = PLATFORM_COLOR

            pygame.draw.rect(self.screen, color, dr, border_radius=4)

        self.player.draw(self.screen, self.cam_y)
        draw_lava(self.screen, self.lava_y, self.cam_y, WIDTH, HEIGHT, self.frame)

        # Standard HUD
        sc = self.font.render(f"Height: {self.score}m  R=Restart", True, (220, 200, 180))
        self.screen.blit(sc, (8, 10))

        # Task 4: Render Danger Meter HUD & Surge Text
        self._draw_danger_hud()

        if self.game_over:
            self._msg("LAVA GOT YOU!", (220, 80, 40))
        if self.won:
            self._msg("ESCAPED!", (80, 220, 100))
        pygame.display.flip()

    def _draw_danger_hud(self):
        current_rise = self.lava_base_rise * 2.5 if self.is_surging else self.lava_base_rise
        max_possible_speed = 1.2 * 2.5
        fill_pct = min(1.0, current_rise / max_possible_speed)

        bar_x, bar_y, bar_w, bar_h = 320, 12, 160, 18
        pygame.draw.rect(self.screen, (50, 40, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        
        fill_color = (255, 50, 50) if self.is_surging else (220, 140, 40)
        pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, int(bar_w * fill_pct), bar_h), border_radius=3)
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=3)

        label = self.surge_font.render("DANGER", True, (240, 240, 240))
        self.screen.blit(label, (bar_x - 75, bar_y - 1))

        if self.is_surging:
            surge_msg = self.surge_font.render("!! LAVA SURGE !!", True, (255, 60, 60))
            self.screen.blit(surge_msg, (WIDTH // 2 - surge_msg.get_width() // 2, 40))

    def _msg(self, text, color):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.screen.blit(ov, (0, 0))
        m = self.big_font.render(text, True, color)
        s = self.font.render("Press R to Play Again", True, (200, 200, 200))
        self.screen.blit(m, (WIDTH // 2 - m.get_width() // 2, HEIGHT // 2 - 40))
        self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 20))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()