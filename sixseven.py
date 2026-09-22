import pygame 
import dialog
import random
import kvest
from scripts import settings
from scripts import antites
from scripts import map
from scripts import grass
from scripts import inwentar
from scripts import particlas
from scripts import widget
from scripts import batl
from scripts import share
from scripts import master
from scripts import market as magazin
from scripts import utils
from casino_game import casino_game

pygame.init()

экран = pygame.display.set_mode((settings.WIDTH,settings.HEIGHT))
batl.load_fon()
glass_1 = pygame.Surface((settings.WIDTH,settings.HEIGHT),pygame.SRCALPHA)
glass_dark = pygame.Surface((settings.WIDTH,settings.HEIGHT),pygame.SRCALPHA)
часы = pygame.time.Clock()
карта = map.КАРТА67()
NPCs_dio = []
level3 = False
ent = antites.Entity(100,100,5,80,50,карта)
pl = antites.Playr(31535,1460,10,карта)
npc1 = antites.Spirit_diologNPC(31535,1460,карта,"over")
npc2 = antites.Spirit_diologNPC(32173,1460,карта,"GG")
NPCs_dio.append(npc1)
NPCs_dio.append(npc2)
#:)

иветнтарь = False
враги = antites.kreate_anmy(карта)
cursor = utils.load_image('graphics/font/Image20260610104833.png',1)
heart_cursor = utils.load_image("graphics/font/Icon_09.png",1)
tip_cursor = 1
pygame.mouse.set_visible(False)
partikals = []
steat = "game"
clik = False
font = pygame.font.Font(None,100)
press_f_image = font.render('press "F"',1,(42,42,42))
def rectart():
      global pl
      pl = antites.Playr(750,325,10,карта)
share.rectart = rectart
def slot_con():
      global steat
      steat = "game"
def inkris_exp(kol_vo = 1):
     pl.exp += kol_vo
