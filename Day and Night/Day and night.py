import pygame
import sys
import math
import os

version = "0.0.5"

pygame.init()
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

pygame.display.set_caption("Day and Night")
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

fps_font = pygame.font.SysFont(None, 30)
font_path = resource_path(os.path.join("Assets", "PixelatedPusab.ttf"))
font = pygame.font.Font(font_path, 48)

full_heart = pygame.transform.scale(pygame.image.load(resource_path(os.path.join("Assets", "full heart.png"))).convert_alpha(), (75, 75))
half_heart = pygame.transform.scale(pygame.image.load(resource_path(os.path.join("Assets", "half heart.png"))).convert_alpha(), (75, 75))
empty_heart = pygame.transform.scale(pygame.image.load(resource_path(os.path.join("Assets", "empty heart.png"))).convert_alpha(), (75, 75))

Tree = pygame.image.load(resource_path(os.path.join("Assets", "02d79efe95b119bded88c1c16fa8985e-removebg-preview.png"))).convert_alpha()
Resized_tree = pygame.transform.scale(Tree, (384, 453))

Warning_sign = pygame.transform.scale(pygame.image.load(resource_path(os.path.join("Assets", "pixilart-drawing.png"))).convert_alpha(),(500, 500))

game_over = False
end_screen_cooldown = 0

health = 6
damage_cooldown = 0

Lives = 10

Skeleton_scaffolding = pygame.image.load(resource_path(os.path.join("Assets", "h8wfw2.png"))).convert_alpha()
skeleton_arm = pygame.Rect(0, 0, 0, 0)
skeleton_arm_x, skeleton_arm_y, skeleton_arm_rotation = 1150, 75, -35
skeleton_arm_end_x, skeleton_arm_end_y = skeleton_arm_x, skeleton_arm_y
skeleton_arm_damage_cooldown = 0
arm_length = 200
arm_tip_rect = pygame.Rect(skeleton_arm_end_x - 10, skeleton_arm_end_y - 10, 20, 20)
arm_hit_cooldown = 0

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

room = 1

points = 0
perma_points = 0

