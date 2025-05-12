import random
import pygame
import sys
from pygame.locals import *

pygame.init()

FPS = 32
WIDTH = 289
HEIGHT = 512

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Generic Bird")

FPSCLOCK = pygame.time.Clock()
GROUNDY = HEIGHT * 0.87

SPRITES = {}
SOUNDS = {}

BACKGROUND = "Sprites/BACKGROUND1.png"
PLAYER = "Sprites/Bird.png"
PIPE = "Sprites/pipe.png"
BASE_IMAGE = "Sprites/base.png"
MESSAGE_IMAGE = "Sprites/MESSAGE1.png"

PIPE_WIDTH = 80
PIPE_HEIGHT = 350
GAP_BETWEEN_PIPES = 120
DIGIT_WIDTH = 30
DIGIT_HEIGHT = 30

last_lower_y = None

def main():
    pygame.init()
    pygame.mixer.init()

    bg_image = pygame.image.load(BACKGROUND).convert_alpha()
    SPRITES['background'] = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    base_img = pygame.image.load(BASE_IMAGE).convert_alpha()
    SPRITES['base'] = pygame.transform.scale(base_img, (WIDTH, int(HEIGHT * 0.15)))

    message_img = pygame.image.load(MESSAGE_IMAGE).convert_alpha()
    SPRITES['message'] = pygame.transform.scale(message_img, (WIDTH, int(HEIGHT * 0.87)))

    original_bird_w, original_bird_h = int(50*0.8),int (40*0.8)
    bird_img = pygame.image.load(PLAYER).convert_alpha()
    SPRITES['player'] = pygame.transform.scale(bird_img, (original_bird_w, original_bird_h))

    original_pipe = pygame.image.load(PIPE).convert_alpha()
    pipe_upper = pygame.transform.rotate(original_pipe, 180)
    pipe_upper = pygame.transform.scale(pipe_upper, (PIPE_WIDTH, PIPE_HEIGHT))
    pipe_lower = pygame.transform.scale(original_pipe, (PIPE_WIDTH, PIPE_HEIGHT))
    SPRITES['pipe'] = (pipe_upper, pipe_lower)

    digit_sprites = []
    for i in range(10):
        digit_path = f"Sprites/{i}.png"
        digit_img = pygame.image.load(digit_path).convert_alpha()
        digit_img = pygame.transform.scale(digit_img, (DIGIT_WIDTH, DIGIT_HEIGHT))
        digit_sprites.append(digit_img)
    SPRITES['numbers'] = (digit_sprites)

    SOUNDS['die'] = pygame.mixer.Sound("Sprites/sfx/die.MP3")
    SOUNDS['hit'] = pygame.mixer.Sound("Sprites/sfx/hit.MP3")
    SOUNDS['swoosh'] = pygame.mixer.Sound("Sprites/sfx/swoosh.MP3")
    SOUNDS['point'] = pygame.mixer.Sound("Sprites/sfx/point.MP3")

    pygame.mixer.music.load("Sprites/sfx/background.MP3")
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1)
    
