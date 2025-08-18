#!/usr/bin/env python3
import pygame
import random
import sys

# --------------- Config ---------------
WIDTH, HEIGHT = 480, 640
LANES = 3
ROAD_MARGIN = 60  # left/right margin for road
FPS = 60

CAR_W, CAR_H = 50, 90
OB_W, OB_H = 50, 90

START_SPEED = 5
SPEED_INC_EVERY = 5     # seconds between speed increases
SPEED_INC_AMOUNT = 0.35
MAX_SPEED = 18

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
YELLOW = (255, 204, 0)
RED = (220, 70, 70)
BLUE = (80, 170, 255)
GREEN = (60, 200, 130)

# --------------- Helpers ---------------
def lane_centers():
    road_width = WIDTH - 2 * ROAD_MARGIN
    lane_width = road_width // LANES
    centers = [ROAD_MARGIN + lane_width // 2 + i * lane_width for i in range(LANES)]
    return centers, lane_width

def draw_road(surface, scroll_y):
    surface.fill((20, 20, 25))
    # road
    pygame.draw.rect(surface, GRAY, (ROAD_MARGIN, 0, WIDTH - 2*ROAD_MARGIN, HEIGHT))
    # road edges
    pygame.draw.line(surface, WHITE, (ROAD_MARGIN, 0), (ROAD_MARGIN, HEIGHT), 6)
    pygame.draw.line(surface, WHITE, (WIDTH-ROAD_MARGIN, 0), (WIDTH-ROAD_MARGIN, HEIGHT), 6)

    centers, lane_width = lane_centers()
    dash_h = 30
    gap = 30
    for c in centers[1:]:  # draw lane separators (skip left edge)
        y = - (scroll_y % (dash_h + gap))
        while y < HEIGHT:
            pygame.draw.line(surface, YELLOW, (c, y), (c, y + dash_h), 6)
            y += dash_h + gap

def blit_text_center(surface, text, y, font, color=WHITE, outline=True):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH//2, y))
    if outline:
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
            o = font.render(text, True, BLACK)
            surface.blit(o, o.get_rect(center=(WIDTH//2+dx, y+dy)))
    surface.blit(render, rect)

# --------------- Game Objects ---------------
class Car:
    def __init__(self):
        self.centers, self.lane_width = lane_centers()
        self.lane = LANES // 2
        self.x = self.centers[self.lane] - CAR_W//2
        self.y = HEIGHT - CAR_H - 20
        self.color = BLUE
        self.target_lane = self.lane
        self.lerp = 1.0  # finished

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), CAR_W, CAR_H)

    def update(self):
        # smooth lane change
        if self.lane != self.target_lane:
            start_x = self.centers[self.lane] - CAR_W//2
            end_x = self.centers[self.target_lane] - CAR_W//2
            self.lerp += 0.12
            if self.lerp >= 1.0:
                self.lane = self.target_lane
                self.x = end_x
                self.lerp = 1.0
            else:
                self.x = start_x + (end_x - start_x) * self.lerp

    def move_left(self):
        if self.target_lane > 0:
            self.lerp = 0.0
            self.target_lane -= 1

    def move_right(self):
        if self.target_lane < LANES-1:
            self.lerp = 0.0
            self.target_lane += 1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect(), border_radius=10)
        # windshield
        pygame.draw.rect(surface, WHITE, (self.rect().x+8, self.rect().y+10, CAR_W-16, 18), border_radius=6)
        # tail lights
        pygame.draw.rect(surface, RED, (self.rect().x+6, self.rect().bottom-10, 12, 6), border_radius=3)
        pygame.draw.rect(surface, RED, (self.rect().right-18, self.rect().bottom-10, 12, 6), border_radius=3)

class Obstacle:
    def __init__(self, lane, y=-OB_H):
        centers, _ = lane_centers()
        self.x = centers[lane] - OB_W//2
        self.y = y
        self.color = GREEN if random.random() < 0.75 else (200, 200, 200)

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), OB_W, OB_H)

    def update(self, speed):
        self.y += speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect(), border_radius=10)
        pygame.draw.rect(surface, BLACK, (self.rect().x+10, self.rect().y+12, OB_W-20, 20), border_radius=6)

