import pygame
import os
import time
import random
import math
import threading

WINDOW_W = 1000
pygame.init()
WINDOW_H = 600
pygame.font.init()
WINDOW = pygame.display.set_mode((WINDOW_W,WINDOW_H))
pygame.display.set_caption("美丽的谷歌小恐龙")


NORMAL_FONT = pygame.font.SysFont("comicans",30)
BIG_FONT = pygame.font.SysFont("comicans",50)


def LoadImage(name):
    return pygame.transform.scale2x(pygame.image.load(os.path.join("assets",name)).convert_alpha())

def LoadImageWithSize(name,size):
    return pygame.transform.scale(pygame.image.load(os.path.join("assets",name)).convert_alpha(), size)


CactusScales = [(45,100),(70,100),(80,100),(30,60)]

DinoImages = [LoadImageWithSize("dino"+str(x) + ".png",(100,100)) for x in range(1,5)]
CactusImages = [LoadImageWithSize("cactus"+str(x)+".png",CactusScales[x-1]) for x in range(1,5)]
BirdImages = [LoadImage("bird"+str(x)+".png") for x in range(1,3)]
GroundImage = LoadImage("ground.png")
CloudImage = LoadImage("cloud.png")
FallingStoneImage = LoadImage("falling_stone.png")
StoneImage = LoadImage("stone.png")
LightingImage = LoadImage("lighting.png")


class Sound():
    def __init__(self):
        self.jumpSound = pygame.mixer.Sound("./assets/audios/jump.wav")
        self.dieSound = pygame.mixer.Sound("./assets/audios/die.wav")
        self.rushSound = pygame.mixer.Sound("./assets/audios/rush.wav")
        self.explosionSound = pygame.mixer.Sound("./assets/audios/explosion.wav")
    
    def jump(self):
        pygame.mixer.Sound.play(self.jumpSound)
    
    def die(self):
        pygame.mixer.Sound.play(self.dieSound)
    
    def rush(self):
        pygame.mixer.Sound.play(self.rushSound)
    
    def explosion(self):
        pygame.mixer.Sound.play(self.explosionSound)






sound = Sound()



class FallingStone:
    INIT_Y = -30
    IMAGE = FallingStoneImage
    TRUE = StoneImage

    def __init__(self,v):
        self.image = self.IMAGE
        self.true = self.TRUE
        self.v = (-1.2*v,0.45*v)
        self.y = self.INIT_Y
        self.x = random.uniform(500,WINDOW_W+500)

    def move(self):
        self.x += self.v[0]
        self.y += self.v[1]

    def render(self,window):
        window.blit(self.image,(self.x,self.y))

    def crash(self):
        sound.explosion()

    def collide(self,dino,window):
        dino_mask = dino.get_mask()
        stone_mask= pygame.mask.from_surface(self.true)
        offset = (round(self.x-dino.x),round(self.y-dino.y))
        return dino_mask.overlap(stone_mask,offset)
    








class Ground:
    INIT_Y = 485
    IMAGE = GroundImage
    SectionWidth = 100
    INIT_V = 10

    def __init__(self):
        self.image = self.IMAGE
        self.v = self.INIT_V
        self.x = 0
        self.section_count =  math.ceil(WINDOW_W/self.SectionWidth) +1

    def setSpeed(self,v):
        self.v = v 

    def move(self):
        self.x -= self.v
        if self.x < (0-self.SectionWidth):
            self.x = 0

    def render(self,window):
        for i in range(self.section_count):
            window.blit(self.image,(self.x + i*self.SectionWidth,self.INIT_Y))


class Cactus:
    Ground_Y = 490
    INIT_X = WINDOW_W + 100
    IMAGES = CactusImages
    Scales = CactusScales
    def __init__(self,v):
        self.x = self.INIT_X
        self.typeIndex = random.randrange(0,len(self.IMAGES))
        self.image = self.IMAGES[self.typeIndex]
        self.y = self.Ground_Y - self.Scales[self.typeIndex][1]
        self.v = v
        self.passed = False

    def move(self):
        self.x -= self.v


    def collide(self,dino,window):
        dino_mask = dino.get_mask()
        cactus_mask = pygame.mask.from_surface(self.image)
        offset = (round(self.x-dino.x),round(self.y-dino.y))
        return dino_mask.overlap(cactus_mask,offset)


    def render(self,window):
        window.blit(self.image,(self.x,self.y))
    

