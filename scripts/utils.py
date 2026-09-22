import pygame
import csv
import os
import pytmx
pygame.init()

def load_image(путь, моштаб):
    картинка = pygame.image.load(путь).convert_alpha()
    w = картинка.get_width()
    h = картинка.get_height()
    w2 = int(w * моштаб)
    h2 = int(h * моштаб)
    new_картинка = pygame.transform.scale(картинка, (w2, h2))
    return(new_картинка)
def load_images(путь,много):
    картинки = []
    ам = os.listdir(путь)
    for i in ам:
        абоба = load_image(путь +"/"+ i,много)
        картинки.append(абоба)
    return(картинки)


def cut_image(путь, можтаб, size):
    tiles = []
    картинка = load_image(путь, можтаб)
    for x in range(0, картинка.get_width(), size):
        for y in range(0, картинка.get_height(), size):
            tile = картинка.subsurface((x, y, size, size))
            tiles.append(tile)
    return(tiles)


def load_border():
    border = []
    world = pytmx.load_pygame("tiled/spiritland.tmx")
    for x,y,gid in world.get_layer_by_name("границы"):
        if gid != 0:
            border.append((x*16*3.9,y*16*3.9))
    return set (border)
def load_border2():
    border = []
    world = pytmx.load_pygame("я карта/sixseven.tmx")
    for x,y,gid in world.get_layer_by_name("borber"):
        if gid != 0:
            border.append((x*16*3.9,y*16*3.9))
    return set (border)
def load_vxod():
    vxod = []
    world = pytmx.load_pygame("tiled/spiritland.tmx")
    for x,y,git in world.get_layer_by_name("Входы"):
        if git != 0:
            vxod.append(pygame.Rect(x*16*4,y*16*4,16*4,16*4))
    return (vxod)
def load_vorota():
    vorota = []
    world = pytmx.load_pygame("tiled/spiritland.tmx")
    for x,y,git in world.get_layer_by_name("vorota"):
        if git != 0:
            vorota.append(pygame.Rect(x*16*4,y*16*4,16*4,16*4))
    return (vorota)
def load_trlrport():
    tp = []
    world = pytmx.load_pygame("tiled/spiritland.tmx")
    for x,y,git in world.get_layer_by_name("bombulend"):
        if git != 0:
            tp.append(pygame.Rect(x*16*4,y*16*4,16*4,16*4))
    return (tp)
def load_market():
    m = []
    world = pytmx.load_pygame("tiled/spiritland.tmx")
    for x,y,git in world.get_layer_by_name("marlet"):
        if git != 0:
            m.append(pygame.Rect(x*16*4,y*16*4,16*4,16*4))
    return (m)
def load_casino():
    casino = []
    world = pytmx.load_pygame("tiled/spiritland.tmx")
    for x,y,git in world.get_layer_by_name("casino"):
        if git != 0:
            casino.append(pygame.Rect(x*16*4,y*16*4,16*4,16*4))
    return (casino)