import pygame
from pygame.locals import *
import random

pygame.init()

# Game window
game_width = 800
game_height = 500
screen_size = (game_width, game_height)
game_window = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Side Scroller')
padding_y = 50

# Colors
black = (0, 0, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)

# Timing settings
bullet_cooldown = 500
last_bullet_time = pygame.time.get_ticks()
next_enemy_spawn = pygame.time.get_ticks()

# Game levels and difficulty
round = 1
enemies_killed = 0
enemy_speed = 2
enemy_spawn_interval = 3000
show_round_two_popup = False
show_round_three_popup = False
boss_spawned = False
enemy_bullet_cooldown = 1500
last_enemy_bullet_time = pygame.time.get_ticks()

# Gravity and jumping
gravity = 0.5
jump_power = -10
ground_level = game_height - 100

# Scale image helper function
def scale_image(image, new_width):
    image_scale = new_width / image.get_rect().width
    new_height = image.get_rect().height * image_scale
    scaled_size = (new_width, new_height)
    return pygame.transform.scale(image, scaled_size)

# Load background image
bg = pygame.image.load('images/bg.png').convert_alpha()
bg = scale_image(bg, game_width)
bg_scroll = 0

# Load player images
player_images = []
for i in range(2):
    player_image = pygame.image.load(f'images/player/p{i}.png').convert_alpha()
    player_image = scale_image(player_image, 70)
    player_images.append(player_image)

# Load heart images for health
heart_images = []
for i in range(8):
    heart_image = pygame.image.load(f'images/hearts/heart{i}.png').convert_alpha()
    heart_image = scale_image(heart_image, 30)
    heart_images.append(heart_image)

# Load enemy images
enemy_images = []
for i in range(1, 4):
    enemy_image = pygame.image.load(f'images/enemies/e{i}.png').convert_alpha()
    enemy_image = scale_image(enemy_image, 50)
    enemy_image = pygame.transform.flip(enemy_image, True, False)
    enemy_images.append(enemy_image)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.vertical_speed = 0
        self.on_ground = True
        self.lives = 3
        self.score = 0
        self.facing_right = True
        self.image_index = 0
        self.image = player_images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        if not self.on_ground:
            self.vertical_speed += gravity
        self.y += self.vertical_speed

        if self.y >= ground_level:
            self.y = ground_level
            self.vertical_speed = 0
            self.on_ground = True

        self.image_index += 1
        if self.image_index >= len(player_images):
            self.image_index = 0

        self.image = player_images[self.image_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect.x = self.x
        self.rect.y = self.y

        if pygame.sprite.spritecollide(self, enemy_group, True):
            self.lives -= 1

        if pygame.sprite.spritecollide(self, enemy_bullet_group, True):
            self.lives -= 1

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, facing_right):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 5 if facing_right else -5
        self.rect = Rect(x, y, 10, 10)

    def draw(self):
        pygame.draw.circle(game_window, yellow, (self.x, self.y), self.radius)

    def update(self):
        self.x += self.speed
        self.rect.x = self.x
        if self.x < 0 or self.x > game_width:
            self.kill()

