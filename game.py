# 1 - Import library
import pygame
from pygame.locals import *
import math
import random



def pause():
    #This is the pause function.Essentially it's a while loop that waits for the player to either press the pause button or press escape.
    pygame.mixer.music.pause()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0,0,0,100))
    screen.blit(overlay, (0, 0))
    menu_width, menu_height = 400, 250
    menu_x = (width - menu_width) // 2       #(1280-400) // 2
    menu_y = (height - menu_height) // 2     #(720-250) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    pygame.draw.rect(screen, (30, 30, 30), menu_rect, border_radius=12)
    pygame.draw.rect(screen, (255,255,255), menu_rect, 2, border_radius=12)

    # Text
    
    pause_text = font.render("Paused", True, (255,255,255))
    resume_text = small_font.render("Press ESC to Resume", True, (255,255,255))
    quit_text = small_font.render("Press Q to Quit", True, (255,255,255))
    
    # Center text inside the pause box
    screen.blit(pause_text, (menu_x + (menu_width - pause_text.get_width()) // 2, menu_y + 30))
    screen.blit(resume_text, (menu_x + (menu_width - resume_text.get_width()) // 2, menu_y + 100))
    screen.blit(quit_text, (menu_x + (menu_width - quit_text.get_width()) // 2, menu_y + 140))
    
    
    pause_start = pygame.time.get_ticks()
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   #if the player wants to exit the game , do it gracefully
                pygame.quit()
                exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit(0)
            elif event.type==MOUSEBUTTONDOWN: #here we check if the player presses the pause button to unpause
                position = pygame.mouse.get_pos()
                if (position[0] >= button[0]) and (position[0] <= button[0]+button[2]) and (position[1]>=button[1]) and (position[1]<=button[1]+button[3]):   #this lines checks if the mouse's position is inside the buttons rect(hitbox)
                    paused = False
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE: #if the presses escape again , unpause
                paused = False  # resume
            
        
        button = pygame.draw.circle(screen, (255, 255, 255), (width-30, 30), 20)
        pygame.draw.rect(screen, (0, 0, 0), (width-26, 18 ,7,25))
        pygame.draw.rect(screen, (0, 0, 0), (width-42, 18 ,7,25))
        pygame.display.flip()       #refresh the screen

    
    # return how long we were paused
    pause_duration = pygame.time.get_ticks() - pause_start  # this is the total time that the player was paused
    pygame.mixer.music.unpause()
    return pause_duration   #we return it to the main game loop so the timer doesn't keep on counting (we add the paused time to the remaining clicks)


# 2 - Initialize the game
pygame.init()
clock = pygame.time.Clock()
width, height = 1280, 720
screen=pygame.display.set_mode((width, height),pygame.RESIZABLE)
keys = [False, False, False, False]
playerpos=[100,100]
acc=[0,0]
arrows=[]
paused = False
badtimer=100
badtimer1=0
badguys=[[1280,100]]
healthvalue=256
start_time = pygame.time.get_ticks()
paused_time_total = 0
pygame.mixer.init()

# ----- LEVEL SELECTION SCREEN -----
# Fonts
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 32)

selecting = True
level = 1  # default level

while selecting:
    screen.fill((30, 30, 30))  # dark background
    title = font.render("CHOOSE LEVEL", True, (255, 255, 255))
    screen.blit(title, (width // 2 - 200, height // 2 - 150))
    
    font_small = pygame.font.Font(None, 50)
    screen.blit(font_small.render("1 - Level 1 (Easy)", True, (144,238,144)), (width // 2 - 150, height // 2 - 50))
    screen.blit(font_small.render("2 - Level 2 (Normal)", True, (255,165,0)), (width // 2 - 150, height // 2))
    screen.blit(font_small.render("3 - Level 3 (Hard)", True, (255,0,0)), (width // 2 - 150, height // 2 + 50))
    
    pygame.display.flip()  # update screen
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # exit game
            pygame.quit()
            exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:  # choose level 1
                level = 1
                selecting = False
            elif event.key == pygame.K_2:  # choose level 2
                level = 2
                selecting = False
            elif event.key == pygame.K_3:  # choose level 3
                level = 3
                selecting = False




# 3 - Load image
player = pygame.image.load("resources/images/dude.png")
grass = pygame.image.load("resources/images/grass.png")
castle = pygame.image.load("resources/images/castle.png")
arrow = pygame.image.load("resources/images/bullet.png")
badguyimg1 = pygame.image.load("resources/images/badguy.png")
badguyimg=badguyimg1
healthbar = pygame.image.load("resources/images/healthbar.png")
healthbar = pygame.transform.scale(healthbar,(263,20)) 
health = pygame.image.load("resources/images/health.png")
gameover = pygame.image.load("resources/images/gameover.png")
gameover = pygame.transform.scale(gameover,(1280,720))
youwin = pygame.image.load("resources/images/youwin.png")
youwin = pygame.transform.scale(youwin,(1280,720))

# 3.1 - Load audio
death = pygame.mixer.Sound("resources/audio/explode.wav")
hit = pygame.mixer.Sound("resources/audio/explode.wav")
enemy = pygame.mixer.Sound("resources/audio/enemy.wav")
shoot = pygame.mixer.Sound("resources/audio/shoot.wav")
hit.set_volume(0.05)
enemy.set_volume(0.05)
shoot.set_volume(0.1)
pygame.mixer.music.load('resources/audio/moonlight.wav')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.25)

# 4 - keep looping through
running = 1
exitcode = 0
while running:
    badtimer-=1
    # 5 - clear the screen before drawing it again
    screen.fill(0)
    
    # 6 - draw the player on the screen at X:100, Y:100
    for x in range(int(width/grass.get_width())+1):
        for y in range(int(height/grass.get_height())+1):
            screen.blit(grass,(x*100,y*100))
    screen.blit(castle,(0,30))
    screen.blit(castle,(0,135))
    screen.blit(castle,(0,240))
    screen.blit(castle,(0,345 ))
    screen.blit(castle,(0,450))
    screen.blit(castle,(0,555))
    
    # 6.1 - Set player position and rotation
    position = pygame.mouse.get_pos()
    angle = math.atan2(position[1]-(playerpos[1]+32),position[0]-(playerpos[0]+26))
    playerrot = pygame.transform.rotate(player, 360-angle*57.29)
    playerpos1 = (playerpos[0]-playerrot.get_rect().width/2, playerpos[1]-playerrot.get_rect().height/2)
    screen.blit(playerrot, playerpos1) 
    # 6.2 - Draw arrows
    for bullet in arrows:
        index=0
        velx=math.cos(bullet[0])*10
        vely=math.sin(bullet[0])*10
        bullet[1]+=velx
        bullet[2]+=vely
        if bullet[1]<-64 or bullet[1]>1280 or bullet[2]<-64 or bullet[2]>720:
            arrows.pop(index)
        index+=1
        for projectile in arrows:
            arrow1 = pygame.transform.rotate(arrow, 360 - projectile[0] * 57.29)
            screen.blit(arrow1, (projectile[1], projectile[2]))
    # 6.3 - Draw badgers
    if badtimer==0:
        for _ in range(1):
            badguys.append([1280, random.randint(30,600)])
            badtimer=100-(badtimer1*2)
        if badtimer1>=35:
            badtimer1=35
        else:
            badtimer1+=5
    index=0
    for badguy in badguys:
        if badguy[0]<-64:
            badguys.pop(index)
        badguy[0]-=2
        # 6.3.1 - Attack castle
        badrect=pygame.Rect(badguyimg.get_rect())
        badrect.top=badguy[1]
        badrect.left=badguy[0]
        if badrect.left<64:
            hit.play()
            healthvalue -= random.randint(5,20)
            badguys.pop(index)
        #6.3.2 - Check for collisions
        index1=0
        for bullet in arrows:
            bullrect=pygame.Rect(arrow.get_rect())
            bullrect.left=bullet[1]
            bullrect.top=bullet[2]
            if badrect.colliderect(bullrect):
                enemy.play()
                acc[0]+=1
                badguys.pop(index)
                arrows.pop(index1)
            index1+=1
        # 6.3.3 - Next bad guy
        index+=1
    for badguy in badguys:
        screen.blit(badguyimg, badguy)
    # 6.4 - Draw clock
    
    remaining_ms = 90000 - pygame.time.get_ticks() + paused_time_total
    minutes = remaining_ms // 60000
    seconds = (remaining_ms // 1000) % 60
    font = pygame.font.Font(None, 50)
    survivedtext = font.render(f"{minutes}:{str(seconds).zfill(2)} sec", True, (0, 0, 0))
    textRect = survivedtext.get_rect()
    textRect.topright=[700,5]
    screen.blit(survivedtext, textRect)
    # 6.5 - Draw health bar
    screen.blit(healthbar, (1000,690))
    for health1 in range(healthvalue):
        screen.blit(health, (health1+1004,693))
    # 6.6 - Draw a pause button
    button = pygame.draw.circle(screen, (255, 255, 255), (width-30, 30), 20)
    pygame.draw.rect(screen, (0, 0, 0), (width-26, 18 ,7,25))
    pygame.draw.rect(screen, (0, 0, 0), (width-42, 18 ,7,25))
    # 7 - update the screen
    pygame.display.flip()
    # 8 - loop through the events
    for event in pygame.event.get():
        # check if the event is the X button 
        if event.type==pygame.QUIT:
            # if it is quit the game
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key==K_w:
                keys[0]=True
            elif event.key==K_a:
                keys[1]=True
            elif event.key==K_s:
                keys[2]=True
            elif event.key==K_d:
                keys[3]=True
        if event.type == pygame.KEYUP:
            if event.key==pygame.K_w:
                keys[0]=False
            elif event.key==pygame.K_a:
                keys[1]=False
            elif event.key==pygame.K_s:
                keys[2]=False
            elif event.key==pygame.K_d:
                keys[3]=False
            elif event.key==pygame.K_ESCAPE:
                paused_time_total += pause()
        if event.type==pygame.MOUSEBUTTONDOWN:
            position = pygame.mouse.get_pos()
            if (position[0] >= button[0]) and (position[0] <= button[0]+button[2]) and (position[1]>=button[1]) and (position[1]<=button[1]+button[3]):
                paused_time_total += pause()
                
            shoot.stop()
            shoot.play()
            position=pygame.mouse.get_pos()
            acc[1]+=1
            arrows.append([math.atan2(position[1]-(playerpos1[1]+32),position[0]-(playerpos1[0]+26)),playerpos1[0]+32,playerpos1[1]+32])
                
    # 9 - Move player
    if keys[0]:
        if playerpos[1]>23:
           playerpos[1]-=5 
    elif keys[2]:
        if playerpos[1]<height-20:
            playerpos[1]+=5
    if keys[1]:
        if playerpos[0]>23:
            playerpos[0]-=5
    elif keys[3]:
        if playerpos[0]<width-20:
            playerpos[0]+=5

    #10 - Win/Lose check
    if pygame.time.get_ticks()>=90000+paused_time_total:
        running=0
        exitcode=1
    if healthvalue<=0:
        death.play()
        running=0
        exitcode=0
    if acc[1]!=0:
        accuracy=acc[0]*1.0/acc[1]*100
    else:
        accuracy=0
# 11 - Win/lose display        
if exitcode==0:
    pygame.mixer.music.stop()
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    text = font.render("Accuracy: {:.1f}%".format(accuracy), True, (255,0,0))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery+24
    img_rect = gameover.get_rect()
    img_rect.center = screen.get_rect().center 
    screen.blit(gameover, img_rect)
    screen.blit(text, textRect)
    
else:
    pygame.mixer.music.stop()
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    text = font.render("Accuracy: {:.1f}%".format(accuracy), True, (255,255,255))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery+24
    screen.blit(youwin, (0,0))
    screen.blit(text, textRect)
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
    clock.tick(30)
