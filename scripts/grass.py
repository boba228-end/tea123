import pygame 
from scripts import utils
import pytmx
import csv
pygame.init()

class Grass:
    def __init__(self,Id,x,y):
        self.x = x
        self.y = y
        self.timer = 0
        if Id == "1":
           self.image = utils.load_image("graphics/grass/grass_1.png",1) 
        if Id == "2":
           self.image = utils.load_image("graphics/grass/grass_2.png",1) 
        if Id == "3":
           self.image = utils.load_image("graphics/grass/grass_3.png",1)
        self.bxgrass = pygame.Rect(self.x,self.y,self.image.get_width(),self.image.get_height())
        self.stats = True
    def render(self,экран,камера):
      if self.stats ==  True:
         экран.blit(self.image,(self.x-камера[0],self.y-камера[1]))

    def uptate(self):
       if self.stats == False:
          self.timer -= 1
       if self.timer <= 0:
          self.stats = True


def kerate_grass():
    grass = []
    map = pytmx.load_pygame("tiled/spiritland.tmx")
    for i in map.get_layer_by_name("GRASS"):
       garss = Grass("1",i.x*4,i.y*4)
       grass.append(garss)
    return(grass)