# Enemy bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = -4
        self.rect = Rect(x, y, 10, 10)

    def draw(self):
        pygame.draw.circle(game_window, red, (self.x, self.y), self.radius)

    def update(self):
        self.x += self.speed
        self.rect.x = self.x
        if self.x < 0 or self.x > game_width:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = game_width
        self.image_index = 0
        self.image = enemy_images[self.image_index]
        self.rect = self.image.get_rect()

        # Set enemy's y position to slightly below the ground level
        self.y = ground_level + 20
        self.rect.x = self.x
        self.rect.y = self.y

        # Set initial time for bullet shooting
        self.last_enemy_bullet_time = pygame.time.get_ticks()

    def update(self):
        self.x -= enemy_speed
        self.image_index += 0.25
        if self.image_index >= len(enemy_images):
            self.image_index = 0
        self.image = enemy_images[int(self.image_index)]
        self.rect.x = self.x

        # Check for enemy bullet cooldown and shoot more frequently
        if round == 2 and self.last_enemy_bullet_time + 1000 < pygame.time.get_ticks():
            enemy_bullet = EnemyBullet(self.rect.x, self.rect.y + self.image.get_height() // 2)
            enemy_bullet_group.add(enemy_bullet)
            self.last_enemy_bullet_time = pygame.time.get_ticks()

        if pygame.sprite.spritecollide(self, bullet_group, True):
            self.kill()
            global enemies_killed
            enemies_killed += 1
            player.score += 1

        if self.x < 0:
            self.kill()

# Boss Enemy class
class BossEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.health = 10  # Higher health than normal enemies
        self.image = scale_image(enemy_images[0], 120)  # Larger size than normal enemies
        self.rect = self.image.get_rect()
        self.y = ground_level + 20
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        super().update()

        # Boss health handling
        if pygame.sprite.spritecollide(self, bullet_group, True):
            self.health -= 1
            if self.health <= 0:
                self.kill()
                global enemies_killed
                enemies_killed += 1
                player.score += 5  # Boss gives more score when killed
                # Call game over with congratulation message
                game_over("Congratulations! You defeated the boss!")

# Create a function for game over with a message
def game_over(message):
    font = pygame.font.Font(pygame.font.get_default_font(), 48)
    text = font.render(message, True, red)
    text_rect = text.get_rect(center=(game_width // 2, game_height // 2))
    game_window.blit(text, text_rect)
    pygame.display.update()
    pygame.time.wait(3000)  # Pause for 3 seconds to show the message
    pygame.quit()
    exit()

# Create sprite groups
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()

# Create player instance
player_x = 30
player_y = ground_level
player = Player(player_x, player_y)
player_group.add(player)

# Draw message based on round
def draw_message(round_number):
    font = pygame.font.Font(pygame.font.get_default_font(), 36)
    if round_number == 2:
        message = "Round 2! Press Enter to continue!"
    elif round_number == 3:
        message = "Final Round! Boss incoming! Press Enter to continue!"
    
    text = font.render(message, True, red)
    text_rect = text.get_rect(center=(game_width // 2, game_height // 2))
    game_window.blit(text, text_rect)
    pygame.display.update()

# Game loop
clock = pygame.time.Clock()
fps = 120
running = True
bg_scroll = 0

while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    if show_round_two_popup:
        draw_message(2)
        keys = pygame.key.get_pressed()
        if keys[K_RETURN]:
            show_round_two_popup = False
            round = 2
            enemy_speed = 3
            enemy_spawn_interval = 1500
        continue

    if show_round_three_popup:
        draw_message(3)
        keys = pygame.key.get_pressed()
        if keys[K_RETURN]:
            show_round_three_popup = False
            round = 3
            enemy_speed = 4  # Increase speed slightly
            enemy_spawn_interval = 1000
        continue

    keys = pygame.key.get_pressed()

    # Player controls
    if keys[K_LEFT]:
        player.x -= 3
        player.facing_right = False
    if keys[K_RIGHT]:
        player.x += 3
        player.facing_right = True
    if keys[K_UP] and player.on_ground:
        player.vertical_speed = jump_power
        player.on_ground = False

    # Shooting bullets
    if keys[K_SPACE] and last_bullet_time + bullet_cooldown < pygame.time.get_ticks():
        bullet_x = player.x + (player.image.get_width() if player.facing_right else 0)
        bullet_y = player.y + player.image.get_height() // 2
        bullet = Bullet(bullet_x, bullet_y, player.facing_right)
        bullet_group.add(bullet)
        last_bullet_time = pygame.time.get_ticks()

    # Spawn enemies
    if next_enemy_spawn < pygame.time.get_ticks():
        
        if round == 3 and not boss_spawned:
            boss_enemy = BossEnemy()  # Spawn the boss
            enemy_group.add(boss_enemy)
            boss_spawned = True
        else:
            enemy = Enemy()
            enemy_group.add(enemy)

        next_enemy_spawn = random.randint(pygame.time.get_ticks(), pygame.time.get_ticks() + enemy_spawn_interval)

    # Background scrolling
    bg_scroll += 1
    if bg_scroll >= game_width:
        bg_scroll = 0

    # Draw everything
    game_window.blit(bg, (0 - bg_scroll, 0))
    game_window.blit(bg, (game_width - bg_scroll, 0))

    player_group.update()
    bullet_group.update()
    enemy_group.update()
    enemy_bullet_group.update()

    player_group.draw(game_window)
    for bullet in bullet_group:
        bullet.draw()
    for enemy_bullet in enemy_bullet_group:
        enemy_bullet.draw()
    enemy_group.draw(game_window)

    # Display player lives as hearts
    for i in range(player.lives):
        heart_image = heart_images[0]
        heart_x = 10 + i * (heart_image.get_width() + 10)
        heart_y = 10
        game_window.blit(heart_image, (heart_x, heart_y))

    # Display player score
    font = pygame.font.Font(pygame.font.get_default_font(), 24)
    score_text = font.render(f'Score: {player.score}', True, black)
    game_window.blit(score_text, (game_width - 150, 20))

    # Handle round transitions
    if round == 1 and enemies_killed >= 10:
        show_round_two_popup = True

    if round == 2 and enemies_killed >= 20 and not show_round_three_popup:
        show_round_three_popup = True

    if player.lives == 0:
        game_over("Game Over! You lost all lives.")

    pygame.display.update()

pygame.quit()
