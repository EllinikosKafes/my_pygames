# updated_game_with_restart.py
import pygame
from pygame.locals import *
import math
import random
import os

# ------- CONFIG -------
GAME_DURATION_MS = 90000  # 90 seconds
WIDTH, HEIGHT = 1280, 720

# ------- init -------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Defence (updated)")
clock = pygame.time.Clock()

# ------- background music -------
bg_music_path = "resources/audio/moonlight.wav"
if os.path.isfile(bg_music_path):
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.play(-1)  # loop forever
    pygame.mixer.music.set_volume(0.5)  # optional volume


# ------- helper resource loader (non-fatal for sounds) -------
def load_image(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing image: {path}")
    return pygame.image.load(path).convert_alpha()

def load_sound(path):
    if not os.path.isfile(path):
        return None
    return pygame.mixer.Sound(path)

# ------- load images (will raise if missing) -------
player = load_image("resources/images/dude.png")
grass = load_image("resources/images/grass.png")
castle = load_image("resources/images/castle.png")
arrow_img = load_image("resources/images/bullet.png")
badguyimg = load_image("resources/images/badguy.png")
healthbar = load_image("resources/images/healthbar.png")
health = load_image("resources/images/health.png")
gameover = load_image("resources/images/gameover.png")
# youwin may not exist in original; try to load but don't crash if missing
try:
    youwin = load_image("resources/images/youwin.png")
except FileNotFoundError:
    youwin = gameover  # fallback

# ------- optional sounds (won't crash if missing) -------
shoot = load_sound("resources/audio/shoot.wav")
enemy_snd = load_sound("resources/audio/enemy.wav")
hit_snd = load_sound("resources/audio/hit.wav")

# ------- game reset function -------
def reset_game():
    state = {}
    state["keys"] = [False, False, False, False]  # W A S D
    state["playerpos"] = [100, 100]
    state["acc"] = [0, 0]  # hits, shots
    state["arrows"] = []
    state["badtimer"] = 100
    state["badtimer1"] = 0
    state["badguys"] = [[1280, 100]]
    state["healthvalue"] = 194
    state["running"] = True
    state["exitcode"] = 0
    state["start_ticks"] = pygame.time.get_ticks()
    return state

state = reset_game()

# restart button rectangle (centered)
BTN_W, BTN_H = 220, 64
btn_rect = pygame.Rect((WIDTH//2 - BTN_W//2, HEIGHT//2 + 80, BTN_W, BTN_H))
font_small = pygame.font.Font(None, 24)
font_big = pygame.font.Font(None, 36)

# ------- main loop -------
while True:
    clock.tick(60)

    if state["running"]:
        # update timers
        state["badtimer"] -= 1

        # --- drawing background ---
        screen.fill((0, 0, 0))
        gw, gh = grass.get_width(), grass.get_height()
        for x in range(int(WIDTH / gw) + 1):
            for y in range(int(HEIGHT / gh) + 1):
                screen.blit(grass, (x * gw, y * gh))

        # castles
        screen.blit(castle, (0, 30))
        screen.blit(castle, (0, 135))
        screen.blit(castle, (0, 240))
        screen.blit(castle, (0, 345))

        # --- player rotation and draw ---
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(mouse_pos[1] - (state["playerpos"][1] + 32),
                           mouse_pos[0] - (state["playerpos"][0] + 26))
        playerrot = pygame.transform.rotate(player, 360 - angle * 57.29)
        playerpos1 = (state["playerpos"][0] - playerrot.get_rect().width / 2,
                      state["playerpos"][1] - playerrot.get_rect().height / 2)
        screen.blit(playerrot, playerpos1)

        # --- update arrows (iterate on copy for safe removals) ---
        for bullet in state["arrows"][:]:
            velx = math.cos(bullet[0]) * 10
            vely = math.sin(bullet[0]) * 10
            bullet[1] += velx
            bullet[2] += vely
            # correct bounds using window size
            if bullet[1] < -64 or bullet[1] > WIDTH + 64 or bullet[2] < -64 or bullet[2] > HEIGHT + 64:
                if bullet in state["arrows"]:
                    state["arrows"].remove(bullet)

        for projectile in state["arrows"]:
            arrow_rot = pygame.transform.rotate(arrow_img, 360 - projectile[0] * 57.29)
            rect = arrow_rot.get_rect(center=(projectile[1], projectile[2]))
            screen.blit(arrow_rot, rect.topleft)

        # --- spawn bad guys ---
        if state["badtimer"] <= 0:
            state["badguys"].append([1280, random.randint(50, 430)])
            state["badtimer"] = 100 - (state["badtimer1"] * 2)
            if state["badtimer1"] >= 35:
                state["badtimer1"] = 35
            else:
                state["badtimer1"] += 5

        # --- move bad guys and collisions ---
        for badguy in state["badguys"][:]:
            badguy[0] -= 2
            # off-screen removal
            if badguy[0] < -64:
                if badguy in state["badguys"]:
                    state["badguys"].remove(badguy)
                continue

            # attack castle
            badrect = badguyimg.get_rect(topleft=(badguy[0], badguy[1]))
            if badrect.left < 64:
                if hit_snd:
                    hit_snd.play()
                state["healthvalue"] -= random.randint(5, 20)
                if badguy in state["badguys"]:
                    state["badguys"].remove(badguy)
                continue

            # check collisions with arrows
            for bullet in state["arrows"][:]:
                bullrect = arrow_img.get_rect(center=(bullet[1], bullet[2]))
                if badrect.colliderect(bullrect):
                    if enemy_snd:
                        enemy_snd.play()
                    state["acc"][0] += 1
                    if badguy in state["badguys"]:
                        state["badguys"].remove(badguy)
                    if bullet in state["arrows"]:
                        state["arrows"].remove(bullet)
                    break

        # draw bad guys
        for badguy in state["badguys"]:
            screen.blit(badguyimg, badguy)

        # --- draw clock (remaining) ---
        elapsed = pygame.time.get_ticks() - state["start_ticks"]
        remaining = max(0, GAME_DURATION_MS - elapsed)
        minutes = remaining // 60000
        seconds = (remaining // 1000) % 60
        survivedtext = font_small.render(f"{minutes}:{str(seconds).zfill(2)}", True, (0, 0, 0))
        textRect = survivedtext.get_rect(topright=(635, 5))
        screen.blit(survivedtext, textRect)

        # --- draw health ---
        screen.blit(healthbar, (5, 5))
        hv = max(0, min(state["healthvalue"], 200))
        for i in range(hv):
            screen.blit(health, (i + 8, 8))

        # --- update display ---
        pygame.display.flip()

        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == K_w:
                    state["keys"][0] = True
                elif event.key == K_a:
                    state["keys"][1] = True
                elif event.key == K_s:
                    state["keys"][2] = True
                elif event.key == K_d:
                    state["keys"][3] = True
                elif event.key == K_r and not state["running"]:
                    # allow R to restart from end screen as well (if needed)
                    state = reset_game()

            if event.type == pygame.KEYUP:
                if event.key == K_w:
                    state["keys"][0] = False
                elif event.key == K_a:
                    state["keys"][1] = False
                elif event.key == K_s:
                    state["keys"][2] = False
                elif event.key == K_d:
                    state["keys"][3] = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # left click shoots
                if event.button == 1:
                    if shoot:
                        shoot.play()
                    pos = pygame.mouse.get_pos()
                    state["acc"][1] += 1
                    state["arrows"].append([
                        math.atan2(pos[1] - (playerpos1[1] + 32), pos[0] - (playerpos1[0] + 26)),
                        playerpos1[0] + 32,
                        playerpos1[1] + 32
                    ])

        # --- move player (allow diagonals) ---
        if state["keys"][0]:
            state["playerpos"][1] -= 5
        if state["keys"][2]:
            state["playerpos"][1] += 5
        if state["keys"][1]:
            state["playerpos"][0] -= 5
        if state["keys"][3]:
            state["playerpos"][0] += 5

        # keep player inside screen (barrier)
        p_w, p_h = player.get_width(), player.get_height()
        state["playerpos"][0] = max(0, min(state["playerpos"][0], WIDTH - p_w))
        state["playerpos"][1] = max(0, min(state["playerpos"][1], HEIGHT - p_h))

        # --- win/lose checks ---
        if elapsed >= GAME_DURATION_MS:
            state["running"] = False
            state["exitcode"] = 1
        if state["healthvalue"] <= 0:
            state["running"] = False
            state["exitcode"] = 0

    else:
        # --- end screen (running == False) ---
        # compute accuracy
        shots = state["acc"][1]
        hits = state["acc"][0]
        accuracy = (hits / shots * 100) if shots != 0 else 0.0

        # draw end background & message
      
        if state["exitcode"] == 0:
            screen.fill((255, 0, 0))  # full red background
            color = (0, 0, 0)
            screen.blit(gameover, (0, 0))  # optional image overlay
        else:
            screen.fill((0, 255, 0))  # full green background
            color = (0, 0, 0)
            screen.blit(youwin, (0, 0))  # optional image overlay


        # accuracy text
        text = font_big.render(f"Accuracy: {accuracy:.2f}%", True, color)
        tr = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 24))
        screen.blit(text, tr)

        # draw restart button
        pygame.draw.rect(screen, (200, 200, 200), btn_rect)
        pygame.draw.rect(screen, (0, 0, 0), btn_rect, 2)
        btext = font_big.render("Restart (R / Click)", True, (0, 0, 0))
        btr = btext.get_rect(center=btn_rect.center)
        screen.blit(btext, btr)

        pygame.display.flip()

        # handle events on end screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == K_r:
                    state = reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and btn_rect.collidepoint(event.pos):
                    state = reset_game()

