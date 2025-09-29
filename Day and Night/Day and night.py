import pygame
import sys
import random
import os

version = "1.0.3"

pygame.init()
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

pygame.display.set_caption("Day and Night")
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

fps_font = pygame.font.SysFont(None, 30)
font_path = resource_path(os.path.join("Assets", "PixelatedPusab.ttf"))
font = pygame.font.Font(font_path, 48)

full_heart = pygame.transform.scale(
    pygame.image.load(resource_path(os.path.join("Assets", "full heart.png"))).convert_alpha(), 
    (75, 75)
)
half_heart = pygame.transform.scale(
    pygame.image.load(resource_path(os.path.join("Assets", "half heart.png"))).convert_alpha(), 
    (75, 75)
)
empty_heart = pygame.transform.scale(
    pygame.image.load(resource_path(os.path.join("Assets", "empty heart.png"))).convert_alpha(), 
    (75, 75)
)

Tree = pygame.image.load(resource_path(os.path.join("Assets", "02d79efe95b119bded88c1c16fa8985e-removebg-preview.png"))).convert_alpha()
Warning_sign = pygame.transform.scale(pygame.image.load(resource_path(os.path.join("Assets", "pixilart-drawing.png"))).convert_alpha(),(500, 500))

game_over = False
end_screen_cooldown = 0

health = 6
damage_cooldown = 0

