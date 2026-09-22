"""
на складе имеется:
    - трава -
"""
import pygame
pygame.init()
from scripts import utils
naz = None
kolvo = 0
timer = 0
склад = {
    "трава": 200,
    "огонь": 10,
    "пропуск": 1
 } 
def load():
    global fon,grass,font,XP,man,fire,font60,font_text,propusk
    fon = utils.load_image("map/Image20260214132900.png",1.32)
    grass = utils.load_image("graphics/grass/grass_2.png",1)
    XP = utils.load_image("graphics/font/hp.png",0.26)
    man = utils.load_image("map/double_jump.png",0.26)
    fire = utils.load_image("map/Image20260729114652.png",0.2)
    propusk = utils.load_image("casino_game/assets/D27D4394-5290-495F-A4E1-60824BD67C27.png",0.2)
    font = pygame.font.Font(None,40)
    font60 = pygame.font.Font(None,70)
    font_text = pygame.font.Font("scripts/imperial_one/Webfont/Imperial Web.ttf",50)
def combo(экран:pygame.Surface):
    global timer,kolvo,naz
    if timer > 0:
        timer -= 1
        if naz == "трава":
            экран.blit(grass,(400,10))
            tetx_image = font_text.render(str(naz)+"("+str(kolvo)+")",True,(238, 75, 21))
            экран.blit(tetx_image,(470,15))
        if naz == "огонь":
            экран.blit(fire,(370,-10))
            tetx_image = font_text.render(str(naz)+"("+str(kolvo)+")",True,(36, 226, 243))
            экран.blit(tetx_image,(470,15))
        экран.blit
def add_inwentar(название,колво):
    global timer,kolvo,naz
    if timer > 0 and naz == название:
        kolvo += колво
        timer = 520
    else:
        kolvo = колво
        naz = название
        timer = 520
    if название in склад :
        склад[название] += колво
    else:
        склад[название] = колво
    timer = 520
def rem_inwentar(название,колво):
    if название in склад :
        склад[название] -= колво
    else:
        склад[название] = колво


def render(экран):
    global timer,kolvo,naz
    экран.blit(fon,(100,100))
    экран.blit(grass,(180,150))
    экран.blit(font.render(str(склад.get("трава",0)),True,(255,255,255)),(165,135))
    экран.blit(XP,(145,411))
    экран.blit(font.render(str(склад.get("XP",0)),True,(255,255,255)),(162,436))
    экран.blit(man,(260,418))
    экран.blit(font.render(str(склад.get("man",0)),True,(255,255,255)),(277,436))
    экран.blit(fire,(270,130))
    экран.blit(font.render(str(склад.get("огонь",0)),True,(255,255,255)),(270,135))
    if склад["пропуск"] > 0:
        экран.blit(propusk,(367,130))
        
def utate():
    pass



