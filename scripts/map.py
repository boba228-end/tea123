import pygame
from scripts import utils
pygame.init()

class КАРТА:
    def __init__(self):
        self.карта = utils.load_image("tiled/spiritland.png",3.9)
        self.камера = [0,0]
        self.границы = utils.load_border()
        self.vorota = utils.load_vorota()
        self.vxodi = utils.load_vxod()
    def render(self,экран):
        экран.blit(self.карта,(-self.камера[0],-self.камера[1]))
        for i in self.границы:
            bx = pygame.Rect(i[0],i[1],16*3.9,16*3.9)
            #pygame.draw.rect(экран,(255,0,0),(bx.x-self.камера[0],bx.y-self.камера[1],16*3.9,16*3.9))
    def get_iner_sechons(self,bxpl):
        список = []
        for i in self.границы:
            bx = pygame.Rect(i[0],i[1],16*3.9,16*3.9)
            if bx.colliderect(bxpl):
                список.append(bx)
        for i in self.vorota:
            bx = pygame.Rect(i[0],i[1],16*3.9,16*3.9)
            if bx.colliderect(bxpl):
                список.append(bx)
        return(список)
class КАРТА67(КАРТА):
    def __init__(self):
        self.карта = utils.load_image("я карта/sixseven.png",3.9)
        self.камера = [0,0]
        self.границы = utils.load_border2()
        self.vorota = utils.load_vorota()