class Bird:
    IMAGES = BirdImages
    INIT_X = WINDOW_W + 100
    Frequency = 4
    Base = 440
    Span = 50

    
    def __init__(self,v):
        self.image_index= 0
        self.image = self.IMAGES[self.image_index]
        self.v = v
        typeIndex = random.randrange(0,3)
        self.y = self.Base - typeIndex * self.Span
        self.x = self.INIT_X
        self.fre_count = 0
        self.passes = False
    
    def move(self):
        self.x -= self.v
        self.fre_count += 1
        if(self.fre_count%self.Frequency==0):
            self.fre_count =0
            self.image_index += 1
            if(self.image_index == 2):
                self.image_index = 0
            self.image = self.IMAGES[self.image_index]
    
    def collide(self,dino,window):
        dino_mask = dino.get_mask()
        bird_mask= pygame.mask.from_surface(self.image)
        offset = (round(self.x-dino.x),round(self.y-dino.y))
        return dino_mask.overlap(bird_mask,offset)

    def render(self,window):
        window.blit(self.image,(self.x,self.y))




    

class Dino:
    INIT_Y = 400
    INIT_X = 50
    IMAGES = DinoImages
    INIT_VX = 10
    JUMP_V = 40
    V_A = 4
    Frequency = 5
    RUSH_DIS = 120 
    LIGHTING_IMAGE = LightingImage

    
    def __init__(self):
        self.x = self.INIT_X
        self.y = self.INIT_Y
        self.img_index = 0
        self.status = 0
        self.tick_count = 0
        self.fre_count =0
        self.vel_x = self.INIT_VX
        self.vel_y = 0
        self.img = self.IMAGES[self.img_index]
        self.die = False
        self.lightingImage = pygame.transform.scale(self.LIGHTING_IMAGE,(self.RUSH_DIS,32))
        self.rushing = False
        self.rushAble = False


    def jump(self):
        if(self.status == 1):
            return
        self.vel_y = 0-self.JUMP_V
        self.tick_count = 0 
        self.status = 1
        sound.jump()

    def creep(self):
        if(self.status == 1):
            return
        self.status = 2

    def godie(self):
        self.status = 3
        self.die = True
        sound.die()

    def stand(self):
        if(self.status != 2):
            return
        self.img_index = 0
        self.img = self.IMAGES[self.img_index]
        self.status = 0

    def rush(self):
        if(self.rushAble):
            self.rushAble = False
            self.x += self.RUSH_DIS
            self.rushing = True
            sound.rush()
            th1 = threading.Thread(target=self.stoprush)
            th2 = threading.Thread(target=self.recoverRush)
            th1.start()
            th2.start()

    def recoverRush(self):
        time.sleep(1)
        self.rushAble = True

    def stoprush(self):
        time.sleep(0.2)
        self.rushing = False

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def move(self):

        if(self.status == 1):
            self.tick_count += 1
            self.y = self.INIT_Y + self.vel_y*(self.tick_count) + 0.5*self.V_A*((self.tick_count)**2)
            if self.y > self.INIT_Y:
                self.y = self.INIT_Y
                self.status = 0
        else:
            if self.x > self.INIT_X:
                self.x -= (self.x-self.INIT_X)/30


    def render(self,window):


        if(self.status == 0):
            self.fre_count += 1
            if self.fre_count % self.Frequency == 0:
                self.fre_count = 0
                self.img_index += 1
            self.img = self.IMAGES[self.img_index%2]
        
        elif(self.status == 1):
            self.img = self.IMAGES[1]

        elif(self.status == 2):
            self.img = self.IMAGES[2]

        elif(self.status == 3):
            self.img = self.IMAGES[3]

        if(self.rushing):
            window.blit(self.lightingImage,(self.INIT_X+40,self.y+32))
        
        window.blit(self.img,(self.x,self.y))


class Background():
    
    def __init__(self):
        self.clouds = [Cloud()]

    def move(self):
        for cloud in self.clouds:
            cloud.move()
            if(cloud.x<-100):
                self.clouds.remove(cloud)

        lastCloud = self.clouds[len(self.clouds)-1]
        if(lastCloud.x<WINDOW_W - 300 + random.uniform(0,150)):
            self.clouds.append(Cloud())
        


    def render(self,window):
        for cloud in self.clouds:
            cloud.render(window)