# --------------- Game Loop ---------------
def main():
    pygame.init()
    pygame.display.set_caption("Lane Racer - Python")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    try:
        big = pygame.font.SysFont("bahnschrift", 42, bold=True)
        medium = pygame.font.SysFont("bahnschrift", 28, bold=True)
        small = pygame.font.SysFont("bahnschrift", 20)
    except:
        big = pygame.font.Font(None, 42)
        medium = pygame.font.Font(None, 28)
        small = pygame.font.Font(None, 20)

    # game state
    score = 0
    best = 0
    speed = START_SPEED
    last_inc_time = 0
    spawn_timer = 0
    spawn_interval = 900  # ms
    road_scroll = 0

    car = Car()
    obstacles = []

    state = "menu"  # menu, play, gameover

    running = True
    while running:
        dt = clock.tick(FPS)
        t = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = "play"
                        score = 0
                        speed = START_SPEED
                        last_inc_time = t
                        spawn_timer = 0
                        car = Car()
                        obstacles = []
                elif state == "play":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        car.move_left()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        car.move_right()
                    elif event.key in (pygame.K_p,):
                        state = "menu"  # pause to menu
                elif state == "gameover":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = "menu"

        if state == "play":
            # Game updates
            car.update()
            road_scroll += speed
            # Spawn obstacles
            spawn_timer += dt
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                lane_choices = list(range(LANES))
                random.shuffle(lane_choices)
                # spawn 1 or 2 cars with slight offset to avoid impossible gaps
                count = 1 if random.random() < 0.6 else 2
                for i in range(count):
                    lane = lane_choices[i]
                    y_offset = -OB_H - i * (OB_H + 20)
                    obstacles.append(Obstacle(lane, y=y_offset))

            for ob in obstacles:
                ob.update(speed)

            # remove off-screen obstacles and count score
            kept = []
            for ob in obstacles:
                if ob.y > HEIGHT:
                    score += 1
                else:
                    kept.append(ob)
            obstacles = kept

            # collisions
            for ob in obstacles:
                if car.rect().colliderect(ob.rect()):
                    best = max(best, score)
                    state = "gameover"

            # dynamic difficulty
            if t - last_inc_time > SPEED_INC_EVERY * 1000 and speed < MAX_SPEED:
                speed += SPEED_INC_AMOUNT
                last_inc_time = t
                # mildly tighten spawn as speed rises
                spawn_interval = max(450, spawn_interval - 20)

        # --------------- Draw ---------------
        draw_road(screen, road_scroll)
        if state == "menu":
            blit_text_center(screen, "LANE RACER", HEIGHT//2 - 70, big, color=WHITE)
            blit_text_center(screen, "← →  to move", HEIGHT//2, medium)
            blit_text_center(screen, "Press ENTER to start", HEIGHT//2 + 50, medium)
        elif state == "play":
            for ob in obstacles:
                ob.draw(screen)
            car.draw(screen)
            # HUD
            hud = medium.render(f"Score: {score}", True, WHITE)
            screen.blit(hud, (12, 10))
            spd = small.render(f"Speed: {speed:.1f}", True, WHITE)
            screen.blit(spd, (12, 44))
        elif state == "gameover":
            for ob in obstacles:
                ob.draw(screen)
            car.draw(screen)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            blit_text_center(screen, "CRASH!", HEIGHT//2 - 60, big, color=RED)
            blit_text_center(screen, f"Score: {score}   Best: {best}", HEIGHT//2, medium)
            blit_text_center(screen, "Press ENTER for menu", HEIGHT//2 + 50, medium)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
