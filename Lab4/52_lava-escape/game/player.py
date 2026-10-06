import pygame

SPEED = 4

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms, width):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = -13
            self.on_ground = False

        self.vel_y = min(self.vel_y + 0.55, 12)
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))
        
        # Save bottom position prior to vertical step
        prev_bottom = self.rect.bottom
        self.rect.y += int(self.vel_y)
        self.on_ground = False

        for p in platforms:
            # Task 1: Landing triggers strictly when descending and clearing the upper edge
            if self.vel_y > 0 and prev_bottom <= p.top and self.rect.bottom >= p.top:
                if self.rect.right > p.left and self.rect.left < p.right:
                    ptype = getattr(p, 'ptype', 'normal')
                    
                    if ptype == 'spring':
                        # Task 3: Spring launch force
                        self.rect.bottom = p.top
                        self.vel_y = -21
                        self.on_ground = False
                    else:
                        self.rect.bottom = p.top
                        self.vel_y = 0
                        self.on_ground = True
                        
                        # Task 2: Trigger platform crumbling
                        if hasattr(p, 'trigger_crumble'):
                            p.trigger_crumble()

    def draw(self, screen, cam_y):
        dr = self.rect.move(0, -int(cam_y))
        pygame.draw.rect(screen, self.color, dr, border_radius=6)
        pygame.draw.circle(screen, (255, 220, 180), (dr.centerx, dr.top + 8), 7)