class Cloud():
    IMAGE = CloudImage
    INIT_X = WINDOW_W + 20
    
    def __init__(self):
        self.img = self.IMAGE
        self.x = self.INIT_X
        self.y = random.uniform(10,300)
        self.v = random.uniform(8,15)
        # self.v = 10

    def move(self):
        self.x -= self.v

    def render(self,window):
        window.blit(self.img,(self.x,self.y))


    


def play(window):
    run = True

    dino = Dino()
    ground = Ground()
    clock = pygame.time.Clock()

    obt_v = 14
    obt_a = 0.005
    smallest_span = WINDOW_W -100
    span_a = 0.05
    score = 0

    obts = [Cactus(obt_v)]
    stones = []
    background = Background()

    while run:
        clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

            if event.type == pygame.KEYDOWN:
                if(event.key == pygame.K_SPACE):
                    if(dino.die):
                        dino = Dino()
                        obt_v = 14
                        smallest_span = WINDOW_W - 100
                        score = 0
                        obts = [Cactus(obt_v)]
                        stones = []

                elif(event.key == pygame.K_UP):
                    dino.jump()

                elif(event.key == pygame.K_DOWN):
                    dino.creep()
                elif(event.key == pygame.K_RIGHT):
                    dino.rush()
                

            elif event.type == pygame.KEYUP and (event.key == pygame.K_DOWN):
                dino.stand()

        if(dino.die):
            continue

        obt_v += obt_a

        if(obt_v>24):
            obt_v =24
        smallest_span -= span_a

        if(smallest_span<300):
            smallest_span = 300


        if(score > 1600):
            for i in range(10):
                stones.append(FallingStone(obt_v))


        score += 1


        state = pygame.key.get_pressed()
        if state[pygame.K_DOWN]:
            dino.creep()



        dino.move()
        ground.move()
        background.move()

        if(len(stones)==0 and score > 1200):
            dino.rushAble = True
            stones.append(FallingStone(obt_v))


        for obt in obts:
            obt.move()
            if(obt.collide(dino,window)):
                # run = False
                dino.godie()

            if obt.x < -200:
                obts.remove(obt)


        for stone in stones:
            stone.move()
            if(stone.collide(dino,stone)):
                dino.godie()
            
            if(stone.y>430):
                stone.crash()
                stones.remove(stone)
                stones.append(FallingStone(obt_v))

        
        if(obts[len(obts)-1].x < WINDOW_W - random.uniform(smallest_span,WINDOW_W)):
            # if(2000<1800):
            if(score<600):
                obts.append(Cactus(obt_v))
            else:
                if(random.uniform(0,1)>0.5):
                    obts.append(Cactus(obt_v))
                else:
                    obts.append(Bird(obt_v))


        renderAll(window,dino,ground,obts,background,score,stones,dino.die)

    


def renderAll(window,dino,ground,obts,background,score,stones,die):
    drawBackground(window)
    background.render(window)
    ground.render(window)
    
    for obt in obts:
        obt.render(window)

    dino.render(window)

    for stone in stones:
        stone.render(window)



    score_label = NORMAL_FONT.render("score: " + str(score),1,(0,0,0))

    window.blit(score_label,(WINDOW_W-110,10))

    if die:
        die_label= BIG_FONT.render("GAME OVER",1,(0,0,0))
        window.blit(die_label,(WINDOW_W/2-100,WINDOW_H/2-50))

    rushable_text = "rushable: "
    if(dino.rushAble):
        rushable_text += "true"
        rushable_label = NORMAL_FONT.render(rushable_text,1,(0,255,0))
    else:
        rushable_text += "false"
        rushable_label = NORMAL_FONT.render(rushable_text,1,(255,0,0))

    window.blit(rushable_label,(WINDOW_W-280,10))


    pygame.display.update()


def drawBackground(window):
    background = pygame.Surface((WINDOW_W,WINDOW_H))
    background.fill((255,255,255))
    window.blit(background,(0,0))



if __name__ == "__main__":
    play(WINDOW)

        