room_ground = {
    1: [pygame.Rect(0, 750, 1920, 330), pygame.Rect(0, 0, 20, 1080)],
    2: [pygame.Rect(0, 750, 1920, 330), pygame.Rect(650, 500, 1270, 580), pygame.Rect(350, 625, 300, 455)],
    3: [pygame.Rect(0, 500, 300, 580), pygame.Rect(0, 700, 550, 380), pygame.Rect(0, 900, 1920, 180), pygame.Rect(1500, 750, 420, 330)],
    4: [pygame.Rect(0, 750, 1920, 330)],
    5: [pygame.Rect(0, 750, 710,  330), pygame.Rect(1210, 750, 210, 330), pygame.Rect(1420, 950, 500, 130)],
    6: [pygame.Rect(0, 950, 1920, 130)],
    7: [pygame.Rect(0, 950, 400, 130), pygame.Rect(600, 700, 300, 200), pygame.Rect(800, 400, 300, 200),pygame.Rect(800, 400, 1900, 75), pygame.Rect(1600, 400, 75, 1900), pygame.Rect(600, 800, 700, 75), pygame.Rect(1225, 400, 75, 475), pygame.Rect(400, 0, 75, 500)],\
    8: [pygame.Rect(0, 400, 250, 680), pygame.Rect(700, 400, 450, 680), pygame.Rect(1800, 900, 120, 180)],
    9: [pygame.Rect(0, 900, 1920, 180), pygame.Rect(400, 600, 250, 580), pygame.Rect(400, 750, 1100, 330), pygame.Rect(1500, 600, 420, 580)],
    10: [pygame.Rect(0, 600, 1920, 480), pygame.Rect(384, 500, 384, 580), pygame.Rect(1152, 500, 384, 580)]
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
    player_ceiling_hitbox = pygame.Rect(player_x + 15, player_y - 10, player_border_side_length - 30, 10)

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

    ceiling_touching = False
    for ground in room_ground[room]:
        if player_ceiling_hitbox.colliderect(ground):
            ceiling_touching = True
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

    if ceiling_touching and player_y_velocity > 0:
        player_y_velocity = 0
        for ground in room_ground[room]:
            if player_ceiling_hitbox.colliderect(ground):
                player_y = ground.bottom + 10

    if on_ground:
        player_y_velocity = 0
    else:
        player_y_velocity -= 0.1

    if (player_hurtbox.colliderect(ghost_hurtbox) or player_hurtbox.colliderect(arm_tip_rect)) and damage_cooldown <= 0:
        health -= 1
        damage_cooldown = 800
        points -= 100
    damage_cooldown -= 1

def Skeleton_arm_ai():
    global skeleton_arm_x, skeleton_arm_y, skeleton_arm_end_x, skeleton_arm_end_y, player_x, player_y, health, skeleton_arm_damage_cooldown, arm_hit_cooldown, arm_tip_rect

    if room == 6:
        arm_tip_rect = pygame.Rect(skeleton_arm_end_x - 10, skeleton_arm_end_y - 10, 20, 20)
        dx = (player_x + 50) - skeleton_arm_x
        dy = (player_y + 50) - skeleton_arm_y
        distance = math.hypot(dx, dy)
        speed = 2

        if distance > 0:
            move_x = (dx / distance) * min(speed, distance)
            move_y = (dy / distance) * min(speed, distance)
            skeleton_arm_x += move_x
            skeleton_arm_y += move_y

        dx = (player_x + player_side_length // 2) - skeleton_arm_x
        dy = (player_y + player_side_length // 2) - skeleton_arm_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1

        arm_length = 200
        skeleton_arm_end_x = skeleton_arm_x + (dx / distance) * arm_length
        skeleton_arm_end_y = skeleton_arm_y + (dy / distance) * arm_length

        pygame.draw.line(screen, (200, 200, 200), (skeleton_arm_x, skeleton_arm_y), (skeleton_arm_end_x, skeleton_arm_end_y), 20)

        player_center = (player_x + player_side_length // 2, player_y + player_side_length // 2)
        x1, y1 = skeleton_arm_x, skeleton_arm_y
        x2, y2 = skeleton_arm_end_x, skeleton_arm_end_y
        px, py = player_center

        line_mag = math.hypot(x2 - x1, y2 - y1)
        if line_mag == 0:
            line_mag = 1
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
        u = max(0, min(1, u))
        closest_x = x1 + u * (x2 - x1)
        closest_y = y1 + u * (y2 - y1)
        dist_to_line = math.hypot(px - closest_x, py - closest_y)

        arm_thickness = 20

        if dist_to_line < (arm_thickness // 2 + player_side_length // 2) and skeleton_arm_damage_cooldown <= 0:
            health -= 1
            skeleton_arm_damage_cooldown = 800
            arm_hit_cooldown = 800
            skeleton_arm_x, skeleton_arm_y = 1150, 75
        elif dist_to_line < (arm_thickness // 2 + player_side_length // 2):
            skeleton_arm_x, skeleton_arm_y = 1150, 75            

        if skeleton_arm_damage_cooldown > 0:
            skeleton_arm_damage_cooldown -= 1
        if arm_hit_cooldown > 0:
            arm_hit_cooldown -= 1
    else:
        skeleton_arm_x, skeleton_arm_y = 1150, 75
        arm_tip_rect = pygame.Rect(0, 0, 0, 0)

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
    elif room == 6:
        screen.blit(pygame.transform.scale(Skeleton_scaffolding, (1024, 768)), (750, 215))
        screen.blit(GraveStone, (200, 700))
        pygame.draw.rect(screen, (255, 0, 0), (1150, 75, 200, 250))
    elif room == 9:
        screen.blit(pygame.transform.rotate(GraveStone, 90), (150, 650))
    elif room == 10:
        screen.blit(pygame.transform.flip(Resized_tree, 180, 0), (384, 50))
        screen.blit(Resized_tree, (1152, 50))

def ghost_ai():
    global ghost_hurtbox, ghost_x, ghost_y, ghost_direction, ghost_alive, Ghost_respawn_timer, ghost_lowering, ghost_lowering_progress, ghost_rising, ghost_rising_progress, ghost_respawn_y, points, room, health, perma_points, Lives

    if (room == 3 or room == 9) and ghost_alive:
        ghost_hurtbox = pygame.Rect(ghost_x + 32, ghost_y + 32, 120, 136)
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
    
    elif room == 9:
        if ghost_alive:
            if ghost_direction == "right":
                ghost_x += 1
                screen.blit(ghost_sprites[0], (ghost_x, ghost_y))
                if ghost_x >= 1330:
                    ghost_direction = "left"
            else:
                ghost_x -= 1
                screen.blit(ghost_sprites[1], (ghost_x, ghost_y))
                if ghost_x <= 620:
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
            perma_points += 150
            if perma_points >= 1000:
                perma_points -= 1000
                Lives += 1
            if not health == 6:
                health += 1
    else:
        if Ghost_respawn_timer <= 0 and not ghost_rising and not ghost_lowering:
            ghost_rising = True
            ghost_rising_progress = 0
            if room == 3:
                ghost_respawn_y = 720
            elif room == 9:
                ghost_respawn_y = 575
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
    global room, player_x, player_y, ghost_respawn_y, ghost_y
    if player_x + 50 >= 1920:
        room += 1
        player_x = 0
        if room == 3:
            ghost_respawn_y = 720
            ghost_y = ghost_respawn_y
        elif room == 9:
            ghost_respawn_y = 575
            ghost_y = ghost_respawn_y
    if player_x + 50 <= 0:
        room -= 1
        player_x = 1820
        if room == 3:
            ghost_respawn_y = 720
            ghost_y = ghost_respawn_y
        elif room == 9:
            ghost_respawn_y = 575
            ghost_y = ghost_respawn_y

def sky():
    global room, day
    if room in (1, 2, 4, 5, 7, 8, 10):
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
    out_of_lives = font.render("Out of lives...", True, (255, 255, 255))
    if Lives > 0:
        if cooldown > 0:
            timer_text = font.render(f"Wait {cooldown // 1000 + 1} seconds...", True, (255, 100, 100))
            screen.blit(timer_text, (screen.get_width() // 2 - timer_text.get_width() // 2, 600))
        else:
            screen.blit(info_text, (screen.get_width() // 2 - info_text.get_width() // 2, 500))
    else:
        screen.blit(out_of_lives, (screen.get_width() // 2 - out_of_lives.get_width() // 2, 500))
    screen.blit(end_text, (screen.get_width() // 2 - end_text.get_width() // 2, 400))
    screen.blit(font.render(f"Points: {points}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Lives: {Lives}", True, (255, 255, 255)), (1700, 20))
    pygame.display.flip()

def reset_game():
    global health, points, player_x, player_y, player_y_velocity, room, ghost_x, ghost_y, ghost_direction, ghost_alive, Ghost_respawn_timer, ghost_lowering, ghost_lowering_progress, ghost_rising, ghost_rising_progress, ghost_respawn_y, damage_cooldown, skeleton_arm_end_x, skeleton_arm_end_y, skeleton_arm_damage_cooldown
    health = 6
    points -= 500
    player_x, player_y, player_y_velocity = 200, 50, 0
    if room < 4:
        room = 1
    elif room >= 4 and room < 8:
        room = 4
    elif room >= 8:
        room = 8
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
    skeleton_arm_end_x, skeleton_arm_end_y = skeleton_arm_x, skeleton_arm_y
    skeleton_arm_damage_cooldown = 0

def draw():
    sky()
    decorations()
    if damage_cooldown > 0 or arm_hit_cooldown > 0:
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
        screen.blit(font.render(f"Lives: {Lives}", True, (0, 0, 0)), (1700, 20))
    else:
        screen.blit(font.render(f"Points: {points}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Lives: {Lives}", True, (255, 255, 255)), (1700, 20))
    health_bar()
    ghost_ai()
    Skeleton_arm_ai()
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
            Lives -= 1
    else:
        if end_screen_cooldown > 0:
            elapsed = pygame.time.get_ticks() - cooldown_start_time
            end_screen_cooldown = max(0, 5000 - elapsed)
        end_screen(end_screen_cooldown)
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and end_screen_cooldown == 0 and Lives > 0:
                reset_game()
                game_over = False
            elif Lives == 0:
                break

    clock.tick(175)

pygame.quit()
sys.exit()