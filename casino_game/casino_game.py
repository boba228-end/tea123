import pygame, random, sys
from scripts import inwentar,utils


pygame.init()
title_font = pygame.font.SysFont("georgia", 44, bold=True)
font = pygame.font.SysFont("arial", 40, bold=True)
small = pygame.font.SysFont("arial", 24, bold=True)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1100, 730))
WINE = (45, 10, 15)
GOLD = (212, 175, 55)
FELT = (10, 60, 35)
CREAM = (240, 230, 210)

def load_icon(path, size=70):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, (size, size))
cursor = utils.load_image('graphics/font/Image20260610104833.png',1)

symbols = [
    ("grass", load_icon("casino_game/assets/grass.png"), 2),
    ("fire", load_icon("casino_game/assets/fire.png"), 4),
    ("potion", load_icon("casino_game/assets/potion.png"), 6),
    ("dollar", load_icon("casino_game/assets/dollar.png"), 10),
    ("propusk", load_icon("casino_game/assets/D27D4394-5290-495F-A4E1-60824BD67C27.png"), 0)
]
result = [symbols[0], symbols[0], symbols[0]]

msg = ""
in_game = False
 
slot_btn = pygame.Rect(450, 350, 200, 60)
back_btn = pygame.Rect(20, 20, 80*2, 40*2)
spin_btn = pygame.Rect(440, 390, 200, 60)


def draw_bg():
    screen.fill(WINE)
    for row in range(0, 730, 40):
        offset = 20 if (row // 40) % 2 else 0
        for col in range(-20, 1100, 40):
            pygame.draw.circle(screen, (70, 30, 30), (col + offset, row + 20), 3)
    pygame.draw.rect(screen, GOLD, (0, 0, 1100, 730), width=6)


def gold_button(rect, text, txt_color=WINE):
    pygame.draw.rect(screen, GOLD, rect, border_radius=10)
    pygame.draw.rect(screen, CREAM, rect, width=2, border_radius=10)
    label = small.render(text, True, txt_color)
    screen.blit(label, label.get_rect(center=rect.center))


def spin():
    global balance, msg, result
    if inwentar.склад["трава"] < 3:
        msg = "Нет травы"
        return
    inwentar.rem_inwentar("трава",3)
    result = [random.choice(symbols) for _ in range(3)]
    names = [s[0] for s in result]
    if names[0] == names[1] == names[2]:
        win = 3 * result[0][2]
        inwentar.add_inwentar("трава",win)
        msg = f"Джекпот! +{win}"
        if names[0] == "propusk":
            inwentar.add_inwentar("propusk",1)
            msg = "супер джекпот!!!!!!! тебя ищет полиция"
    elif names[0] == names[1] or names[1] == names[2] or names[0] == names[2]:
        inwentar.add_inwentar("трава",3)
        msg = "Ура! +10"
    else:
        msg = "Мимо"


def run():
    global screen
    global in_game
    pygame.display.set_caption("Казино")
    running = True
    while running:
        clock.tick(120)
        XM = pygame.mouse.get_pos()[0] 
        yM = pygame.mouse.get_pos()[1]
        draw_bg()
        balance = inwentar.склад["трава"]
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if not in_game and slot_btn.collidepoint(e.pos):
                    in_game = True
                    
                elif in_game and back_btn.collidepoint(e.pos):
                    in_game = False
                elif in_game and spin_btn.collidepoint(e.pos):
                    spin()

        if not in_game:
            title = title_font.render("КАЗИНО", True, GOLD)
            screen.blit(title, title.get_rect(center=(550, 250)))
            gold_button(slot_btn, "Слот-машина")
        else:
            gold_button(back_btn, "Назад")
            screen.blit(small.render(f"Баланс: {balance}", True, GOLD), (400, 30))
            reel_panel = pygame.Rect(360, 280, 360, 90)
            pygame.draw.rect(screen, FELT, reel_panel, border_radius=12)
            pygame.draw.rect(screen, GOLD, reel_panel, width=4, border_radius=12)

            for i, sym in enumerate(result):
                icon = sym[1]
                x = reel_panel.x + 20 + i * 130
                screen.blit(icon, icon.get_rect(center=(x + 35, reel_panel.centery)))

            gold_button(spin_btn, "Крутить!")

            if msg:
                msg_label = small.render(msg, True, GOLD)
                screen.blit(msg_label, msg_label.get_rect(center=(540, 465)))
        screen.blit(cursor,(XM,yM))
        pygame.display.flip()


