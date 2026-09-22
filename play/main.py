import pygame
import random
import sys
import math
import os
import asyncio

def get_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

async def main():
    pygame.init()

    WIDTH, HEIGHT = 321, 480
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Merge Pro")
    clock = pygame.time.Clock()
    


    font_path = get_path("scripts/imperial_one/Webfont/Imperial Web.ttf")
    
    def get_font(size):
        try:
            return pygame.font.Font(font_path, size)
        except:
            return pygame.font.SysFont("Arial", size, bold=True)

    ui_font = get_font(28)     
    score_font = get_font(22) 
    
    GAME_PLAY = 0
    GAME_MENU = 1
    state = GAME_PLAY
    score = 0

    def load_img(path, w, h):
        try:
            full_path = get_path(path)
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(surf, (random.randint(150, 255), 50, 50), (w//2, h//2), min(w, h)//2)
            return surf

    FRUIT_DATA = {
        0: (40, 39, 18, 1), 1: (35, 50, 16, 2), 2: (57, 65, 26, 5), 
        3: (50, 70, 24, 8), 4: (55, 71, 25, 12), 5: (60, 80, 28, 20), 
        6: (60, 69, 28, 35), 7: (80, 80, 36, 60)
    }

    imgs = [
        load_img("fukt.png", 40, 39), load_img("strawdery.png", 35, 50),
        load_img("apple.png", 57, 65), load_img("dradon.png", 40, 62),
        load_img("grape.png", 55, 71), load_img("pai.png", 60, 80),
        load_img("cherry.png", 60, 69), load_img("watermelon.png", 60, 60),
    ]
    map_img = load_img("map.png", WIDTH, HEIGHT)

    dropped_fruits = []
    gravity, air_f, ground_f, elastic = 0.4, 0.96, 0.8, 0.15
    current_type = random.randint(0, 1)
    s_x, s_y, is_falling, v_y = WIDTH // 2, 50, False, 0

    def draw_btn(text, x, y, w, h, base_c, hover_c):
        m_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]
        rect = pygame.Rect(x, y, w, h)
        color = hover_c if rect.collidepoint(m_pos) else base_c
        
        pygame.draw.rect(screen, color, rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=12)
        
        txt = ui_font.render(text, True, (255, 255, 255))
        screen.blit(txt, (x + (w - txt.get_width())//2, y + (h - txt.get_height())//2))
        return rect.collidepoint(m_pos) and clicked

    while True:
        screen.blit(map_img, (0, 0))
        
        if state == GAME_PLAY:
            mouse_x = pygame.mouse.get_pos()[0]
            curr_w, curr_h, curr_r, curr_m = FRUIT_DATA[current_type]

            if not is_falling:
                s_x = max(curr_r, min(mouse_x, WIDTH - curr_r))
                pygame.draw.line(screen, (255, 255, 255, 100), (s_x, s_y), (s_x, HEIGHT), 1)
                screen.blit(imgs[current_type], (s_x - curr_w/2, s_y - curr_h/2))
            else:
                v_y += gravity
                s_y += v_y
                hit = any(math.hypot(s_x - f['x'], s_y - f['y']) < curr_r + f['r'] for f in dropped_fruits)
                if s_y >= HEIGHT - curr_r or hit:
                    if s_y > HEIGHT - curr_r: s_y = HEIGHT - curr_r
                    dropped_fruits.append({'type': current_type, 'x': s_x, 'y': s_y, 'r': curr_r, 'm': curr_m, 'vx': 0, 'vy': v_y * 0.3})
                    current_type, is_falling, v_y, s_y = random.randint(0, 1), False, 0, 50
                else:
                    screen.blit(imgs[current_type], (s_x - curr_w/2, s_y - curr_h/2))

            for _ in range(8):
                for i, f1 in enumerate(dropped_fruits):
                    if f1['y'] < HEIGHT - f1['r']: f1['vy'] += gravity / 8
                    f_eff = ground_f if f1['y'] >= HEIGHT - f1['r'] - 1 else air_f
                    f1['vx'] *= f_eff**(1/8); f1['vy'] *= air_f**(1/8)
                    f1['x'] += f1['vx']/8; f1['y'] += f1['vy']/8
                    if f1['y'] > HEIGHT - f1['r']: f1['y'], f1['vy'] = HEIGHT - f1['r'], 0
                    if f1['x'] < f1['r']: f1['x'], f1['vx'] = f1['r'], f1['vx'] * -0.2
                    elif f1['x'] > WIDTH - f1['r']: f1['x'], f1['vx'] = WIDTH - f1['r'], f1['vx'] * -0.2

                    for j in range(i + 1, len(dropped_fruits)):
                        f2 = dropped_fruits[j]
                        dx, dy = f2['x'] - f1['x'], f2['y'] - f1['y']
                        dist = math.hypot(dx, dy)
                        if dist < f1['r'] + f2['r']:
                            if dist == 0: dist = 0.1
                            nx, ny = dx/dist, dy/dist
                            overlap = (f1['r'] + f2['r']) - dist
                            mt = f1['m'] + f2['m']
                            f1['x'] -= nx * overlap * (f2['m']/mt); f1['y'] -= ny * overlap * (f2['m']/mt)
                            f2['x'] += nx * overlap * (f1['m']/mt); f2['y'] += ny * overlap * (f1['m']/mt)
                            rvx, rvy = f2['vx'] - f1['vx'], f2['vy'] - f1['vy']
                            if rvx*nx + rvy*ny < 0:
                                imp = -(1 + elastic) * (rvx*nx + rvy*ny) / (1/f1['m'] + 1/f2['m'])
                                f1['vx'] -= (imp/f1['m'])*nx; f1['vy'] -= (imp/f1['m'])*ny
                                f2['vx'] += (imp/f2['m'])*nx; f2['vy'] += (imp/f2['m'])*ny

            to_rem = set()
            for i in range(len(dropped_fruits)):
                for j in range(i + 1, len(dropped_fruits)):
                    f1, f2 = dropped_fruits[i], dropped_fruits[j]
                    if f1['type'] == f2['type'] and f1['type'] < 7:
                        if math.hypot(f1['x']-f2['x'], f1['y']-f2['y']) < (f1['r']+f2['r'])*1.05:
                            to_rem.update([i, j])
                            nt = f1['type'] + 1
                            score += (nt * 10)
                            dropped_fruits.append({'type': nt, 'x': (f1['x']+f2['x'])/2, 'y': (f1['y']+f2['y'])/2, 'r': FRUIT_DATA[nt][2], 'm': FRUIT_DATA[nt][3], 'vx': 0, 'vy': 0})
                            break
                if to_rem: break
            dropped_fruits = [f for idx, f in enumerate(dropped_fruits) if idx not in to_rem]

            for f in dropped_fruits:
                screen.blit(imgs[f['type']], (f['x'] - FRUIT_DATA[f['type']][0]/2, f['y'] - FRUIT_DATA[f['type']][1]/2))

            score_shadow = score_font.render(f"SCORE: {score}", True, (40, 40, 40))
            score_text = score_font.render(f"SCORE: {score}", True, (255, 220, 50))
            screen.blit(score_shadow, (2, 52))
            screen.blit(score_text, (0, 50))

        elif state == GAME_MENU:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            if draw_btn("RESUME", 85, 160, 150, 50, (40, 120, 40), (60, 170, 60)): state = GAME_PLAY
            if draw_btn("RESTART", 85, 230, 150, 50, (120, 80, 30), (170, 110, 40)): 
                dropped_fruits, is_falling, s_y, state, score = [], False, 50, GAME_PLAY, 0
            if draw_btn("EXIT", 85, 300, 150, 50, (120, 30, 30), (170, 50, 50)): pygame.quit(); sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = GAME_MENU if state == GAME_PLAY else GAME_PLAY
            if event.type == pygame.MOUSEBUTTONDOWN and state == GAME_PLAY: is_falling = True

        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(60)

asyncio.run(main())