share.inkris_exp = inkris_exp
share.pl = pl
share.level3 = level3
levlel = 1     
bombutp = utils.load_trlrport()
market = utils.load_market()
casino = utils.load_casino()
inwentar.load()
widget = widget.Button(settings.WIDTH/2-100,300,200,50,"black","yellow","continue","white","black",55)
widget.slot = slot_con
def run():
     expant = 120
     cllapst = 0
     global steat,иветнтарь
     while True:
        
          if npc1.HP <= 0 and npc1 in NPCs_dio:
                         карта.vorota = []
                         NPCs_dio.remove(npc1)     
          if npc2.HP <= 0 and npc2 in NPCs_dio:
                                   карта.vorota = []
                                   NPCs_dio.remove(npc2)     
          if steat == "game":
               pl.ener += 0.002
               #print(pl.exp)
               if pl.ener >= 100:
                    pl.ener = 100
               экран.fill((0,0,0))
               #print(str(pl.exp))
               XM = pygame.mouse.get_pos()[0] 
               yM = pygame.mouse.get_pos()[1]
               pygame.display.set_caption(str((XM+карта.камера[0],yM+карта.камера[1])))
               if  dialog.in_dialog == False:
                    pl.x += (XM+карта.камера[0] - pl.x) /5
                    pl.y += (yM+карта.камера[1] - pl.y) /5
                    pass
               
               часы.tick(settings.FPS)
               ent.update()
               ent.render(экран)
               карта.render(экран)
               карта.камера[0] += (pl.x-экран.get_width()/2-карта.камера[0])
               карта.камера[1] += (pl.y-экран.get_height()/2-карта.камера[1])
               карта.камера[0] = int(карта.камера[0])
               карта.камера[1] = int(карта.камера[1])
               карта.камера[0] = max(0,карта.камера[0])
               карта.камера[1] = max(0,карта.камера[1])
               карта.камера[0] = min(карта.камера[0],карта.карта.get_width() - экран.get_width())
               карта.камера[1] = min(карта.камера[1],карта.карта.get_height() - экран.get_height())
               if len(враги) < 2:
                    врг = antites.Spirit(random.randint(1000,4000),random.randint(500,3000),карта)
                    враги.append(врг)
               for i in partikals:
                    i.render(экран,карта.камера)
                    i.uptate(partikals)
               pl.update()
               pl.render(экран,карта.камера)
               for i in NPCs_dio:
                    i.render(экран,карта.камера)
                    i.uptate()
               for i in враги:
                    i.render(экран,карта.камера)
                    i.update(враги) 
               inwentar.combo(экран)
               if иветнтарь == True:
                    inwentar.render(экран)
                    inwentar.utate()
    
               pl.render_hp(экран) 
               clik = False
               
               if иветнтарь == True:
                    inwentar.render(экран)
                    inwentar.utate()
               
               for ev in pygame.event.get():
                         if ev.type == pygame.MOUSEBUTTONDOWN:
                              clik = True
                         if ev.type == pygame.QUIT:
                              exit(0)
                         if ev.type == pygame.KEYDOWN:
                              if ev.key == pygame.K_SPACE:
                                   pass
                              if ev.key == pygame.K_a and dialog.in_dialog == False:
                                   pl.runl = True
                              if ev.key == pygame.K_k:
                                   pl.HP = 0
                              if ev.key == pygame.K_d and dialog.in_dialog == False:
                                   pl.runr = True
                              if ev.key == pygame.K_j and dialog.in_dialog == False:
                                   inkris_exp(100)
                              if ev.key == pygame.K_w and dialog.in_dialog == False:
                                   pl.runu = True
                              if ev.key == pygame.K_s and dialog.in_dialog == False:
                                   pl.rund = True
                              if ev.key == pygame.K_t:
                                   inwentar.add_inwentar("огонь",(random.randint(1,100)))
                              for i in NPCs_dio:
                                   if ev.key == pygame.K_f and  i.cehk_for_dialog(pl) == True and i.live == True:
                                        dialog.start_dialog(i.name)
                                        share.nps = i
                              if ev.key == pygame.K_TAB:
                                   иветнтарь = not иветнтарь
                              if ev.key == pygame.K_ESCAPE:
                                   steat = "pause"
                                   glass_1.blit(экран,(0,0))
                         if ev.type == pygame.KEYUP:
                              if ev.key == pygame.K_a:
                                   pl.runl = False
                              if ev.key == pygame.K_d:
                                   pl.runr = False
                              if ev.key == pygame.K_w:
                                   pl.runu = False         
                              if ev.key == pygame.K_s:
                                   pl.rund = False
               for i in bombutp: 
                    if pl.get_bx().colliderect(i):
                         pygame.draw.rect(экран,(255,0,0),(100,100,1000,1000))
               if share.level3 == True and cllapst == 0:
                     cllapst = 120

               for i in market:
                    if pl.get_bx().colliderect(i):
                         if pygame.key.get_pressed()[pygame.K_f]:
                              magazin.run(экран,pl)
                         #pygame.draw.rect(экран,(255,0,100),(i.move(-карта.камера[0],-карта.камера[1])))
                         экран.blit(press_f_image,(settings.WIDTH/2-press_f_image.get_width()/2,300))  
               for i in casino:
                    if pl.get_bx().colliderect(i):
                         if pygame.key.get_pressed()[pygame.K_f]:
                                   casino_game.run()
                         #pygame.draw.rect(экран,(255,0,100),(i.move(-карта.камера[0],-карта.камера[1])))
                         экран.blit(press_f_image,(settings.WIDTH/2-press_f_image.get_width()/2,300))  
                    
               dialog.render(экран,clik)
               if expant != 0:
                    expant -= 1
                    glass_dark.fill("black")
                    pygame.draw.circle(glass_dark,(0,0,0,0),(settings.WIDTH/2,settings.HEIGHT/2),-settings.WIDTH/240*expant+settings.WIDTH/2)
                    экран.blit(glass_dark,(0,0))
               if cllapst != 0:
                    cllapst -= 1
                    glass_dark.fill("black")
                    pygame.draw.circle(glass_dark,(0,0,0,0),(settings.WIDTH/2,settings.HEIGHT/2),cllapst*5)
                    экран.blit(glass_dark,(0,0))
                    if cllapst == 0:
                         return
               экран.blit(cursor,(XM,yM))
               pygame.display.update()

          if steat == "pause":
               glass_dark.fill((0,0,0,200))
               экран.blit(glass_1,(0,0))
               экран.blit(glass_dark,(0,0))
               #smoth = pygame.transform.smoothscale(экран,(settings.WIDTH/2,settings.HEIGHT/2),экран)
               #экран.blit(smoth,(0,0))
               widget.render(экран)     
               widget.update(clik)  
               clik = False
               for ev in pygame.event.get():
                    if ev.type == pygame.MOUSEBUTTONDOWN:
                              clik = True
                    if ev.type == pygame.QUIT:
                              exit(0)
                    if ev.type == pygame.KEYDOWN:
                         if ev.key == pygame.K_ESCAPE:
                                   steat = "game"
               экран.blit(cursor,(XM,yM))
               pygame.display.update()