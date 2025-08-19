import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game window
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter 🚀")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Clock
FPS = 60
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 24)

def game_loop():
    # Spaceship
    player_width, player_height = 50, 30
    player = pygame.Rect(WIDTH//2 - player_width//2, HEIGHT-60, player_width, player_height)
    player_speed = 5

    # Bullets
    bullets = []
    bullet_speed = 7

    # Enemies
    enemies = []
    enemy_width, enemy_height = 40, 30
    enemy_speed = 2
    spawn_timer = 0

    # Score
    score = 0

    run = True
    while run:
        clock.tick(FPS)

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # --- Player movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed

        # --- Shooting bullets ---
        if keys[pygame.K_SPACE]:
            if len(bullets) == 0 or bullets[-1].y < HEIGHT - 150:  # limit fire rate
                bullets.append(pygame.Rect(player.centerx-3, player.top-10, 6, 12))

        # --- Move bullets ---
        for bullet in bullets[:]:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets.remove(bullet)

        # --- Spawn enemies ---
        spawn_timer += 1
        if spawn_timer > 60:  # every 1 second
            x_pos = random.randint(0, WIDTH - enemy_width)
            enemies.append(pygame.Rect(x_pos, -enemy_height, enemy_width, enemy_height))
            spawn_timer = 0

        # --- Move enemies ---
        for enemy in enemies[:]:
            enemy.y += enemy_speed
            if enemy.y > HEIGHT:  # Enemy reached bottom = Game Over
                run = False
            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 1
                    break

        # --- Draw everything ---
        screen.fill(BLACK)

        # Draw player
        pygame.draw.rect(screen, GREEN, player)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, bullet)

        # Draw enemies
        for enemy in enemies:
            pygame.draw.rect(screen, RED, enemy)

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    return score

def game_over_screen(score):
    screen.fill(BLACK)
    game_over_text = font.render("GAME OVER!", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    replay_text = font.render("Press R to Replay or Q to Quit", True, WHITE)

    screen.blit(game_over_text, (WIDTH//2 - 70, HEIGHT//2 - 40))
    screen.blit(score_text, (WIDTH//2 - 80, HEIGHT//2))
    screen.blit(replay_text, (WIDTH//2 - 150, HEIGHT//2 + 40))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Replay
                    waiting = False
                    return True
                elif event.key == pygame.K_q:  # Quit
                    pygame.quit()
                    sys.exit()

def main():
    while True:
        score = game_loop()
        if not game_over_screen(score):
            break

main()
