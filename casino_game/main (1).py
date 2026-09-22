import pygame, pygame.gfxdraw, random, sys, math, os

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Royal Casino")
clock = pygame.time.Clock()

# ---------------------------------------------------------------- fonts ----
title_font = pygame.font.SysFont("georgia", 64, bold=True)
big_font   = pygame.font.SysFont("georgia", 40, bold=True)
font       = pygame.font.SysFont("arial", 26, bold=True)
small      = pygame.font.SysFont("arial", 20, bold=True)
tiny       = pygame.font.SysFont("arial", 15, bold=True)
micro      = pygame.font.SysFont("arial", 12, bold=True)

# --------------------------------------------------------------- colors ----
WINE       = (32, 8, 12)
WINE_DARK  = (18, 4, 7)
GOLD       = (212, 175, 55)
GOLD_LIGHT = (247, 226, 150)
GOLD_DARK  = (140, 108, 30)
FELT       = (10, 70, 40)
FELT_DARK  = (6, 45, 25)
CREAM      = (240, 230, 210)
RED        = (188, 30, 34)
BLACK_C    = (25, 25, 28)
WHITE      = (250, 250, 250)
BLUE       = (40, 70, 150)
STEEL      = (120, 120, 130)


def lighten(c, amt):
    return tuple(min(255, int(v + amt)) for v in c)


def darken(c, amt):
    return tuple(max(0, int(v - amt)) for v in c)


# ---------------------------------------------------------- misc globals ---
anim_state = {}
frame_tick = 0


def anim_update(key, hovered, pressed, hspeed=0.25, pspeed=0.4):
    a = anim_state.setdefault(key, {"h": 0.0, "p": 0.0})
    a["h"] += ((1.0 if hovered else 0.0) - a["h"]) * hspeed
    a["p"] += ((1.0 if pressed else 0.0) - a["p"]) * pspeed
    return a["h"], a["p"]


def overlay_dark(alpha=165):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    screen.blit(ov, (0, 0))


# ------------------------------------------------------- smoothing helper -
def rounded_rect_aa(size, fill, radius, border_color=None, border_w=0, ss=3):
    """Draws a rounded rect supersampled then downscaled for anti-aliased edges."""
    w, h = size
    w = max(1, w); h = max(1, h)
    temp = pygame.Surface((w * ss, h * ss), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, w * ss, h * ss)
    r = max(1, int(radius * ss))
    if fill is not None:
        pygame.draw.rect(temp, fill, rect, border_radius=r)
    if border_color is not None and border_w > 0:
        pygame.draw.rect(temp, border_color, rect, width=max(1, border_w * ss), border_radius=r)
    return pygame.transform.smoothscale(temp, (w, h))


# ------------------------------------------------------- button graphics ---
def draw_volumetric(surf, rect, base_color, radius, hover_t, press_t, enabled=True):
    if rect.w <= 0 or rect.h <= 0:
        return
    shadow = rect.move(0, 6)
    pygame.draw.rect(surf, WINE_DARK, shadow, border_radius=radius)
    ss = 3
    w, h = rect.w, rect.h
    temp = pygame.Surface((w * ss, h * ss), pygame.SRCALPHA)
    trect = pygame.Rect(0, 0, w * ss, h * ss)
    r = max(1, radius * ss)
    fill = lighten(base_color, int(18 * hover_t)) if enabled else (110, 110, 110)
    pygame.draw.rect(temp, fill, trect, border_radius=r)
    light = lighten(base_color, 95) if enabled else (170, 170, 170)
    dark = darken(base_color, 70) if enabled else (60, 60, 60)
    if trect.w > 2 * r and trect.h > 2 * r:
        lw = 3 * ss
        pygame.draw.line(temp, light, (trect.left + r, trect.top + 2 * ss), (trect.right - r, trect.top + 2 * ss), lw)
        pygame.draw.line(temp, light, (trect.left + 2 * ss, trect.top + r), (trect.left + 2 * ss, trect.bottom - r), lw)
        pygame.draw.line(temp, dark, (trect.left + r, trect.bottom - 2 * ss), (trect.right - r, trect.bottom - 2 * ss), lw)
        pygame.draw.line(temp, dark, (trect.right - 2 * ss, trect.top + r), (trect.right - 2 * ss, trect.bottom - r), lw)
    pygame.draw.rect(temp, darken(base_color, 30) if enabled else (80, 80, 80), trect, width=2 * ss, border_radius=r)
    scaled = pygame.transform.smoothscale(temp, (w, h))
    surf.blit(scaled, rect.topleft)
    if hover_t > 0.05 and enabled:
        pygame.draw.rect(surf, GOLD_LIGHT, rect.inflate(6, 6), width=2, border_radius=radius + 3)


def draw_button(surf, rect, text, key, color=GOLD, txt_color=WINE, fnt=None, enabled=True, radius=14):
    fnt = fnt or font
    mp = pygame.mouse.get_pos()
    hovered = enabled and rect.collidepoint(mp)
    pressed = hovered and pygame.mouse.get_pressed()[0]
    hov, pr = anim_update(key, hovered, pressed)
    grow = int(3 * hov) - int(4 * pr)
    r = rect.inflate(grow, grow)
    r.y += int(3 * pr)
    draw_volumetric(surf, r, color, radius, hov, pr, enabled)
    lines = text.split("\n")
    lh = fnt.get_height()
    start_y = r.centery - (len(lines) * lh) // 2 + lh // 2
    for i, ln in enumerate(lines):
        lbl = fnt.render(ln, True, txt_color if enabled else (120, 120, 120))
        surf.blit(lbl, lbl.get_rect(center=(r.centerx, start_y + i * lh)))
    return rect


def draw_panel(surf, rect, color=FELT, radius=18, border=GOLD):
    if rect.w <= 0 or rect.h <= 0:
        return
    shadow = rect.move(0, 8)
    pygame.draw.rect(surf, WINE_DARK, shadow, border_radius=radius)
    ss = 2
    w, h = rect.w, rect.h
    temp = pygame.Surface((w * ss, h * ss), pygame.SRCALPHA)
    trect = pygame.Rect(0, 0, w * ss, h * ss)
    r = max(1, radius * ss)
    pygame.draw.rect(temp, color, trect, border_radius=r)
    pygame.draw.rect(temp, darken(color, 35), trect, width=6 * ss, border_radius=r)
    pygame.draw.rect(temp, border, trect, width=3 * ss, border_radius=r)
    scaled = pygame.transform.smoothscale(temp, (w, h))
    surf.blit(scaled, rect.topleft)