def welcomeScreen():
    playerx = int(WIDTH / 5)
    playery = int(HEIGHT/2)
    messagex = 0
    messagey = int(HEIGHT * 0.08)
    basex = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        SCREEN.blit(SPRITES['background'], (0, 0))
        SCREEN.blit(SPRITES['player'], (playerx, playery))
        SCREEN.blit(SPRITES['message'], (messagex, messagey))
        SCREEN.blit(SPRITES['base'], (basex, GROUNDY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def mainGame():
    score = 0
    px = int(WIDTH / 5)
    py = int(HEIGHT / 2)
    bx = 0

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    upperPipes = [
        {'x': WIDTH + 200, 'y': newPipe1[0]['y'], 'scored': newPipe1[0]['scored']},
        {'x': WIDTH + 200 + (WIDTH / 2), 'y': newPipe2[0]['y'], 'scored': newPipe2[0]['scored']},
    ]
    lowerPipes = [
        {'x': WIDTH + 200, 'y': newPipe1[1]['y'], 'scored': newPipe1[1]['scored']},
        {'x': WIDTH + 200 + (WIDTH / 2), 'y': newPipe2[1]['y'], 'scored': newPipe2[1]['scored']},
    ]

    pipeVelocityX = -5 # SPEED OF PIPES MOVING TO LEFT
    playerVelocityY = -10 #player velocity from starting the game if its in positive it will fell on the ground
    playerMaxVelocityY = 10
    playerAccY = 1 # DEFAULT 1 IF WE INCREASE IT THERE WILL BE UNCERTAINTY
    playerFlapAccV = -8 # HELPS IN THE JUMPING
    playerFlapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if py > 0:
                    playerVelocityY = playerFlapAccV
                    playerFlapped = True
                    SOUNDS['swoosh'].play()

        if isCollide(px, py, upperPipes, lowerPipes):
            return
#function passes if the bird passes through the pipe
        playerMidPos = px + SPRITES['player'].get_width()/2 # for checking if our player corss the center of pipe then add 1 in our score
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + SPRITES['pipe'][0].get_width()/2 # center of pipe
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"your score is {score}") # f-string realtime added values
                SOUNDS['point'].play()
                print(f"Score: {score}")

#cotrol birds movements
        if playerVelocityY < playerMaxVelocityY and not playerFlapped: 
            playerVelocityY += playerAccY #simulates gravity
        if playerFlapped:
            playerFlapped = False

        playerHeight = SPRITES['player'].get_height()
        py = py + min(playerVelocityY, GROUNDY - py - playerHeight)# whenever the bird falls on the base the game ends not helping the bird to sink in the ground for forver

        for upipe, lpipe in zip(upperPipes, lowerPipes): #to make upper and lower pipein the same frame
            upipe['x'] += pipeVelocityX
            lpipe['x'] += pipeVelocityX

        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append({
                'x': newPipe[0]['x'],
                'y': newPipe[0]['y'],
                'scored': newPipe[0]['scored']
            })
            lowerPipes.append({
                'x': newPipe[1]['x'],
                'y': newPipe[1]['y'],
                'scored': newPipe[1]['scored']
            })

        if upperPipes[0]['x'] < -SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        SCREEN.blit(SPRITES['background'], (0, 0))
        for upipe, lpipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(SPRITES['pipe'][0], (upipe['x'], upipe['y']))
            SCREEN.blit(SPRITES['pipe'][1], (lpipe['x'], lpipe['y']))
        SCREEN.blit(SPRITES['base'], (bx, GROUNDY))
        SCREEN.blit(SPRITES['player'], (px, py))
        showScore(score)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(px, py, upperPipes, lowerPipes):
    playerRect = pygame.Rect(px, py, SPRITES['player'].get_width(), SPRITES['player'].get_height())
    if py >= GROUNDY - SPRITES['player'].get_height():
        SOUNDS['die'].play()
        return True

    for pipe in upperPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], SPRITES['pipe'][0].get_width(), SPRITES['pipe'][0].get_height())
        if playerRect.colliderect(pipeRect):
            SOUNDS['die'].play()
            return True
        

    for pipe in lowerPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], SPRITES['pipe'][1].get_width(), SPRITES['pipe'][1].get_height())
        if playerRect.colliderect(pipeRect):
            SOUNDS['die'].play()
            return True

    return False

def getRandomPipe():
    global last_lower_y
    pipeHeight = SPRITES['pipe'][1].get_height()
    minBottomY = int(HEIGHT / 5)
    maxBottomY = int(GROUNDY - (GAP_BETWEEN_PIPES + 50 )) 

    while True:
        yLower = random.randint(minBottomY, maxBottomY)
        if yLower != last_lower_y:
            last_lower_y = yLower
            break

    pipeX = WIDTH + 10  # for the smooth appearance of the pipe after another pipe
    yUpper = yLower - GAP_BETWEEN_PIPES - pipeHeight
    pipe = [
        {'x': pipeX, 'y': yUpper, 'scored': False},
        {'x': pipeX, 'y': yLower, 'scored': False},
    ]
    if pipe[0]['y'] < -(pipeHeight - 20):
        pipe[0]['y'] = -(pipeHeight - 20)
    return pipe

def showScore(score):
    digits = [int(x) for x in str(score)]
    total_width = sum(SPRITES['numbers'][digit].get_width() for digit in digits)
    xoffset = (WIDTH - total_width) / 2
    for digit in digits:
        SCREEN.blit(SPRITES['numbers'][digit], (xoffset, HEIGHT * 0.12))
        xoffset += SPRITES['numbers'][digit].get_width()


while True:
    main()
    welcomeScreen()
    mainGame()