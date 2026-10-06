import pygame
import random
import math

PLATFORM_COLOR = (100, 80, 50)
CRUMBLING_COLOR = (180, 70, 50)
SPRING_COLOR = (60, 220, 100)
LAVA_COLOR = (220, 60, 20)

class Platform(pygame.Rect):
    def __init__(self, x, y, width, height, ptype='normal'):
        super().__init__(x, y, width, height)
        self.ptype = ptype  # 'normal', 'crumbling', or 'spring'
        self.is_crumbling = False
        self.timer = 0
        self.max_timer = 45  # ~0.75 seconds before disintegration
        self.destroyed = False

    def trigger_crumble(self):
        if self.ptype == 'crumbling' and not self.is_crumbling:
            self.is_crumbling = True

    def update(self):
        if self.is_crumbling:
            self.timer += 1
            if self.timer >= self.max_timer:
                self.destroyed = True

    def get_draw_rect(self, cam_y):
        dr = self.move(0, -int(cam_y))
        if self.is_crumbling:
            # Shake offset horizontally when crumbling
            shake_offset = random.randint(-3, 3)
            dr = dr.move(shake_offset, 0)
        return dr


def generate_platforms(width, base_y, count=30):
    # Ground platform is always normal
    plats = [Platform(0, base_y, width, 20, ptype='normal')]
    y = base_y - 110
    for i in range(count):
        w = random.randint(80, 200)
        x = random.randint(0, width - w)
        
        # Decide platform type
        rnd = random.random()
        if rnd < 0.30:
            ptype = 'crumbling'
        elif rnd < 0.50:
            ptype = 'spring'
        else:
            ptype = 'normal'

        plats.append(Platform(x, y, w, 16, ptype=ptype))
        y -= random.randint(80, 130)
    return plats


def draw_lava(screen, lava_y, cam_y, width, height, frame):
    ly = int(lava_y - cam_y)
    if ly < height:
        pts = [(0, ly)]
        for x in range(0, width + 20, 20):
            pts.append((x, ly + int(math.sin(x * 0.08 + frame * 0.1) * 8)))
        pts.append((width, height))
        pts.append((0, height))
        pygame.draw.polygon(screen, LAVA_COLOR, pts)
        
        s = pygame.Surface((width, 30), pygame.SRCALPHA)
        for i in range(15):
            pygame.draw.line(s, (255, 100, 0, max(0, 60 - i * 4)), (0, i), (width, i), 1)
        screen.blit(s, (0, ly - 15))