# --------------------------------------------------------------- background
def draw_bg():
    screen.fill(WINE)
    for row in range(0, HEIGHT, 40):
        offset = 20 if (row // 40) % 2 else 0
        for col in range(-20, WIDTH + 20, 40):
            pygame.gfxdraw.filled_circle(screen, col + offset, row + 20, 3, (62, 24, 26))
    pygame.draw.rect(screen, GOLD_DARK, (0, 0, WIDTH, HEIGHT), width=14)
    pygame.draw.rect(screen, GOLD, (10, 10, WIDTH - 20, HEIGHT - 20), width=4)
    for cx, cy in [(24, 24), (WIDTH - 24, 24), (24, HEIGHT - 24), (WIDTH - 24, HEIGHT - 24)]:
        pygame.gfxdraw.filled_circle(screen, cx, cy, 10, GOLD)
        pygame.gfxdraw.aacircle(screen, cx, cy, 10, GOLD_LIGHT)


def draw_balance_badge():
    rect = pygame.Rect(WIDTH - 230, 18, 210, 54)
    draw_panel(screen, rect, color=(50, 15, 20), radius=14, border=GOLD)
    lbl = small.render(f"Баланс: {balance}$", True, GOLD_LIGHT)
    screen.blit(lbl, lbl.get_rect(center=rect.center))


def draw_header(title_text):
    lbl = big_font.render(title_text, True, GOLD)
    screen.blit(lbl, lbl.get_rect(center=(WIDTH // 2, 55)))
    draw_balance_badge()


# ----------------------------------------------------------- glossy shape --
def draw_glossy_circle(surf, cx, cy, r, color):
    pygame.gfxdraw.filled_circle(surf, cx + 2, cy + 3, r, darken(color, 60))
    pygame.gfxdraw.filled_circle(surf, cx, cy, r, color)
    pygame.gfxdraw.aacircle(surf, cx, cy, r, lighten(color, 40))
    pygame.gfxdraw.aacircle(surf, cx, cy, r - 1, lighten(color, 40))
    hl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 120), (r // 4, r // 6, r, int(r * 0.6)))
    surf.blit(hl, (cx - r, cy - r))


# ------------------------------------------------------------- slot icons --
def draw_cherry(surf, cx, cy, size, color=(190, 20, 30)):
    r = size // 4
    draw_glossy_circle(surf, cx - r, cy + r, r, color)
    draw_glossy_circle(surf, cx + r, cy + r, r, color)
    pygame.draw.line(surf, (50, 130, 50), (cx - r, cy), (cx, cy - size // 2), 3)
    pygame.draw.line(surf, (50, 130, 50), (cx + r, cy), (cx, cy - size // 2), 3)
    leaf = [(cx, cy - size // 2), (cx + size // 5, cy - size // 2 - 8), (cx + 2, cy - size // 2 + 6)]
    pygame.gfxdraw.filled_polygon(surf, leaf, (70, 160, 70))
    pygame.gfxdraw.aapolygon(surf, leaf, (70, 160, 70))


def draw_star(surf, cx, cy, size, color=GOLD):
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rad = size // 2 if i % 2 == 0 else size // 4
        pts.append((cx + rad * math.cos(ang), cy - rad * math.sin(ang)))
    shadow_pts = [(x + 3, y + 4) for x, y in pts]
    pygame.gfxdraw.filled_polygon(surf, shadow_pts, darken(color, 60))
    pygame.gfxdraw.filled_polygon(surf, pts, color)
    pygame.gfxdraw.aapolygon(surf, pts, lighten(color, 70))


def draw_bell(surf, cx, cy, size, color=(230, 190, 60)):
    body = pygame.Rect(cx - size // 3, cy - size // 3, 2 * size // 3, size // 2)
    pygame.draw.ellipse(surf, darken(color, 40), body.move(2, 3))
    pygame.draw.ellipse(surf, color, body)
    pygame.draw.rect(surf, color, (cx - size // 2, cy + size // 8, size, size // 8), border_radius=6)
    pygame.gfxdraw.filled_circle(surf, cx, cy + size // 4 + size // 8, size // 14, darken(color, 30))
    pygame.draw.rect(surf, darken(color, 20), (cx - 4, cy - size // 2, 8, size // 8))


def draw_seven(surf, cx, cy, size, color=(230, 50, 50)):
    txt = big_font.render("7", True, color)
    shadow = big_font.render("7", True, darken(color, 90))
    surf.blit(shadow, shadow.get_rect(center=(cx + 2, cy + 3)))
    surf.blit(txt, txt.get_rect(center=(cx, cy)))


SYMBOLS = [("cherry", draw_cherry, 2), ("bell", draw_bell, 4), ("star", draw_star, 6), ("seven", draw_seven, 10)]

# -------------------------------------------------------------- card deck --
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = [("\u2660", BLACK_C), ("\u2665", RED), ("\u2666", RED), ("\u2663", BLACK_C)]
RANK_VAL = {"A": 14, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13}


def make_deck():
    deck = [(r, sym, col) for r in RANKS for sym, col in SUITS]
    random.shuffle(deck)
    return deck


def card_value(rank):
    if rank in ("J", "Q", "K"):
        return 10
    if rank == "A":
        return 11
    return int(rank)


def hand_value(hand):
    total = sum(card_value(c[0]) for c in hand)
    aces = sum(1 for c in hand if c[0] == "A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def bacc_val(rank):
    if rank in ("J", "Q", "K", "10"):
        return 0
    if rank == "A":
        return 1
    return int(rank)


def bacc_hand_value(hand):
    return sum(bacc_val(c[0]) for c in hand) % 10


def poker3_score(cards):
    vals = sorted([RANK_VAL[c[0]] for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    flush = len(set(suits)) == 1
    is_straight = (vals[0] - vals[1] == 1 and vals[1] - vals[2] == 1)
    if vals == [14, 3, 2]:
        is_straight = True
        vals = [3, 2, 1]
    counts = {}
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
    count_vals = sorted(counts.values(), reverse=True)
    if is_straight and flush:
        return (6, vals)
    elif count_vals[0] == 3:
        return (5, vals)
    elif is_straight:
        return (4, vals)
    elif flush:
        return (3, vals)
    elif count_vals[0] == 2:
        pair_val = [v for v, c in counts.items() if c == 2][0]
        kicker = [v for v, c in counts.items() if c == 1]
        return (2, [pair_val] + kicker)
    else:
        return (1, vals)


POKER_HAND_NAMES = {6: "Стрит-флеш", 5: "Тройка", 4: "Стрит", 3: "Флеш", 2: "Пара", 1: "Старшая карта"}


def draw_card(surf, x, y, card, face_up=True, w=88, h=124):
    rect = pygame.Rect(x, y, w, h)
    shadow = pygame.Rect(x + 4, y + 6, w, h)
    pygame.draw.rect(surf, WINE_DARK, shadow, border_radius=10)
    if face_up:
        rank, sym, color = card
        bg = rounded_rect_aa((w, h), CREAM, 10, (170, 160, 140), 2)
        surf.blit(bg, (x, y))
        rlbl = small.render(rank, True, color)
        surf.blit(rlbl, (x + 8, y + 6))
        slbl = small.render(sym, True, color)
        surf.blit(slbl, (x + 8, y + 28))
        big_sym = big_font.render(sym, True, color)
        surf.blit(big_sym, big_sym.get_rect(center=rect.center))
        rlbl2 = pygame.transform.rotate(rlbl, 180)
        surf.blit(rlbl2, (x + w - rlbl2.get_width() - 8, y + h - rlbl2.get_height() - 6))
        slbl2 = pygame.transform.rotate(slbl, 180)
        surf.blit(slbl2, (x + w - slbl2.get_width() - 8, y + h - slbl2.get_height() - 28))
    else:
        bg = rounded_rect_aa((w, h), (95, 15, 25), 10, GOLD, 3)
        surf.blit(bg, (x, y))
        inner = rect.inflate(-16, -16)
        inner_bg = rounded_rect_aa((inner.w, inner.h), (125, 25, 35), 8)
        surf.blit(inner_bg, (inner.x, inner.y))
        for i in range(4):
            yy = inner.y + i * inner.h // 4
            pygame.draw.line(surf, GOLD_DARK, (inner.x, yy), (inner.x + inner.w, yy), 1)


# ---------------------------------------------------------------- dice ----
PIP_POS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)],
}


def draw_die(surf, cx, cy, size, value, wobble=0.0):
    s = size
    depth = int(s * 0.22)
    pad = depth + 6
    temp = pygame.Surface((s + pad * 2, s + pad * 2), pygame.SRCALPHA)
    ox, oy = pad, pad
    front = pygame.Rect(ox, oy + depth, s, s)
    top_pts = [(ox, oy + depth), (ox + depth, oy), (ox + depth + s, oy), (ox + s, oy + depth)]
    right_pts = [(ox + s, oy + depth), (ox + depth + s, oy), (ox + depth + s, oy + s), (ox + s, oy + depth + s)]
    pygame.gfxdraw.filled_polygon(temp, top_pts, lighten(CREAM, 10))
    pygame.gfxdraw.aapolygon(temp, top_pts, lighten(CREAM, 10))
    pygame.gfxdraw.filled_polygon(temp, right_pts, darken(CREAM, 55))
    pygame.gfxdraw.aapolygon(temp, right_pts, darken(CREAM, 55))
    front_bg = rounded_rect_aa((s, s), CREAM, 8, (120, 110, 90), 2, ss=2)
    temp.blit(front_bg, (front.x, front.y))
    pygame.gfxdraw.aapolygon(temp, top_pts, (120, 110, 90))
    pygame.gfxdraw.aapolygon(temp, right_pts, (120, 110, 90))
    for px, py in PIP_POS[value]:
        cxp = int(front.x + px * front.w)
        cyp = int(front.y + py * front.h)
        rr = max(3, s // 14)
        pygame.gfxdraw.filled_circle(temp, cxp, cyp, rr, (35, 28, 28))
        pygame.gfxdraw.aacircle(temp, cxp, cyp, rr, (35, 28, 28))
    rotated = pygame.transform.rotozoom(temp, wobble, 1.0)
    surf.blit(rotated, rotated.get_rect(center=(cx, cy)))


# ---------------------------------------------------------------- coin ----
def draw_coin_visual(surf, cx, cy, r, flipping, frames, final):
    if flipping:
        # Flips end-over-end around a HORIZONTAL axis: the coin squashes
        # in HEIGHT (not width) as it rotates, like a real coin toss.
        vscale = max(0.10, abs(math.cos(frames * 0.85)))
        hh = max(6, int(r * 2 * vscale))
        rect = pygame.Rect(0, 0, r * 2, hh)
        rect.center = (cx, cy)
        showing_heads = math.cos(frames * 0.85) > 0
        edge_color = GOLD if showing_heads else GOLD_DARK
        pygame.draw.ellipse(surf, darken(edge_color, 30), rect.move(0, 3))
        pygame.draw.ellipse(surf, edge_color, rect)
        pygame.draw.ellipse(surf, GOLD_LIGHT, rect, width=max(1, min(3, hh // 6)))
        if hh > r * 0.9:
            letter = "\u041e" if showing_heads else "\u0420"
            lbl = font.render(letter, True, WINE)
            surf.blit(lbl, lbl.get_rect(center=(cx, cy)))
    else:
        pygame.gfxdraw.filled_circle(surf, cx + 2, cy + 4, r, darken(GOLD, 55))
        pygame.gfxdraw.filled_circle(surf, cx, cy, r, GOLD)
        pygame.gfxdraw.aacircle(surf, cx, cy, r, GOLD_LIGHT)
        pygame.gfxdraw.aacircle(surf, cx, cy, r - 1, GOLD_LIGHT)
        pygame.gfxdraw.aacircle(surf, cx, cy, r - 2, GOLD_LIGHT)
        letter = "\u041e" if final == "heads" else "\u0420"
        lbl = big_font.render(letter, True, WINE)
        surf.blit(lbl, lbl.get_rect(center=(cx, cy)))


# ------------------------------------------------------------- roulette ---
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}


def num_color(n):
    if n == 0:
        return "green"
    return "red" if n in RED_NUMBERS else "black"


def draw_wheel(surf, cx, cy, r, angle_offset, show_numbers=True):
    wedge = 360 / 37
    for i in range(37):
        a1 = math.radians(angle_offset + i * wedge - 90)
        a2 = math.radians(angle_offset + (i + 1) * wedge - 90)
        col = (20, 120, 40) if i == 0 else ((190, 30, 30) if i in RED_NUMBERS else (25, 25, 28))
        pts = [(cx, cy)]
        for s in range(5):
            a = a1 + (a2 - a1) * s / 4
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pygame.gfxdraw.filled_polygon(surf, pts, col)
        pygame.gfxdraw.aapolygon(surf, pts, darken(col, 20))
        if show_numbers:
            mid = angle_offset + (i + 0.5) * wedge - 90
            am = math.radians(mid)
            tx = cx + r * 0.8 * math.cos(am)
            ty = cy + r * 0.8 * math.sin(am)
            lbl = micro.render(str(i), True, WHITE)
            rotated = pygame.transform.rotate(lbl, -(mid + 90))
            surf.blit(rotated, rotated.get_rect(center=(tx, ty)))
    pygame.gfxdraw.aacircle(surf, cx, cy, r, GOLD)
    pygame.gfxdraw.aacircle(surf, cx, cy, r - 1, GOLD)
    pygame.gfxdraw.aacircle(surf, cx, cy, r - 2, GOLD)
    hub_r = max(6, r // 4)
    pygame.gfxdraw.filled_circle(surf, cx, cy, hub_r, GOLD_DARK)
    pygame.gfxdraw.aacircle(surf, cx, cy, hub_r, GOLD)
    pygame.draw.polygon(surf, GOLD, [(cx - 10, cy - r - 16), (cx + 10, cy - r - 16), (cx, cy - r + 6)])


# ======================================================= GAME STATE ========
balance = 1000
state = "menu"          # menu, hub, tutorial, slots, blackjack, roulette, dice, coin, craps, baccarat, poker
current_game = None
paused = False
tutorials_shown = set()
current_rects = {}
dragging_lever = False

GAMES = [
    {"key": "slots", "title": "Слот-машина", "desc": "Крути и выигрывай", "color": (150, 40, 40)},
    {"key": "blackjack", "title": "Блэкджек", "desc": "Наберите 21", "color": (20, 95, 60)},
    {"key": "roulette", "title": "Рулетка", "desc": "Красное или чёрное", "color": (160, 20, 20)},
    {"key": "dice", "title": "Кости", "desc": "Испытай удачу", "color": (40, 60, 140)},
    {"key": "coin", "title": "Монетка", "desc": "Орёл или решка", "color": (150, 120, 20)},
    {"key": "craps", "title": "Крэпс", "desc": "Классика на двух костях", "color": (70, 45, 130)},
    {"key": "baccarat", "title": "Баккара", "desc": "Игрок против банкира", "color": (25, 80, 90)},
    {"key": "poker", "title": "Покер", "desc": "Три карты против дилера", "color": (110, 70, 25)},
]
GAME_TITLES = {g["key"]: g["title"] for g in GAMES}

TUTORIALS = {
    "slots": ["Потяните рычаг или нажмите «Крутить», чтобы запустить барабаны.",
              "Два одинаковых символа — маленький выигрыш.",
              "Три одинаковых символа подряд — ДЖЕКПОТ!"],
    "blackjack": ["Наберите больше очков, чем дилер, но не больше 21.",
                  "«Ещё карту» — взять карту, «Хватит» — остановиться.",
                  "Туз считается за 11 или 1 очко."],
    "roulette": ["Выберите число или цвет и нажмите «Крутить».",
                 "Точное число даёт выигрыш x36.",
                 "Цвет (красное/чёрное) даёт x2."],
    "dice": ["Выберите число от 1 до 6 или чётность.",
             "Нажмите «Бросить», чтобы кубик взлетел и крутился в воздухе.",
             "Точное число — x5, чётность/нечётность — x2."],
    "coin": ["Выберите Орёл или Решка.",
             "Нажмите «Подбросить монету».",
             "Угадали сторону — выигрыш x2."],
    "craps": ["Сделайте ставку и бросьте два кубика — это «выход».",
              "7 или 11 сразу дают победу, 2, 3 или 12 — проигрыш.",
              "Любое другое число становится «точкой»: бросайте снова, пока не выпадет точка (победа) или 7 (проигрыш)."],
    "baccarat": ["Поставьте на Игрока, Банкира или Ничью.",
                 "Каждой стороне раздаётся по 2 карты, считаются только последние цифры суммы очков.",
                 "Ближе к 9 побеждает. Ничья даёт выигрыш x9."],
    "poker": ["Сделайте ставку (анте) и получите 3 карты.",
              "Посмотрите на карты: «Играть» — удвоить ставку, «Сбросить» — потерять анте.",
              "Комбинация сильнее дилерской — выигрыш выплачивается за обе ставки."],
}

# ---- slots state ----
sl_bet = 20
sl_result = [SYMBOLS[0], SYMBOLS[0], SYMBOLS[0]]
sl_display = [SYMBOLS[0], SYMBOLS[0], SYMBOLS[0]]
sl_spinning = False
sl_frames = 0
sl_final = [SYMBOLS[0], SYMBOLS[0], SYMBOLS[0]]
sl_message = ""
sl_lever = 0.0

# ---- blackjack state ----
bj_bet = 20
bj_deck = []
bj_player = []
bj_dealer = []
bj_state = "betting"   # betting, playing, dealer, done
bj_timer = 0
bj_message = ""

# ---- roulette state ----
rl_bet_amount = 20
rl_bet_type = None
rl_spinning = False
rl_frames = 0
rl_angle = 0.0
rl_target = 0.0
rl_final = 0
rl_result = None
rl_message = ""
RL_MAX_FRAMES = 110

# ---- dice state ----
dc_bet = 20
dc_choice = None
dc_spinning = False
dc_frames = 0
dc_final = 1
dc_display = 1
dc_message = ""
dc_y = 0.0
dc_vy = 0.0
dc_rot = 0.0

# ---- coin state ----
cn_bet = 20
cn_choice = None
cn_flipping = False
cn_frames = 0
cn_final = None
cn_y = 0.0
cn_vy = 0.0
cn_message = ""

# ---- craps state ----
cr_bet = 20
cr_state = "betting"    # betting, rolling, point, done
cr_point = None
cr_d1, cr_d2 = 1, 1
cr_final1, cr_final2 = 1, 1
cr_spinning = False
cr_frames = 0
cr_y = 0.0
cr_vy = 0.0
cr_rot = 0.0
cr_message = ""

# ---- baccarat state ----
bc_bet = 20
bc_choice = None
bc_player = []
bc_banker = []
bc_deck = []
bc_state = "betting"    # betting, done
bc_message = ""

# ---- poker (3 card) state ----
pk_bet = 20
pk_deck = []
pk_player = []
pk_dealer = []
pk_state = "betting"    # betting, deciding, done
pk_message = ""


def reset_slots():
    global sl_result, sl_display, sl_spinning, sl_frames, sl_message
    sl_result = [SYMBOLS[0], SYMBOLS[0], SYMBOLS[0]]
    sl_display = list(sl_result)
    sl_spinning = False
    sl_frames = 0
    sl_message = ""


def reset_blackjack():
    global bj_deck, bj_player, bj_dealer, bj_state, bj_timer, bj_message
    bj_deck = make_deck()
    bj_player = []
    bj_dealer = []
    bj_state = "betting"
    bj_timer = 0
    bj_message = ""


def reset_roulette():
    global rl_bet_type, rl_spinning, rl_frames, rl_angle, rl_result, rl_message
    rl_bet_type = None
    rl_spinning = False
    rl_frames = 0
    rl_angle = 0.0
    rl_result = None
    rl_message = ""


def reset_dice():
    global dc_choice, dc_spinning, dc_frames, dc_display, dc_message, dc_y, dc_vy, dc_rot
    dc_choice = None
    dc_spinning = False
    dc_frames = 0
    dc_display = 1
    dc_message = ""
    dc_y = 0.0
    dc_vy = 0.0
    dc_rot = 0.0


def reset_coin():
    global cn_choice, cn_flipping, cn_frames, cn_final, cn_y, cn_vy, cn_message
    cn_choice = None
    cn_flipping = False
    cn_frames = 0
    cn_final = None
    cn_y = 0.0
    cn_vy = 0.0
    cn_message = ""


def reset_craps():
    global cr_state, cr_point, cr_spinning, cr_frames, cr_message, cr_y, cr_vy, cr_rot
    cr_state = "betting"
    cr_point = None
    cr_spinning = False
    cr_frames = 0
    cr_message = ""
    cr_y = 0.0
    cr_vy = 0.0
    cr_rot = 0.0


def reset_baccarat():
    global bc_choice, bc_player, bc_banker, bc_state, bc_message
    bc_choice = None
    bc_player = []
    bc_banker = []
    bc_state = "betting"
    bc_message = ""


def reset_poker():
    global pk_player, pk_dealer, pk_state, pk_message
    pk_player = []
    pk_dealer = []
    pk_state = "betting"
    pk_message = ""


RESETTERS = {"slots": reset_slots, "blackjack": reset_blackjack, "roulette": reset_roulette,
             "dice": reset_dice, "coin": reset_coin, "craps": reset_craps,
             "baccarat": reset_baccarat, "poker": reset_poker}


def enter_game(key):
    global state, current_game
    current_game = key
    if key not in tutorials_shown:
        state = "tutorial"
    else:
        RESETTERS[key]()
        state = key


def confirm_tutorial():
    global state
    tutorials_shown.add(current_game)
    RESETTERS[current_game]()
    state = current_game


# --------------------------------------------------------- slots actions --
def slot_spin():
    global balance, sl_spinning, sl_frames, sl_final, sl_message, sl_lever
    if sl_spinning:
        return
    if balance < sl_bet:
        sl_message = "Недостаточно средств!"
        return
    balance -= sl_bet
    sl_final = [random.choice(SYMBOLS) for _ in range(3)]
    sl_spinning = True
    sl_frames = 0
    sl_message = ""
    sl_lever = 1.0


def update_slots():
    global sl_frames, sl_spinning, sl_result, sl_message, balance, sl_lever, dragging_lever
    if not dragging_lever:
        sl_lever += (0.0 - sl_lever) * 0.12
    if not sl_spinning:
        return
    sl_frames += 1
    stops = [22, 34, 46]
    for i in range(3):
        if sl_frames < stops[i]:
            if sl_frames % 3 == 0:
                sl_display[i] = random.choice(SYMBOLS)
        else:
            sl_display[i] = sl_final[i]
    if sl_frames >= stops[-1] + 6:
        sl_spinning = False
        sl_result[:] = sl_final
        names = [s[0] for s in sl_result]
        if names[0] == names[1] == names[2]:
            win = sl_bet * sl_final[0][2]
            balance += win
            sl_message = f"ДЖЕКПОТ! +{win}$"
        elif names[0] == names[1] or names[1] == names[2] or names[0] == names[2]:
            win = sl_bet
            balance += win
            sl_message = f"Есть пара! +{win}$"
        else:
            sl_message = "Мимо, попробуйте ещё"


# ----------------------------------------------------- blackjack actions --
def bj_finish_natural():
    global bj_state, balance, bj_message
    pv = hand_value(bj_player)
    dv = hand_value(bj_dealer)
    if pv == 21 and dv == 21:
        balance += bj_bet
        bj_message = "Ничья (у обоих блэкджек)"
    elif pv == 21:
        win = int(bj_bet * 2.5)
        balance += win
        bj_message = f"Блэкджек! +{win}$"
    else:
        bj_message = "У дилера блэкджек. Вы проиграли."
    bj_state = "done"


def bj_deal():
    global bj_deck, bj_player, bj_dealer, bj_state, balance, bj_message, bj_timer
    if bj_state not in ("betting", "done"):
        return
    if balance < bj_bet:
        bj_message = "Недостаточно средств!"
        return
    if len(bj_deck) < 15:
        bj_deck = make_deck()
    balance -= bj_bet
    bj_player = [bj_deck.pop(), bj_deck.pop()]
    bj_dealer = [bj_deck.pop(), bj_deck.pop()]
    bj_message = ""
    bj_timer = 0
    if hand_value(bj_player) == 21 or hand_value(bj_dealer) == 21:
        bj_finish_natural()
    else:
        bj_state = "playing"


def bj_hit():
    global bj_state, bj_message
    if bj_state != "playing":
        return
    if not bj_deck:
        bj_deck.extend(make_deck())
    bj_player.append(bj_deck.pop())
    if hand_value(bj_player) > 21:
        bj_state = "done"
        bj_message = "Перебор! Вы проиграли."


def bj_stand():
    global bj_state, bj_timer
    if bj_state != "playing":
        return
    bj_state = "dealer"
    bj_timer = 0


def update_blackjack():
    global bj_state, bj_timer, balance, bj_message
    if bj_state != "dealer":
        return
    bj_timer += 1
    if bj_timer > 22:
        bj_timer = 0
        if hand_value(bj_dealer) < 17:
            if not bj_deck:
                bj_deck.extend(make_deck())
            bj_dealer.append(bj_deck.pop())
        else:
            pv = hand_value(bj_player)
            dv = hand_value(bj_dealer)
            if dv > 21 or pv > dv:
                win = bj_bet * 2
                balance += win
                bj_message = f"Победа! +{win}$"
            elif pv == dv:
                balance += bj_bet
                bj_message = "Ничья, ставка возвращена"
            else:
                bj_message = "Дилер выиграл"
            bj_state = "done"


# ------------------------------------------------------- roulette actions -
def rl_spin():
    global balance, rl_spinning, rl_frames, rl_final, rl_message, rl_target, rl_angle
    if rl_spinning:
        return
    if rl_bet_type is None:
        rl_message = "Сделайте ставку!"
        return
    if balance < rl_bet_amount:
        rl_message = "Недостаточно средств!"
        return
    balance -= rl_bet_amount
    rl_final = random.randint(0, 36)
    wedge = 360 / 37
    base = (-rl_final * wedge) % 360
    rl_target = 360 * 6 + base
    rl_angle = 0.0
    rl_spinning = True
    rl_frames = 0
    rl_message = ""


def rl_resolve():
    global balance, rl_message, rl_result
    rl_result = rl_final
    color = num_color(rl_final)
    kind, val = rl_bet_type
    if kind == "num" and val == rl_final:
        win = rl_bet_amount * 36
        balance += win
        rl_message = f"Число {rl_final}! Выигрыш +{win}$"
    elif kind == "color" and val == color:
        win = rl_bet_amount * 2
        balance += win
        color_ru = "красное" if color == "red" else "чёрное"
        rl_message = f"Выпало {color_ru}! +{win}$"
    else:
        color_ru = {"red": "красное", "black": "чёрное", "green": "зеро"}[color]
        rl_message = f"Выпало {rl_final} ({color_ru}). Увы."


def update_roulette():
    global rl_frames, rl_angle, rl_spinning
    if not rl_spinning:
        return
    rl_frames += 1
    t = min(1.0, rl_frames / RL_MAX_FRAMES)
    eased = 1 - (1 - t) ** 3
    rl_angle = rl_target * eased
    if rl_frames >= RL_MAX_FRAMES:
        rl_spinning = False
        rl_angle = rl_target % 360
        rl_resolve()


# ------------------------------------------------------------ dice actions
def dc_roll():
    global balance, dc_spinning, dc_frames, dc_final, dc_message, dc_y, dc_vy, dc_rot
    if dc_spinning:
        return
    if dc_choice is None:
        dc_message = "Выберите ставку!"
        return
    if balance < dc_bet:
        dc_message = "Недостаточно средств!"
        return
    balance -= dc_bet
    dc_final = random.randint(1, 6)
    dc_spinning = True
    dc_frames = 0
    dc_message = ""
    dc_y = 0.0
    dc_vy = -15.0
    dc_rot = 0.0


def dc_resolve():
    global balance, dc_message
    kind, val = dc_choice
    if kind == "num" and val == dc_final:
        win = dc_bet * 5
        balance += win
        dc_message = f"Выпало {dc_final}! +{win}$"
    elif kind == "parity":
        actual = "even" if dc_final % 2 == 0 else "odd"
        if val == actual:
            win = dc_bet * 2
            balance += win
            word = "чётное" if actual == "even" else "нечётное"
            dc_message = f"Выпало {dc_final} ({word})! +{win}$"
        else:
            dc_message = f"Выпало {dc_final}. Увы."
    else:
        dc_message = f"Выпало {dc_final}. Увы."


def update_dice():
    global dc_frames, dc_spinning, dc_display, dc_y, dc_vy, dc_rot
    if not dc_spinning:
        return
    dc_frames += 1
    dc_vy += 0.9
    dc_y += dc_vy
    dc_rot += 18 + abs(dc_vy) * 1.4
    if dc_frames % 3 == 0:
        dc_display = random.randint(1, 6)
    if dc_y >= 0 and dc_vy >= 0 and dc_frames > 14:
        dc_spinning = False
        dc_y = 0.0
        dc_rot = 0.0
        dc_display = dc_final
        dc_resolve()


# ------------------------------------------------------------ coin actions
def cn_flip():
    global balance, cn_flipping, cn_frames, cn_final, cn_vy, cn_y, cn_message
    if cn_flipping:
        return
    if cn_choice is None:
        cn_message = "Выберите сторону!"
        return
    if balance < cn_bet:
        cn_message = "Недостаточно средств!"
        return
    balance -= cn_bet
    cn_final = random.choice(["heads", "tails"])
    cn_flipping = True
    cn_frames = 0
    cn_vy = -14.0
    cn_y = 0.0
    cn_message = ""


def cn_resolve():
    global balance, cn_message
    side_ru = "Орёл" if cn_final == "heads" else "Решка"
    if cn_choice == cn_final:
        win = cn_bet * 2
        balance += win
        cn_message = f"{side_ru}! Победа +{win}$"
    else:
        cn_message = f"Выпал {side_ru.lower()}. Увы."


def update_coin():
    global cn_frames, cn_vy, cn_y, cn_flipping
    if not cn_flipping:
        return
    cn_frames += 1
    cn_vy += 0.9
    cn_y += cn_vy
    if cn_y >= 0 and cn_vy >= 0 and cn_frames > 10:
        cn_y = 0.0
        cn_flipping = False
        cn_resolve()


# ----------------------------------------------------------- craps actions
def cr_roll():
    global balance, cr_state, cr_spinning, cr_frames, cr_final1, cr_final2, cr_message, cr_y, cr_vy, cr_rot
    if cr_spinning:
        return
    if cr_state == "betting":
        if balance < cr_bet:
            cr_message = "Недостаточно средств!"
            return
        balance -= cr_bet
    if cr_state not in ("betting", "point"):
        return
    cr_final1 = random.randint(1, 6)
    cr_final2 = random.randint(1, 6)
    cr_spinning = True
    cr_frames = 0
    cr_y = 0.0
    cr_vy = -15.0
    cr_rot = 0.0
    cr_message = ""


def cr_resolve():
    global balance, cr_message, cr_state, cr_point
    total = cr_final1 + cr_final2
    if cr_state == "betting":
        if total in (7, 11):
            win = cr_bet * 2
            balance += win
            cr_message = f"Выброс {total}! Победа +{win}$"
            cr_state = "done"
        elif total in (2, 3, 12):
            cr_message = f"Крэпс ({total})! Вы проиграли."
            cr_state = "done"
        else:
            cr_point = total
            cr_state = "point"
            cr_message = f"Точка: {total}. Бросайте снова!"
    else:  # point phase
        if total == 7:
            cr_message = "Выпала 7 — вы проиграли."
            cr_state = "done"
        elif total == cr_point:
            win = cr_bet * 2
            balance += win
            cr_message = f"Точка выбита! +{win}$"
            cr_state = "done"
        else:
            cr_message = f"Выпало {total}, точка ({cr_point}) ещё в игре — бросайте!"


def update_craps():
    global cr_frames, cr_spinning, cr_y, cr_vy, cr_rot, cr_d1, cr_d2
    if not cr_spinning:
        return
    cr_frames += 1
    cr_vy += 0.9
    cr_y += cr_vy
    cr_rot += 18 + abs(cr_vy) * 1.4
    if cr_frames % 3 == 0:
        cr_d1 = random.randint(1, 6)
        cr_d2 = random.randint(1, 6)
    if cr_y >= 0 and cr_vy >= 0 and cr_frames > 14:
        cr_spinning = False
        cr_y = 0.0
        cr_rot = 0.0
        cr_d1, cr_d2 = cr_final1, cr_final2
        cr_resolve()


# --------------------------------------------------------- baccarat actions
def bc_deal():
    global balance, bc_deck, bc_player, bc_banker, bc_state, bc_message
    if bc_state != "betting":
        return
    if bc_choice is None:
        bc_message = "Выберите Игрока, Банкира или Ничью!"
        return
    if balance < bc_bet:
        bc_message = "Недостаточно средств!"
        return
    balance -= bc_bet
    if len(bc_deck) < 10:
        bc_deck = make_deck()
    bc_player = [bc_deck.pop(), bc_deck.pop()]
    bc_banker = [bc_deck.pop(), bc_deck.pop()]
    pv = bacc_hand_value(bc_player)
    bv = bacc_hand_value(bc_banker)
    if pv > bv:
        winner = "player"
    elif bv > pv:
        winner = "banker"
    else:
        winner = "tie"
    if bc_choice == winner:
        if winner == "tie":
            win = bc_bet * 9
            balance += win
            bc_message = f"Ничья {pv}:{bv}! Выигрыш +{win}$"
        else:
            win = int(bc_bet * 1.95)
            balance += win
            side = "Игрок" if winner == "player" else "Банкир"
            bc_message = f"{side} побеждает {pv}:{bv}! +{win}$"
    elif winner == "tie":
        balance += bc_bet
        bc_message = f"Ничья {pv}:{bv} — ставка возвращена."
    else:
        side = "Игрок" if winner == "player" else "Банкир"
        bc_message = f"{side} побеждает {pv}:{bv}. Увы."
    bc_state = "done"


# ------------------------------------------------------------ poker actions
def pk_deal():
    global balance, pk_deck, pk_player, pk_dealer, pk_state, pk_message
    if pk_state != "betting":
        return
    if balance < pk_bet:
        pk_message = "Недостаточно средств!"
        return
    balance -= pk_bet
    if len(pk_deck) < 10:
        pk_deck = make_deck()
    pk_player = [pk_deck.pop(), pk_deck.pop(), pk_deck.pop()]
    pk_dealer = [pk_deck.pop(), pk_deck.pop(), pk_deck.pop()]
    pk_message = ""
    pk_state = "deciding"


def pk_play():
    global balance, pk_state, pk_message
    if pk_state != "deciding":
        return
    if balance < pk_bet:
        pk_message = "Недостаточно средств для игры!"
        return
    balance -= pk_bet
    ps = poker3_score(pk_player)
    ds = poker3_score(pk_dealer)
    pname = POKER_HAND_NAMES[ps[0]]
    dname = POKER_HAND_NAMES[ds[0]]
    if ps > ds:
        win = pk_bet * 4
        balance += win
        pk_message = f"{pname} против {dname} — победа! +{win}$"
    elif ps == ds:
        win = pk_bet * 2
        balance += win
        pk_message = f"Ничья ({pname}) — ставки возвращены."
    else:
        pk_message = f"{pname} против {dname} — дилер сильнее. Увы."
    pk_state = "done"


def pk_fold():
    global pk_state, pk_message
    if pk_state != "deciding":
        return
    pk_message = "Вы сбросили карты. Анте потеряно."
    pk_state = "done"


# =========================================================== DRAW SCREENS =
def draw_menu():
    lbl = title_font.render("ROYAL CASINO", True, GOLD)
    screen.blit(lbl, lbl.get_rect(center=(WIDTH // 2, 220)))
    sub = small.render("Добро пожаловать в казино", True, CREAM)
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, 280)))
    play_rect = pygame.Rect(WIDTH // 2 - 130, 380, 260, 72)
    exit_rect = pygame.Rect(WIDTH // 2 - 130, 470, 260, 60)
    draw_button(screen, play_rect, "ИГРАТЬ", "menu_play", fnt=font)
    draw_button(screen, exit_rect, "ВЫХОД", "menu_exit", color=(120, 30, 30), txt_color=CREAM, fnt=font)
    return {"play": play_rect, "exit": exit_rect}


def draw_mini_icon(key, cx, cy):
    if key == "slots":
        draw_star(screen, cx, cy, 60)
    elif key == "blackjack":
        draw_card(screen, cx - 30, cy - 40, ("A", "\u2660", BLACK_C), True, w=60, h=84)
    elif key == "roulette":
        draw_wheel(screen, cx, cy, 34, 0, show_numbers=False)
    elif key == "dice":
        draw_die(screen, cx, cy, 46, 5)
    elif key == "coin":
        draw_coin_visual(screen, cx, cy, 32, False, 0, "heads")
    elif key == "craps":
        draw_die(screen, cx - 20, cy, 34, 4)
        draw_die(screen, cx + 20, cy + 6, 34, 6)
    elif key == "baccarat":
        draw_card(screen, cx - 34, cy - 38, ("9", "\u2666", RED), True, w=54, h=76)
        draw_card(screen, cx + 6, cy - 30, ("K", "\u2660", BLACK_C), True, w=54, h=76)
    elif key == "poker":
        draw_card(screen, cx - 44, cy - 34, ("Q", "\u2665", RED), True, w=48, h=68)
        draw_card(screen, cx - 12, cy - 40, ("K", "\u2660", BLACK_C), True, w=48, h=68)
        draw_card(screen, cx + 20, cy - 34, ("A", "\u2663", BLACK_C), True, w=48, h=68)


def draw_hub():
    draw_header("ВЫБЕРИТЕ ИГРУ")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "hub_back", color=(90, 20, 25), txt_color=CREAM)
    rects = {"back": back}
    cw, ch, gap = 220, 168, 18
    row0_x = (WIDTH - (3 * cw + 2 * gap)) // 2
    row1_x = (WIDTH - (2 * cw + gap)) // 2
    rows_y = [148, 148 + ch + gap, 148 + 2 * (ch + gap)]
    positions = [(row0_x, rows_y[0]), (row0_x + cw + gap, rows_y[0]), (row0_x + 2 * (cw + gap), rows_y[0]),
                 (row0_x, rows_y[1]), (row0_x + cw + gap, rows_y[1]), (row0_x + 2 * (cw + gap), rows_y[1]),
                 (row1_x, rows_y[2]), (row1_x + cw + gap, rows_y[2])]
    for g, (x, y) in zip(GAMES, positions):
        rect = pygame.Rect(x, y, cw, ch)
        draw_panel(screen, rect, color=g["color"], radius=16, border=GOLD)
        draw_mini_icon(g["key"], rect.centerx, rect.y + 62)
        tlbl = font.render(g["title"], True, GOLD_LIGHT)
        screen.blit(tlbl, tlbl.get_rect(center=(rect.centerx, rect.y + 118)))
        dlbl = tiny.render(g["desc"], True, CREAM)
        screen.blit(dlbl, dlbl.get_rect(center=(rect.centerx, rect.y + 143)))
        hov, pr = anim_update(g["key"] + "_hub", rect.collidepoint(pygame.mouse.get_pos()), False)
        if hov > 0.05:
            pygame.draw.rect(screen, GOLD_LIGHT, rect.inflate(6, 6), width=3, border_radius=18)
        rects[g["key"]] = rect
    return rects


def draw_tutorial():
    key = current_game
    overlay_dark(180)
    panel = pygame.Rect(WIDTH // 2 - 350, 110, 700, 540)
    draw_panel(screen, panel, color=(45, 12, 16), radius=20, border=GOLD)
    title = big_font.render(f"Как играть: {GAME_TITLES[key]}", True, GOLD)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 55)))
    lines = TUTORIALS[key]
    for i, ln in enumerate(lines):
        bounce = int(3 * math.sin(frame_tick * 0.15 + i))
        arrow = small.render("\u27a4", True, GOLD)
        screen.blit(arrow, (panel.x + 40 + bounce, panel.y + 130 + i * 62))
        # wrap long lines
        words = ln.split(" ")
        wlines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if small.size(test)[0] > panel.w - 130:
                wlines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            wlines.append(cur)
        for j, wl in enumerate(wlines):
            txt = small.render(wl, True, CREAM)
            screen.blit(txt, (panel.x + 80, panel.y + 130 + i * 62 + j * 24))
    bob = int(6 * math.sin(frame_tick * 0.12))
    chevron = font.render("\u2193", True, GOLD_LIGHT)
    screen.blit(chevron, chevron.get_rect(center=(panel.centerx, panel.y + 445 + bob)))
    ok_rect = pygame.Rect(panel.centerx - 150, panel.y + 465, 300, 60)
    draw_button(screen, ok_rect, "Понятно, играть!", "tut_ok")
    return {"ok": ok_rect}


def bet_controls(y, bet_value, minus_key, plus_key):
    minus_r = pygame.Rect(WIDTH // 2 - 150, y, 60, 50)
    plus_r = pygame.Rect(WIDTH // 2 + 90, y, 60, 50)
    draw_button(screen, minus_r, "-10", minus_key, fnt=small)
    draw_button(screen, plus_r, "+10", plus_key, fnt=small)
    lbl = font.render(f"Ставка: {bet_value}$", True, GOLD_LIGHT)
    screen.blit(lbl, lbl.get_rect(center=(WIDTH // 2, y + 25)))
    return minus_r, plus_r


def draw_message(msg, y=690):
    if msg:
        lbl = font.render(msg, True, GOLD_LIGHT)
        screen.blit(lbl, lbl.get_rect(center=(WIDTH // 2, y)))


def draw_lever(rect_x, rect_y, rect_h, pull_t):
    track = pygame.Rect(rect_x, rect_y, 26, rect_h)
    pygame.draw.rect(screen, WINE_DARK, track, border_radius=13)
    pygame.draw.rect(screen, darken(GOLD, 40), track, width=3, border_radius=13)
    base = pygame.Rect(rect_x - 22, rect_y + rect_h - 6, 70, 26)
    draw_panel(screen, base, color=(60, 18, 22), radius=10, border=GOLD)
    knob_y = rect_y + 18 + pull_t * (rect_h - 60)
    knob_center = (rect_x + 13, int(knob_y))
    pygame.draw.line(screen, GOLD_DARK, (rect_x + 13, rect_y + rect_h - 10), knob_center, 8)
    pygame.gfxdraw.filled_circle(screen, knob_center[0], knob_center[1], 22, RED)
    pygame.gfxdraw.aacircle(screen, knob_center[0], knob_center[1], 22, GOLD_LIGHT)
    pygame.gfxdraw.aacircle(screen, knob_center[0], knob_center[1], 20, GOLD)
    knob_rect = pygame.Rect(0, 0, 48, 48)
    knob_rect.center = knob_center
    return track, knob_rect


def draw_slots():
    draw_header("СЛОТ-МАШИНА")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "slots_back", color=(90, 20, 25), txt_color=CREAM)

    panel = pygame.Rect(WIDTH // 2 - 220, 200, 440, 170)
    draw_panel(screen, panel, color=FELT, radius=16, border=GOLD)
    for i in range(3):
        cx = panel.x + 90 + i * 140
        cy = panel.centery
        slot_rect = pygame.Rect(cx - 55, panel.y + 20, 110, 130)
        pygame.draw.rect(screen, FELT_DARK, slot_rect, border_radius=10)
        pygame.draw.rect(screen, GOLD_DARK, slot_rect, width=3, border_radius=10)
        sym = sl_display[i]
        sym[1](screen, cx, cy, 64)

    lever_track, lever_knob = draw_lever(panel.right + 34, panel.y - 10, panel.h + 20, sl_lever)

    spin_rect = pygame.Rect(WIDTH // 2 - 130, 410, 260, 60)
    draw_button(screen, spin_rect, "КРУТИТЬ!", "slots_spin", enabled=not sl_spinning)
    mrect, prect = bet_controls(495, sl_bet, "slots_bet_minus", "slots_bet_plus")
    draw_message(sl_message, 585)
    hint = tiny.render("Совет: рычаг справа можно потянуть вниз мышью", True, (200, 190, 170))
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 620)))
    return {"back": back, "spin": spin_rect, "bet_minus": mrect, "bet_plus": prect,
            "lever_track": lever_track, "lever_knob": lever_knob}


def draw_blackjack():
    draw_header("БЛЭКДЖЕК")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "bj_back", color=(90, 20, 25), txt_color=CREAM)

    dlbl = small.render("Дилер", True, GOLD_LIGHT)
    screen.blit(dlbl, (WIDTH // 2 - 260, 150))
    for i, c in enumerate(bj_dealer):
        face_up = True if bj_state in ("dealer", "done") or i == 0 else False
        draw_card(screen, WIDTH // 2 - 260 + i * 100, 180, c, face_up)
    if bj_dealer:
        dv = hand_value(bj_dealer) if bj_state in ("dealer", "done") else "?"
        vlbl = small.render(f"Сумма: {dv}", True, CREAM)
        screen.blit(vlbl, (WIDTH // 2 - 260, 320))

    plbl = small.render("Игрок", True, GOLD_LIGHT)
    screen.blit(plbl, (WIDTH // 2 - 260, 400))
    for i, c in enumerate(bj_player):
        draw_card(screen, WIDTH // 2 - 260 + i * 100, 430, c, True)
    if bj_player:
        vlbl = small.render(f"Сумма: {hand_value(bj_player)}", True, CREAM)
        screen.blit(vlbl, (WIDTH // 2 - 260, 570))

    rects = {"back": back}
    if bj_state in ("betting", "done"):
        deal_rect = pygame.Rect(WIDTH // 2 - 130, 590, 260, 58)
        label = "РАЗДАТЬ" if bj_state == "betting" else "ЕЩЁ РАЗ"
        draw_button(screen, deal_rect, label, "bj_deal")
        mrect, prect = bet_controls(658, bj_bet, "bj_bet_minus", "bj_bet_plus")
        rects.update({"deal": deal_rect, "bet_minus": mrect, "bet_plus": prect})
        draw_message(bj_message, 745)
    elif bj_state == "playing":
        hit_rect = pygame.Rect(WIDTH // 2 - 220, 610, 200, 60)
        stand_rect = pygame.Rect(WIDTH // 2 + 20, 610, 200, 60)
        draw_button(screen, hit_rect, "ЕЩЁ КАРТУ", "bj_hit")
        draw_button(screen, stand_rect, "ХВАТИТ", "bj_stand", color=(120, 30, 30), txt_color=CREAM)
        rects.update({"hit": hit_rect, "stand": stand_rect})
        draw_message(bj_message, 700)
    else:
        wait = small.render("Дилер думает...", True, GOLD_LIGHT)
        screen.blit(wait, wait.get_rect(center=(WIDTH // 2, 630)))
        draw_message(bj_message, 700)
    return rects


def draw_roulette():
    draw_header("РУЛЕТКА")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "rl_back", color=(90, 20, 25), txt_color=CREAM)

    draw_wheel(screen, WIDTH // 2, 195, 95, rl_angle)

    rects = {"back": back}
    x0, y0 = 96, 300
    bw, bh = 66, 44
    gap = 4
    zero_rect = pygame.Rect(x0, y0, bw, bh * 3 + gap * 2)
    color0 = GOLD if rl_bet_type == ("num", 0) else (20, 120, 40)
    draw_button(screen, zero_rect, "0", "rl_num_0", color=color0, txt_color=CREAM, fnt=font, radius=10)
    rects["num_0"] = zero_rect
    startx = x0 + bw + 8
    for row in range(3):
        for col in range(12):
            n = row * 12 + col + 1
            rect = pygame.Rect(startx + col * (bw + 4), y0 + row * (bh + gap), bw, bh)
            base = RED if num_color(n) == "red" else BLACK_C
            color = GOLD if rl_bet_type == ("num", n) else base
            txtc = WINE if rl_bet_type == ("num", n) else CREAM
            draw_button(screen, rect, str(n), f"rl_num_{n}", color=color, txt_color=txtc, fnt=tiny, radius=8)
            rects[f"num_{n}"] = rect

    red_rect = pygame.Rect(WIDTH // 2 - 320, 452, 300, 58)
    black_rect = pygame.Rect(WIDTH // 2 + 20, 452, 300, 58)
    rc = GOLD if rl_bet_type == ("color", "red") else RED
    bc = GOLD if rl_bet_type == ("color", "black") else BLACK_C
    draw_button(screen, red_rect, "КРАСНОЕ", "rl_red", color=rc, txt_color=CREAM if rc != GOLD else WINE)
    draw_button(screen, black_rect, "ЧЁРНОЕ", "rl_black", color=bc, txt_color=CREAM if bc != GOLD else WINE)
    rects["red"] = red_rect
    rects["black"] = black_rect

    mrect, prect = bet_controls(524, rl_bet_amount, "rl_bet_minus", "rl_bet_plus")
    rects["bet_minus"] = mrect
    rects["bet_plus"] = prect

    spin_rect = pygame.Rect(WIDTH // 2 - 130, 588, 260, 58)
    draw_button(screen, spin_rect, "КРУТИТЬ!", "rl_spin", enabled=not rl_spinning)
    rects["spin"] = spin_rect
    draw_message(rl_message, 675)
    return rects


def draw_dice():
    draw_header("КОСТИ")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "dc_back", color=(90, 20, 25), txt_color=CREAM)

    draw_die(screen, WIDTH // 2, int(210 + dc_y), 140, dc_display, dc_rot)

    rects = {"back": back}
    startx = WIDTH // 2 - 3 * 90
    for n in range(1, 7):
        rect = pygame.Rect(startx + (n - 1) * 90, 360, 76, 64)
        color = GOLD if dc_choice == ("num", n) else BLUE
        txtc = WINE if dc_choice == ("num", n) else CREAM
        draw_button(screen, rect, str(n), f"dc_num_{n}", color=color, txt_color=txtc)
        rects[f"num_{n}"] = rect

    even_rect = pygame.Rect(WIDTH // 2 - 220, 445, 200, 55)
    odd_rect = pygame.Rect(WIDTH // 2 + 20, 445, 200, 55)
    ec = GOLD if dc_choice == ("parity", "even") else (90, 60, 20)
    oc = GOLD if dc_choice == ("parity", "odd") else (90, 60, 20)
    draw_button(screen, even_rect, "ЧЁТНОЕ", "dc_even", color=ec, txt_color=WINE if ec == GOLD else CREAM, fnt=small)
    draw_button(screen, odd_rect, "НЕЧЁТНОЕ", "dc_odd", color=oc, txt_color=WINE if oc == GOLD else CREAM, fnt=small)
    rects["even"] = even_rect
    rects["odd"] = odd_rect

    roll_rect = pygame.Rect(WIDTH // 2 - 130, 590, 260, 60)
    draw_button(screen, roll_rect, "БРОСИТЬ", "dc_roll", enabled=not dc_spinning)
    rects["roll"] = roll_rect
    mrect, prect = bet_controls(525, dc_bet, "dc_bet_minus", "dc_bet_plus")
    rects["bet_minus"] = mrect
    rects["bet_plus"] = prect
    draw_message(dc_message, 670)
    return rects


def draw_coin_game():
    draw_header("МОНЕТКА")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "cn_back", color=(90, 20, 25), txt_color=CREAM)

    base_cy = 340
    draw_coin_visual(screen, WIDTH // 2, int(base_cy + cn_y), 80, cn_flipping, cn_frames, cn_final)

    rects = {"back": back}
    heads_rect = pygame.Rect(WIDTH // 2 - 220, 460, 200, 60)
    tails_rect = pygame.Rect(WIDTH // 2 + 20, 460, 200, 60)
    hc = GOLD if cn_choice == "heads" else (150, 120, 20)
    tc = GOLD if cn_choice == "tails" else (150, 120, 20)
    draw_button(screen, heads_rect, "ОРЁЛ", "cn_heads", color=hc, txt_color=WINE)
    draw_button(screen, tails_rect, "РЕШКА", "cn_tails", color=tc, txt_color=WINE)
    rects["heads"] = heads_rect
    rects["tails"] = tails_rect

    flip_rect = pygame.Rect(WIDTH // 2 - 150, 545, 300, 60)
    draw_button(screen, flip_rect, "ПОДБРОСИТЬ МОНЕТУ", "cn_flip", enabled=not cn_flipping, fnt=small)
    rects["flip"] = flip_rect
    mrect, prect = bet_controls(620, cn_bet, "cn_bet_minus", "cn_bet_plus")
    rects["bet_minus"] = mrect
    rects["bet_plus"] = prect
    draw_message(cn_message, 700)
    return rects


def draw_craps():
    draw_header("КРЭПС")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "cr_back", color=(90, 20, 25), txt_color=CREAM)

    draw_die(screen, WIDTH // 2 - 70, int(200 + cr_y), 110, cr_d1, cr_rot)
    draw_die(screen, WIDTH // 2 + 70, int(200 + cr_y), 110, cr_d2, -cr_rot)

    if cr_point is not None and cr_state in ("point", "done"):
        plbl = small.render(f"Точка: {cr_point}", True, GOLD_LIGHT)
        screen.blit(plbl, plbl.get_rect(center=(WIDTH // 2, 330)))

    rects = {"back": back}
    if cr_state in ("betting",):
        roll_rect = pygame.Rect(WIDTH // 2 - 130, 400, 260, 58)
        draw_button(screen, roll_rect, "БРОСИТЬ", "cr_roll", enabled=not cr_spinning)
        rects["roll"] = roll_rect
        mrect, prect = bet_controls(475, cr_bet, "cr_bet_minus", "cr_bet_plus")
        rects["bet_minus"] = mrect
        rects["bet_plus"] = prect
        draw_message(cr_message, 560)
    elif cr_state == "point":
        roll_rect = pygame.Rect(WIDTH // 2 - 130, 400, 260, 58)
        draw_button(screen, roll_rect, "БРОСИТЬ СНОВА", "cr_roll", enabled=not cr_spinning, fnt=small)
        rects["roll"] = roll_rect
        draw_message(cr_message, 480)
    else:
        again_rect = pygame.Rect(WIDTH // 2 - 130, 400, 260, 58)
        draw_button(screen, again_rect, "ЕЩЁ РАЗ", "cr_again")
        rects["again"] = again_rect
        draw_message(cr_message, 480)
    return rects


def draw_baccarat():
    draw_header("БАККАРА")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "bc_back", color=(90, 20, 25), txt_color=CREAM)

    plbl = small.render("Игрок", True, GOLD_LIGHT)
    screen.blit(plbl, (WIDTH // 2 - 380, 170))
    for i, c in enumerate(bc_player):
        draw_card(screen, WIDTH // 2 - 380 + i * 100, 200, c, True)
    if bc_player:
        vlbl = small.render(f"Очки: {bacc_hand_value(bc_player)}", True, CREAM)
        screen.blit(vlbl, (WIDTH // 2 - 380, 335))

    bklbl = small.render("Банкир", True, GOLD_LIGHT)
    screen.blit(bklbl, (WIDTH // 2 + 100, 170))
    for i, c in enumerate(bc_banker):
        draw_card(screen, WIDTH // 2 + 100 + i * 100, 200, c, True)
    if bc_banker:
        vlbl = small.render(f"Очки: {bacc_hand_value(bc_banker)}", True, CREAM)
        screen.blit(vlbl, (WIDTH // 2 + 100, 335))

    rects = {"back": back}
    py = 400
    pr = pygame.Rect(WIDTH // 2 - 330, py, 210, 56)
    br = pygame.Rect(WIDTH // 2 - 105, py, 210, 56)
    tr = pygame.Rect(WIDTH // 2 + 120, py, 210, 56)
    pc = GOLD if bc_choice == "player" else FELT
    bcc = GOLD if bc_choice == "banker" else FELT
    tc = GOLD if bc_choice == "tie" else FELT
    draw_button(screen, pr, "ИГРОК x2", "bc_player", color=pc, txt_color=WINE if pc == GOLD else CREAM, fnt=small)
    draw_button(screen, br, "БАНКИР x1.95", "bc_banker", color=bcc, txt_color=WINE if bcc == GOLD else CREAM, fnt=small)
    draw_button(screen, tr, "НИЧЬЯ x9", "bc_tie", color=tc, txt_color=WINE if tc == GOLD else CREAM, fnt=small)
    rects.update({"player_bet": pr, "banker_bet": br, "tie_bet": tr})

    if bc_state == "betting":
        deal_rect = pygame.Rect(WIDTH // 2 - 130, 470, 260, 58)
        draw_button(screen, deal_rect, "РАЗДАТЬ", "bc_deal")
        rects["deal"] = deal_rect
        mrect, prect = bet_controls(545, bc_bet, "bc_bet_minus", "bc_bet_plus")
        rects["bet_minus"] = mrect
        rects["bet_plus"] = prect
    else:
        again_rect = pygame.Rect(WIDTH // 2 - 130, 470, 260, 58)
        draw_button(screen, again_rect, "ЕЩЁ РАЗ", "bc_again")
        rects["again"] = again_rect
    draw_message(bc_message, 635)
    return rects


def draw_poker():
    draw_header("ПОКЕР (3 КАРТЫ)")
    back = pygame.Rect(20, 18, 150, 54)
    draw_button(screen, back, "\u2190 Меню", "pk_back", color=(90, 20, 25), txt_color=CREAM)

    dlbl = small.render("Дилер", True, GOLD_LIGHT)
    screen.blit(dlbl, (WIDTH // 2 - 200, 160))
    for i, c in enumerate(pk_dealer):
        face_up = pk_state == "done"
        draw_card(screen, WIDTH // 2 - 200 + i * 100, 190, c, face_up)
    if pk_dealer and pk_state == "done":
        vlbl = small.render(POKER_HAND_NAMES[poker3_score(pk_dealer)[0]], True, CREAM)
        screen.blit(vlbl, (WIDTH // 2 - 200, 330))

    plbl = small.render("Игрок", True, GOLD_LIGHT)
    screen.blit(plbl, (WIDTH // 2 - 200, 400))
    for i, c in enumerate(pk_player):
        draw_card(screen, WIDTH // 2 - 200 + i * 100, 430, c, True)
    if pk_player:
        vlbl = small.render(POKER_HAND_NAMES[poker3_score(pk_player)[0]], True, CREAM)
        screen.blit(vlbl, (WIDTH // 2 - 200, 570))

    rects = {"back": back}
    if pk_state == "betting":
        deal_rect = pygame.Rect(WIDTH // 2 - 130, 600, 260, 58)
        draw_button(screen, deal_rect, "РАЗДАТЬ (АНТЕ)", "pk_deal", fnt=small)
        rects["deal"] = deal_rect
        mrect, prect = bet_controls(668, pk_bet, "pk_bet_minus", "pk_bet_plus")
        rects["bet_minus"] = mrect
        rects["bet_plus"] = prect
        draw_message(pk_message, 745)
    elif pk_state == "deciding":
        play_rect = pygame.Rect(WIDTH // 2 - 220, 610, 200, 58)
        fold_rect = pygame.Rect(WIDTH // 2 + 20, 610, 200, 58)
        draw_button(screen, play_rect, "ИГРАТЬ", "pk_play")
        draw_button(screen, fold_rect, "СБРОСИТЬ", "pk_fold", color=(120, 30, 30), txt_color=CREAM)
        rects["play"] = play_rect
        rects["fold"] = fold_rect
        draw_message(pk_message, 690)
    else:
        again_rect = pygame.Rect(WIDTH // 2 - 130, 610, 260, 58)
        draw_button(screen, again_rect, "ЕЩЁ РАЗ", "pk_again")
        rects["again"] = again_rect
        draw_message(pk_message, 690)
    return rects


def draw_pause_overlay():
    overlay_dark(170)
    panel = pygame.Rect(WIDTH // 2 - 210, 220, 420, 340)
    draw_panel(screen, panel, color=(45, 12, 16), radius=20, border=GOLD)
    title = big_font.render("ПАУЗА", True, GOLD)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 55)))
    resume_r = pygame.Rect(panel.centerx - 150, panel.y + 110, 300, 58)
    restart_r = pygame.Rect(panel.centerx - 150, panel.y + 180, 300, 58)
    hub_r = pygame.Rect(panel.centerx - 150, panel.y + 250, 300, 58)
    draw_button(screen, resume_r, "Продолжить", "pause_resume")
    draw_button(screen, restart_r, "Начать заново", "pause_restart")
    draw_button(screen, hub_r, "В главное меню", "pause_hub", color=(90, 20, 25), txt_color=CREAM)
    return {"resume": resume_r, "restart": restart_r, "hub": hub_r}


# ============================================================ CLICK LOGIC =
def handle_menu_click(pos, rects):
    global state, running
    if rects["play"].collidepoint(pos):
        state = "hub"
    elif rects["exit"].collidepoint(pos):
        running = False


def handle_hub_click(pos, rects):
    global state
    if rects["back"].collidepoint(pos):
        state = "menu"
        return
    for g in GAMES:
        if rects[g["key"]].collidepoint(pos):
            enter_game(g["key"])
            return


def handle_tutorial_click(pos, rects):
    if rects["ok"].collidepoint(pos):
        confirm_tutorial()


def handle_slots_click(pos, rects):
    global state, sl_bet
    if rects["back"].collidepoint(pos):
        state = "hub"
    elif rects["spin"].collidepoint(pos):
        slot_spin()
    elif rects["bet_minus"].collidepoint(pos):
        sl_bet = max(10, sl_bet - 10)
    elif rects["bet_plus"].collidepoint(pos):
        sl_bet = min(500, sl_bet + 10)


def handle_blackjack_click(pos, rects):
    global state, bj_bet
    if rects["back"].collidepoint(pos):
        state = "hub"
        return
    if "deal" in rects and rects["deal"].collidepoint(pos):
        bj_deal()
    elif "hit" in rects and rects["hit"].collidepoint(pos):
        bj_hit()
    elif "stand" in rects and rects["stand"].collidepoint(pos):
        bj_stand()
    elif "bet_minus" in rects and rects["bet_minus"].collidepoint(pos):
        bj_bet = max(10, bj_bet - 10)
    elif "bet_plus" in rects and rects["bet_plus"].collidepoint(pos):
        bj_bet = min(500, bj_bet + 10)


def handle_roulette_click(pos, rects):
    global state, rl_bet_type, rl_bet_amount
    if rects["back"].collidepoint(pos):
        state = "hub"
        return
    if rl_spinning:
        return
    if rects["spin"].collidepoint(pos):
        rl_spin()
        return
    if rects["red"].collidepoint(pos):
        rl_bet_type = ("color", "red")
        return
    if rects["black"].collidepoint(pos):
        rl_bet_type = ("color", "black")
        return
    if rects["bet_minus"].collidepoint(pos):
        rl_bet_amount = max(10, rl_bet_amount - 10)
        return
    if rects["bet_plus"].collidepoint(pos):
        rl_bet_amount = min(500, rl_bet_amount + 10)
        return
    for n in range(37):
        key = f"num_{n}"
        if rects[key].collidepoint(pos):
            rl_bet_type = ("num", n)
            return


def handle_dice_click(pos, rects):
    global state, dc_choice, dc_bet
    if rects["back"].collidepoint(pos):
        state = "hub"
        return
    if dc_spinning:
        return
    if rects["roll"].collidepoint(pos):
        dc_roll()
        return
    if rects["even"].collidepoint(pos):
        dc_choice = ("parity", "even")
        return
    if rects["odd"].collidepoint(pos):
        dc_choice = ("parity", "odd")
        return
    if rects["bet_minus"].collidepoint(pos):
        dc_bet = max(10, dc_bet - 10)
        return
    if rects["bet_plus"].collidepoint(pos):
        dc_bet = min(500, dc_bet + 10)
        return
    for n in range(1, 7):
        key = f"num_{n}"
        if rects[key].collidepoint(pos):
            dc_choice = ("num", n)
            return


def handle_coin_click(pos, rects):
    global state, cn_choice, cn_bet
    if rects["back"].collidepoint(pos):
        state = "hub"
        return
    if cn_flipping:
        return
    if rects["flip"].collidepoint(pos):
        cn_flip()
        return
    if rects["heads"].collidepoint(pos):
        cn_choice = "heads"
        return
    if rects["tails"].collidepoint(pos):
        cn_choice = "tails"
        return
    if rects["bet_minus"].collidepoint(pos):
        cn_bet = max(10, cn_bet - 10)
        return
    if rects["bet_plus"].collidepoint(pos):
        cn_bet = min(500, cn_bet + 10)
        return


def handle_craps_click(pos, rects):
    global state, cr_bet
    if rects["back"].collidepoint(pos):
        state = "hub"
        return
    if "roll" in rects and rects["roll"].collidepoint(pos):
        cr_roll()
        return
    if "again" in rects and rects["again"].collidepoint(pos):
        reset_craps()
        return
    if "bet_minus" in rects and rects["bet_minus"].collidepoint(pos):
        cr_bet = max(10, cr_bet - 10)
        return
    if "bet_plus" in rects and rects["bet_plus"].collidepoint(pos):
        cr_bet = min(500, cr_bet + 10)
        return


def handle_baccarat_click(pos, rects):
    global state, bc_choice, bc_bet
    if rects["back"].collidepoint(pos):
        state = "hub"
        return
    if "deal" in rects and rects["deal"].collidepoint(pos):
        bc_deal()
        return
    if "again" in rects and rects["again"].collidepoint(pos):
        reset_baccarat()
        return
    if bc_state == "betting":
        if rects["player_bet"].collidepoint(pos):
            bc_choice = "player"
            return
        if rects["banker_bet"].collidepoint(pos):
            bc_choice = "banker"
            return
        if rects["tie_bet"].collidepoint(pos):
            bc_choice = "tie"
            return
        if "bet_minus" in rects and rects["bet_minus"].collidepoint(pos):
            bc_bet = max(10, bc_bet - 10)
            return
        if "bet_plus" in rects and rects["bet_plus"].collidepoint(pos):
            bc_bet = min(500, bc_bet + 10)
            return


def handle_poker_click(pos, rects):
    global state, pk_bet
    if rects["back"].collidepoint(pos):
        state = "hub"
        return
    if "deal" in rects and rects["deal"].collidepoint(pos):
        pk_deal()
        return
    if "play" in rects and rects["play"].collidepoint(pos):
        pk_play()
        return
    if "fold" in rects and rects["fold"].collidepoint(pos):
        pk_fold()
        return
    if "again" in rects and rects["again"].collidepoint(pos):
        reset_poker()
        return
    if "bet_minus" in rects and rects["bet_minus"].collidepoint(pos):
        pk_bet = max(10, pk_bet - 10)
        return
    if "bet_plus" in rects and rects["bet_plus"].collidepoint(pos):
        pk_bet = min(500, pk_bet + 10)
        return


def handle_pause_click(pos, rects):
    global state, paused
    if rects["resume"].collidepoint(pos):
        paused = False
    elif rects["restart"].collidepoint(pos):
        RESETTERS[current_game]()
        paused = False
    elif rects["hub"].collidepoint(pos):
        paused = False
        state = "hub"


CLICK_HANDLERS = {
    "menu": handle_menu_click, "hub": handle_hub_click, "tutorial": handle_tutorial_click,
    "slots": handle_slots_click, "blackjack": handle_blackjack_click, "roulette": handle_roulette_click,
    "dice": handle_dice_click, "coin": handle_coin_click, "craps": handle_craps_click,
    "baccarat": handle_baccarat_click, "poker": handle_poker_click,
}

DRAW_DISPATCH = {
    "menu": draw_menu, "hub": draw_hub, "tutorial": draw_tutorial,
    "slots": draw_slots, "blackjack": draw_blackjack, "roulette": draw_roulette,
    "dice": draw_dice, "coin": draw_coin_game, "craps": draw_craps,
    "baccarat": draw_baccarat, "poker": draw_poker,
}

UPDATE_DISPATCH = {
    "slots": update_slots, "blackjack": update_blackjack, "roulette": update_roulette,
    "dice": update_dice, "coin": update_coin, "craps": update_craps,
}

# ================================================================ MAIN ====
TEST_FRAMES = int(os.environ.get("CASINO_TEST_FRAMES", "0"))
frame_count = 0
running = True
while running:
    clock.tick(60)
    frame_tick += 1
    frame_count += 1

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            if state in ("slots", "blackjack", "roulette", "dice", "coin", "craps", "baccarat", "poker"):
                paused = not paused
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if (not paused and state == "slots" and "lever_knob" in current_rects
                    and current_rects["lever_knob"].collidepoint(e.pos)):
                dragging_lever = True
            else:
                try:
                    if paused:
                        handle_pause_click(e.pos, current_rects)
                    else:
                        CLICK_HANDLERS[state](e.pos, current_rects)
                except KeyError:
                    pass
        elif e.type == pygame.MOUSEMOTION:
            if dragging_lever:
                track = current_rects.get("lever_track")
                if track:
                    rel = (e.pos[1] - (track.top + 18)) / max(1, (track.h - 60))
                    sl_lever = max(0.0, min(1.0, rel))
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if dragging_lever:
                dragging_lever = False
                if sl_lever > 0.75:
                    slot_spin()

    if not paused and state in UPDATE_DISPATCH:
        UPDATE_DISPATCH[state]()

    draw_bg()
    base_rects = DRAW_DISPATCH[state]()
    if paused:
        current_rects = draw_pause_overlay()
    else:
        current_rects = base_rects

    pygame.display.flip()

    if TEST_FRAMES and frame_count >= TEST_FRAMES:
        running = False

pygame.quit()
sys.exit()