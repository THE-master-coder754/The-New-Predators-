import pygame
import random
import sys
import os

SCALE = 3           
WIDTH = 800
HEIGHT = 300
FPS = 60
GROUND_Y = 230      
GRAVITY = 0.7
JUMP_FORCE = -13.5
OBSTACLE_SPEED_START = 8
SPEED_INCREMENT = 0.004   

BG_COLOR = (135, 195, 235)
GROUND_COLOR = (60, 120, 50)
GROUND_DARK = (45, 90, 38)
TEXT_COLOR = (20, 50, 20)

def load(name):
    img = pygame.image.load(os.path.join(os.path.dirname(__file__), name)).convert_alpha()
    w, h = img.get_size()
    return pygame.transform.scale(img, (w * SCALE, h * SCALE))

class Deer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = [load("deer_1.png"), load("deer_2.png"), load("deer_3.png")]
        self.frame_index = 0
        self.frame_timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_Y
        self.rect.x = 80
        self.vel_y = 0
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

        # animate only while on ground
        if self.on_ground:
            self.frame_timer += 1
            if self.frame_timer >= 8:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 1   # mid-air pose
        self.image = self.frames[self.frame_index]

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

class Obstacle(pygame.sprite.Sprite):
    IMAGES = []

    def __init__(self, speed):
        super().__init__()
        self.image = random.choice(Obstacle.IMAGES)
        self.rect = self.image.get_rect()
        self.rect.bottom = GROUND_Y
        self.rect.x = WIDTH + 20
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

def pixel_collide(deer, obstacle):
    offset = (obstacle.rect.x - deer.rect.x, obstacle.rect.y - deer.rect.y)
    deer_mask = pygame.mask.from_surface(deer.image)
    obs_mask = pygame.mask.from_surface(obstacle.image)
    return deer_mask.overlap(obs_mask, offset) is not None

def draw_ground(screen):
    pygame.draw.rect(screen, GROUND_DARK, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, 10))
    pygame.draw.rect(screen, GROUND_DARK, (0, GROUND_Y + 10, WIDTH, 4))
    for x in range(0, WIDTH, 18):
        pygame.draw.line(screen, (80, 160, 50), (x, GROUND_Y), (x - 3, GROUND_Y - 5), 2)
        pygame.draw.line(screen, (80, 160, 50), (x + 5, GROUND_Y), (x + 7, GROUND_Y - 6), 2)
        pygame.draw.line(screen, (50, 130, 40), (x + 10, GROUND_Y), (x + 9, GROUND_Y - 4), 2)

def draw_text(screen, font, text, x, y, color=TEXT_COLOR):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Deer Run")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("monospace", 36, bold=True)
    font_small = pygame.font.SysFont("monospace", 20)

    Obstacle.IMAGES = [
        load("cactus_1.png"),
        load("cactus_2.png"),
        load("rock_1.png"),
        load("rock_2.png"),
        load("stump_1.png"),
        load("tree_1.png"),
    ]

    def reset():
        deer = Deer()
        obstacles = pygame.sprite.Group()
        return deer, obstacles

    deer, obstacles = reset()
    score = 0
    highscore = 0
    speed = OBSTACLE_SPEED_START
    spawn_timer = 0
    spawn_interval = 90   # frames between spawns
    game_over = False
    started = False

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if game_over:
                        deer, obstacles = reset()
                        score = 0
                        speed = OBSTACLE_SPEED_START
                        spawn_timer = 0
                        game_over = False
                        started = True
                    else:
                        started = True
                        deer.jump()

        screen.fill(BG_COLOR)
        draw_ground(screen)

        if started and not game_over:
            score += 1
            speed += SPEED_INCREMENT
            spawn_interval = max(45, 90 - int(speed * 3))

            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                obstacles.add(Obstacle(speed))

            obstacles.update()
            deer.update()

            for obs in obstacles:
                if pixel_collide(deer, obs):
                    game_over = True
                    if score > highscore:
                        highscore = score

        # draw
        obstacles.draw(screen)
        screen.blit(deer.image, deer.rect)

        # score
        draw_text(screen, font_small, f"SCORE  {score // 6:05d}", WIDTH - 200, 20)
        if highscore > 0:
            draw_text(screen, font_small, f"BEST  {highscore // 6:05d}", WIDTH - 200, 46)

        if not started:
            draw_text(screen, font_big, "DEER RUN", WIDTH // 2 - 100, HEIGHT // 2 - 60)
            draw_text(screen, font_small, "Press SPACE or UP to start", WIDTH // 2 - 130, HEIGHT // 2)

        if game_over:
            draw_text(screen, font_big, "GAME OVER", WIDTH // 2 - 115, HEIGHT // 2 - 60)
            draw_text(screen, font_small, "Press SPACE to restart", WIDTH // 2 - 110, HEIGHT // 2)

        pygame.display.flip()

if __name__ == "__main__":
    main()