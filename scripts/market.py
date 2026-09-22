import pygame
from scripts import inwentar
from scripts import utils
from scripts import settings
from scripts import particlas
from scripts import share
pygame.init()

class Item():
     def __init__(self,x,y,tip,kost,image):
        self.x = x
        self.y = y
        self.odvodka = utils.load_image("graphics/font/ovsdfdsaf.png",1.3)
        self.videlenie = utils.load_image("graphics/font/ffsdfsdfdsafasd.png",1.1)
        self.grass = utils.load_image("graphics/grass/grass_1.png",0.7)
        self.fire = utils.load_image("map/Image20260729114652.png",0.1)
        self.trebivonia = utils.load_image("graphics/font/Image20260610104839.png",1.1)
        self.tip = tip
        self.kost = kost
        self.dy = 0
        self.coins = []
        self.time = 0
        self.font = pygame.font.Font(None,25*2)
        self.image = image
     def reneder(self,экаран,clik,playr):
          if self.time > 15:
               self.dy -= 1 
               self.time -= 1
          if self.time <= 15 and self.time != 0:
               self.dy += 1 
               self.time -= 1
          
          XM = pygame.mouse.get_pos()[0] 
          yM = pygame.mouse.get_pos()[1]
          bx = экаран.blit(self.odvodka,(self.x-7,self.y))
          bx = bx.inflate(-30,-30)
          экаран.blit(self.image,(self.x,self.y+self.dy))
          #pygame.draw.rect(экаран,(255,0,0),(bx),2)
          if bx.collidepoint(XM,yM):
               for i in self.kost:
                         if i in inwentar.склад:
                              if inwentar.склад[i] < self.kost[i]:
                                   share.tip_cursor = 2
                                   break
               else:
                    share.tip_cursor = 1 
               экаран.blit(self.videlenie,(self.x+4,self.y+8))
               экаран.blit(self.trebivonia,(self.x-30,self.y+130))
               for i in self.kost:
                    if i == "огонь":
                         
                         
                         bx = экаран.blit(self.fire,(self.x,self.y+100+50+60))
                         текст = self.font.render(":"+"  "+str(self.kost[i]),True,(255,255,0))
                         экаран.blit(текст,(bx.right+20,bx.top+7))
               for i in self.kost:
                    if i == "трава":
                         
                         bx = экаран.blit(self.grass,(self.x,self.y+100+50))
                         текст = self.font.render(":"+"  "+str(self.kost[i]),True,(255,255,0))
                         экаран.blit(текст,(bx.right+20,bx.top+7))
               if clik == True:
                    for i in self.kost:
                         if i in inwentar.склад:
                              if inwentar.склад[i] < self.kost[i]:
                                   break
                    else:
                         if self.time == 0:
                              if self.tip == "armor":
                                   playr.armor = 2
                              elif self.tip == "armor2":
                                   playr.armor = 3
                              else:
                                   inwentar.add_inwentar(self.tip,1)
                              
                              for i in self.kost:
                                   inwentar.rem_inwentar(i,self.kost[i])
                                   self.time = 30
                                   partikl = particlas.Partikl_coins(self.x,self.y)
                                   self.coins.append(partikl)
          for i in self.coins:
               i.render(экаран,(0,0))
               i.uptate(self.coins)




def Load_otems():

     xp_img = utils.load_image("graphics/font/hp.png",0.3)
     man_img = utils.load_image("map/double_jump.png",0.3)
     armor_img = utils.load_image("map/Image20260729110249.png",0.3)
     armor2_img = utils.load_image("map/Image20260729112747.png",0.3)
     itam = Item(100,100,"XP",{
          "трава": 3
     },xp_img)
     itam2 = Item(300,100,"man",{
          "трава": 2
     },man_img)
     itam3 = Item(100,300,"armor",{
          "трава" : 20,
          "огонь": 3
     },armor_img)
     itam4 = Item(300,300,"armor2",{
          "трава" : 150,
          "огонь": 10
     },armor2_img)
     return([itam4,itam3,itam2,itam])


def run(экран,plaer):
    cursor = utils.load_image('graphics/font/Image20260610104833.png',1)
    heart_cursor = utils.load_image("graphics/font/Icon_09.png",1)
    share.tip_cursor = 1
    clock = pygame.time.Clock()
    inventar = False
    items = Load_otems()
    clik = False
    fon = utils.load_image("graphics/font/Image20260610104742.png",3)
    fon = fon.subsurface(fon.get_bounding_rect())
    экран = pygame.display.set_mode((fon.get_width(),fon.get_height())) 
    while True:
        clock.tick(120)
        экран.fill((41, 18, 18))
        экран.blit(fon,(0,0))
        share.tip_cursor = 1
        for i in items:
             i.reneder(экран,clik,plaer)
        if inventar == True:
          
             inwentar.render(экран)
        clik = False
        for ev in pygame.event.get():
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    clik = True
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_k:
                            экран = pygame.display.set_mode((settings.WIDTH,settings.HEIGHT)) 
                            return
                    if ev.key == pygame.K_TAB:
                        inventar = not inventar          
                if ev.type == pygame.QUIT:
                    exit(0)
        XM = pygame.mouse.get_pos()[0] 
        yM = pygame.mouse.get_pos()[1]
        if share.tip_cursor == 1:
                экран.blit(cursor,(XM,yM))
        else:
                экран.blit(heart_cursor,(XM-heart_cursor.get_width()/2,yM-heart_cursor.get_height()/2))
        pygame.display.update()