GraveStone = pygame.image.load(resource_path(os.path.join("Assets", "GraveStone.png"))).convert_alpha()
GraveStone_height, GraveStone_width = GraveStone.get_height(), GraveStone.get_width()
GraveStone = pygame.transform.scale(GraveStone, (GraveStone_width // 1.75, GraveStone_height // 1.75))

sheet = pygame.image.load(resource_path(os.path.join("Assets", "gosth.png"))).convert_alpha()

ghost_sprites = []
ghost_x, ghost_y = 500, 720
for i in range(4):
    x = i * 25
    frame = sheet.subsurface(pygame.Rect(x, 0, 25, 25))
    ghost_sprites.append(pygame.transform.scale(frame, (200, 200)))

ghost_direction = "right"
ghost_hurtbox = pygame.Rect(ghost_x + 32, ghost_y + 32, 120, 136)
ghost_alive = True
Ghost_respawn_timer = 0
ghost_lowering = False
ghost_lowering_progress = 0
ghost_rising = False
ghost_rising_progress = 0
ghost_respawn_y = 720

room = 5

points = 0

room_ground = {
    1: [pygame.Rect(0, 750, 1920, 330), pygame.Rect(0, 0, 20, 1080)],
    2: [pygame.Rect(0, 750, 1920, 330), pygame.Rect(650, 500, 1270, 580), pygame.Rect(350, 625, 300, 455)],
    3: [pygame.Rect(0, 500, 300, 580), pygame.Rect(0, 700, 550, 380), pygame.Rect(0, 900, 1920, 180), pygame.Rect(1500, 750, 420, 330)],
    4: [pygame.Rect(0, 750, 1920, 330)],
    5: [pygame.Rect(0, 750, 710,  330), pygame.Rect(1210, 750, 210, 330), pygame.Rect(1420, 950, 500, 130)],
    6: [pygame.Rect(0, 950, 1920, 130)]
}

player_x, player_y, player_side_length, player_border_side_length, player_y_velocity = 200,  50, 100, 120, 0

Attack_timer = 0
attack = pygame.Rect(0, 0, 0, 0)
delayed_attack = pygame.Rect(0, 0, 0, 0)

def player_movement():
    global player_x, player_y, player_y_velocity, repeat, damage_cooldown, health, points
    
    player_hurtbox = pygame.Rect(player_x - 10, player_y - 10, player_border_side_length, player_border_side_length )
    player_ground_hitbox = pygame.Rect(player_x + 15, player_y, player_border_side_length - 30, player_border_side_length,)
    player_right_side_hitbox = pygame.Rect(player_x + player_side_length, player_y + 10, 10, player_side_length - 20)
    player_left_side_hitbox = pygame.Rect(player_x - 10, player_y + 10, 10, player_side_length - 20)

    on_ground = False
    for ground in room_ground[room]:
        if player_ground_hitbox.colliderect(ground):
            on_ground = True
            break
    
    right_side_touching = False
    for ground in room_ground[room]:
        if player_right_side_hitbox.colliderect(ground):
            right_side_touching = True
            break

    left_side_touching = False
    for ground in room_ground[room]:
        if player_left_side_hitbox.colliderect(ground):
            left_side_touching = True
            break

    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not left_side_touching:
        player_x -= 3
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not right_side_touching:
        player_x += 3
    if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and repeat < 4:
        player_y_velocity = 5
        repeat += 0.1
    elif on_ground:
        repeat = 0
    else:
        repeat = 5
    
    player_y -= player_y_velocity
    if on_ground:
        player_y_velocity = 0
    else:
        player_y_velocity -= 0.1
    if player_hurtbox.colliderect(ghost_hurtbox) and damage_cooldown <= 0:
        health -= 1
        damage_cooldown = 400
        points -= 100
    damage_cooldown -= 1

def decorations():
    if room == 1:
        pygame.draw.rect(screen, (160, 120, 90), (300, 100, 1200, 600))
        screen.blit(pygame.transform.rotate(font.render("Controls:", True, (0, 0, 0)), 23), (400, 250))
        screen.blit(pygame.transform.rotate(font.render("WASD/Arrow keys for movement", True, (0, 0, 0)), -15), (500, 150))
        screen.blit(pygame.transform.rotate(font.render("JKL for combat", True, (0, 0, 0)), 50), (1150, 300))
    elif room == 3:
        screen.blit(GraveStone, (825, 660))    
    elif room == 4:
        screen.blit(Tree, (1500, 300))
    elif room == 5:
        screen.blit(pygame.transform.rotate(Warning_sign, 60), (710, 515))

def ghost_ai():
    global ghost_hurtbox, ghost_x, ghost_y, ghost_direction, ghost_alive, Ghost_respawn_timer, ghost_lowering, ghost_lowering_progress, ghost_rising, ghost_rising_progress, ghost_respawn_y, points, room

    if room == 3:
        if ghost_alive:
            ghost_hurtbox = pygame.Rect(ghost_x + 32, ghost_y + 32, 120, 136)
        else:
            ghost_hurtbox = pygame.Rect(0, 0, 0, 0)
    else:
        ghost_hurtbox = pygame.Rect(0, 0, 0, 0)

    if room == 3:
        if ghost_alive:
            if ghost_direction == "right":
                ghost_x += 1
                screen.blit(ghost_sprites[0], (ghost_x, ghost_y))
                if ghost_x >= 1350:
                    ghost_direction = "left"
            else:
                ghost_x -= 1
                screen.blit(ghost_sprites[1], (ghost_x, ghost_y))
                if ghost_x <= 500:
                    ghost_direction = "right"
        elif ghost_lowering:
            if ghost_lowering_progress < 60:
                ghost_y += 2
                ghost_lowering_progress += 1
                screen.blit(ghost_sprites[2], (ghost_x, ghost_y))
            else:
                ghost_lowering = False
            Ghost_respawn_timer -= 1
        elif ghost_rising:
            if ghost_rising_progress < 60:
                ghost_y -= 2
                ghost_rising_progress += 1
                screen.blit(ghost_sprites[2], (ghost_x, ghost_y))
            else:
                ghost_rising = False
                ghost_alive = True
                ghost_y = ghost_respawn_y
        else:
            Ghost_respawn_timer -= 1

    if ghost_alive:
        if ghost_hurtbox.colliderect(attack):
            ghost_alive = False
            ghost_lowering = True
            ghost_lowering_progress = 0
            Ghost_respawn_timer = 1000
            points += 150
    else:
        if Ghost_respawn_timer <= 0 and not ghost_rising and not ghost_lowering:
            ghost_rising = True
            ghost_rising_progress = 0
            ghost_y = ghost_respawn_y + 120

def fighting():
    global Attack_timer, attack, left_fist, right_fist, top_fist, delayed_attack

    left_fist = pygame.Rect(player_x - 60, player_y + 25, 50, 50)
    right_fist = pygame.Rect(player_x + 110, player_y + 25, 50, 50)
    top_fist = pygame.Rect(player_x + 25, player_y - 60, 50, 50)

    keys = pygame.key.get_pressed()

    if Attack_timer <= 0:
        if keys[pygame.K_j]:
            attack = left_fist
            delayed_attack = left_fist
            Attack_timer = 20
        elif keys[pygame.K_l]:
            attack = right_fist
            delayed_attack = right_fist
            Attack_timer = 20
        elif keys[pygame.K_k]:
            attack = top_fist
            delayed_attack = top_fist
            Attack_timer = 20

    if Attack_timer > 0:
        Attack_timer -= 1
    else:
        attack = pygame.Rect(0, 0, 0, 0)
        delayed_attack = None

    return attack

    

def room_change():
    global room, player_x, player_y
    if player_x + 50 >= 1920:
        room += 1
        player_x = 0
    if player_x + 50 <= 0:
        room -= 1
        player_x = 1820

def sky():
    global room, day
    if room in (1, 2, 4, 5):
        day = True
        screen.fill((208, 246, 255))
        pygame.draw.circle(screen, (255, 243, 128), (50, 50), 150)
    else:
        day = False
        screen.fill((28,28,56))
        pygame.draw.circle(screen, (84, 84, 84), (1870, 50), 150)
        pygame.draw.circle(screen, (107, 107, 107), (1820, 50), 50)
        pygame.draw.circle(screen, (107, 107, 107), (1875, 130), 30)
        pygame.draw.circle(screen, (107, 107, 107), (1810, 130), 20)

def health_bar():
    global health

    if health == 6:
        screen.blit(full_heart, (10, 60))
        screen.blit(full_heart, (80, 60))
        screen.blit(full_heart, (150, 60))
    elif health == 5:
        screen.blit(full_heart, (10, 60))
        screen.blit(full_heart, (80, 60))
        screen.blit(half_heart, (150, 60))
    elif health == 4:
        screen.blit(full_heart, (10, 60))
        screen.blit(full_heart, (80, 60))
        screen.blit(empty_heart, (150, 60))
    elif health == 3:
        screen.blit(full_heart, (10, 60))
        screen.blit(half_heart, (80, 60))
        screen.blit(empty_heart, (150, 60))
    elif health == 2:
        screen.blit(full_heart, (10, 60))
        screen.blit(empty_heart, (80, 60))
        screen.blit(empty_heart, (150, 60))
    elif health == 1:
        screen.blit(half_heart, (10, 60))
        screen.blit(empty_heart, (80, 60))
        screen.blit(empty_heart, (150, 60))

def fps_counter():
    fps = int(clock.get_fps())
    if day:
        fps_text = fps_font.render(f"FPS: {fps}", True, (0, 0, 0))
    else:
        fps_text = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (1800, 10))

def falling_into_the_void():
    global player_x, player_y, player_y_velocity, health, points

    if player_y >= 1080:
        player_y_velocity = 0
        health -= 1
        points -= 200
        player_x, player_y = 200, 50

def end_screen(cooldown):
    screen.fill((0, 0, 0))
    large_font = pygame.font.Font(font_path, 96)
    end_text = large_font.render("Game Over", True, (255, 255, 255))
    info_text = font.render("Press any key to restart", True, (255, 255, 255))
    if cooldown > 0:
        timer_text = font.render(f"Wait {cooldown // 1000 + 1} seconds...", True, (255, 100, 100))
        screen.blit(timer_text, (screen.get_width() // 2 - timer_text.get_width() // 2, 600))
    else:
        screen.blit(info_text, (screen.get_width() // 2 - info_text.get_width() // 2, 500))
    screen.blit(end_text, (screen.get_width() // 2 - end_text.get_width() // 2, 400))
    pygame.display.flip()

def reset_game():
    global health, points, player_x, player_y, player_y_velocity, room, ghost_x, ghost_y, ghost_direction, ghost_alive, Ghost_respawn_timer, ghost_lowering, ghost_lowering_progress, ghost_rising, ghost_rising_progress, ghost_respawn_y, damage_cooldown
    health = 6
    points = 0
    player_x, player_y, player_y_velocity = 200, 50, 0
    room = 4
    ghost_x, ghost_y = 500, 720
    ghost_direction = "right"
    ghost_alive = True
    Ghost_respawn_timer = 0
    ghost_lowering = False
    ghost_lowering_progress = 0
    ghost_rising = False
    ghost_rising_progress = 0
    ghost_respawn_y = 720
    damage_cooldown = 0

def draw():
    sky()
    decorations()
    if damage_cooldown > 0:
        pygame.draw.rect(screen, (205, 105, 45), (player_x - 10, player_y - 10, player_border_side_length, player_border_side_length), border_radius = 20)
        pygame.draw.rect(screen, (250, 135, 70), (player_x - 2.5, player_y - 2.5, player_side_length + 5, player_side_length + 5), border_radius = 20)
    else:
        pygame.draw.rect(screen, (173, 116, 17), (player_x - 10, player_y - 10, player_border_side_length, player_border_side_length), border_radius = 20)
        pygame.draw.rect(screen, (255, 171, 25), (player_x - 2.5, player_y - 2.5, player_side_length + 5, player_side_length + 5), border_radius = 20)
    pygame.draw.rect(screen, (255, 213, 102), fighting(), border_radius = 20)
    for ground in room_ground[room]:
        pygame.draw.rect(screen, (0, 204, 68), ground,)
    if day:
        screen.blit(font.render(f"Points: {points}", True, (0, 0, 0)), (10, 10))
    else:
        screen.blit(font.render(f"Points: {points}", True, (255, 255, 255)), (10, 10))
    health_bar()
    ghost_ai()
    fps_counter()
    pygame.display.flip()

running = True
end_screen_cooldown = 0

running = True
end_screen_cooldown = 0

while running:
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        player_movement()
        falling_into_the_void()
        room_change()
        draw()
        if health <= 0:
            game_over = True
            end_screen_cooldown = 5000
            cooldown_start_time = pygame.time.get_ticks()
    else:
        if end_screen_cooldown > 0:
            elapsed = pygame.time.get_ticks() - cooldown_start_time
            end_screen_cooldown = max(0, 5000 - elapsed)
        end_screen(end_screen_cooldown)
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and end_screen_cooldown == 0:
                reset_game()
                game_over = False

    clock.tick(175)

pygame.quit()
sys.exit()