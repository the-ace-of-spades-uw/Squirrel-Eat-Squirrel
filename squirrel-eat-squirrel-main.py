# Squirrel Eat Squirrel (a 2D Katamari Damacy clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
# ***Team intials: Asa L (AL), Meridan D (MD) Sarina S (SS)), Hoyt S (HS)***


# Importing differnt modules AL
import random, sys, time, math, pygame,os
# Import pygame locals into script namespace AL
from pygame.locals import *

# describes the window in which the game will appear on the screen   MD
FPS = 30 # frames per second to update the screen
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

# Differnt colours expressed as tuples of RGB values AL
GRASSCOLOR = (24, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (212,175,55) 

#assignment of the variables that will be used later in the creation of game functions   MD
CAMERASLACK = 90     # how far from the center the squirrel moves before moving the camera
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30    # how high the player bounces
STARTSIZE = 25       # how big the player starts off
WINSIZE = 300        # how big the player needs to be to win
INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3        # how much health the player starts with

NUMGRASS = 80        # number of grass objects in the active area
NUMSQUIRRELS = 30    # number of squirrels in the active area
SQUIRRELMINSPEED = 3 # slowest squirrel speed
SQUIRRELMAXSPEED = 7 # fastest squirrel speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'

#Relative path system using os module AL
game_folder = os.path.dirname(__file__)
assets_folder = os.path.join(game_folder, "assets")
sound_folder = os.path.join(game_folder,"sounds")

"""
This program has three data structures to represent the player, enemy squirrels, and grass background objects. The data structures are dictionaries with the following keys:

Keys used by all three data structures:
    'x' - the left edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'y' - the top edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'rect' - the pygame.Rect object representing where on the screen the object is located.
Player data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'facing' - either set to LEFT or RIGHT, stores which direction the player is facing.
    'size' - the width and height of the player in pixels. (The width & height are always the same.)
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'health' - an integer showing how many more times the player can be hit by a larger squirrel before dying.
Enemy Squirrel data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'movex' - how many pixels per frame the squirrel moves horizontally. A negative integer is moving to the left, a positive to the right.
    'movey' - how many pixels per frame the squirrel moves vertically. A negative integer is moving up, a positive moving down.
    'width' - the width of the squirrel's image, in pixels
    'height' - the height of the squirrel's image, in pixels
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'bouncerate' - how quickly the squirrel bounces. A lower number means a quicker bounce.
    'bounceheight' - how high (in pixels) the squirrel bounces
Grass data structure keys:
    'grassImage' - an integer that refers to the index of the pygame.Surface object in GRASSIMAGES used for this grass object
"""


def main():  #allows the runGame() function to be put into script at the end    MD
    """
    (None) -> None
    Loads images, surfacs, sounds and runs the main game AL
    """
    
    global FPSCLOCK, DISPLAYSURF, BASICFONT, SMALLFONT, MEDIUMFONT,L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES, BOUNCESOUND, bestTime
    
    pygame.init() #intialize python modules AL
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load(os.path.join(assets_folder,'gameicon.png'))) #sets the icon in windows title bar SS
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT)) #sets durface size of display SS
    pygame.display.set_caption('Squirrel Eat Squirrel') # sets caption text in title bar SS
    BASICFONT = pygame.font.Font(os.path.join(assets_folder, "gamefont.ttf"), 32) # sets new font object from file SS, changed font on game AL
    SMALLFONT = pygame.font.Font(os.path.join(assets_folder, "gamefont.ttf"), 12) # for smaller applications AL
    #load sound related items AL
    randomMusicInt = random.randint(0,100) #randomly select background music based on weighted average AL
    if 0 <= randomMusicInt < 45:
        BACKGROUNDMUSIC = pygame.mixer.music.load(os.path.join(sound_folder,'backgroundmusic1.mp3'))
    elif 45 <= randomMusicInt < 90:
        BACKGROUNDMUSIC = pygame.mixer.music.load(os.path.join(sound_folder,'backgroundmusic2.mp3'))
    elif 90 <= randomMusicInt <= 100:
        BACKGROUNDMUSIC = pygame.mixer.music.load(os.path.join(sound_folder,'backgroundmusic3.mp3'))

    #load sound effects AL
    BOUNCESOUND = pygame.mixer.Sound(os.path.join(sound_folder,'bouncesound.ogg')) #make sure to load sound effects as ogg AL
    BOUNCESOUND.set_volume(0.5)

    #Determine best time from file AL
    bestTime = int(readFromFile("besttime.txt"))

    # load the image files
    L_SQUIR_IMG = pygame.image.load(os.path.join(assets_folder,'squirrel.png')) # loads squirrel and enemy squirrel into code SS
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False)
    GRASSIMAGES = []
    for i in range(1, 5):
        GRASSIMAGES.append(pygame.image.load(os.path.join(assets_folder,'grass%s.png' % i)))

    while True:
        runGame()
        # loop that calls the game to run when main() is in the script   MD
        # starts game once setup is complete SS

def runGame():
    global bestTime
    
    pygame.mixer.music.rewind() #rewind the music before each newgame AL
    pygame.mixer.music.play(loops=-1) #play music and keep looping it AL
    # set up variables for the start of a new game
    invulnerableMode = False  # if the player is invulnerable
    invulnerableStartTime = 0 # time the player became invulnerable
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
    winMode = False           # if the player has won
    newBestMode = False       # if the player has beaten the previous best time AL

    gameStartTime = time.time() # record the start of a game relative to epoch AL

    # create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE) 
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = SMALLFONT.render('You have achieved OMEGA SQUIRREL!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = SMALLFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    #Best time text AL
    bestTimeMins = bestTime // 60 # formal best time in terms of mins and seconds, assuming user won't take over an hour to complete the game AL
    bestTimeSecs = bestTime - (bestTimeMins * 60)
    bestTimeSurf = SMALLFONT.render(("Best Time: " + str(bestTimeMins) + ":" + str(bestTimeSecs) ), True, WHITE)
    bestTimeRect = bestTimeSurf.get_rect()
    bestTimeRect.topright = (WINWIDTH - 10, 20) # Near the top left corner of screen AL

    # camerax and cameray are the top left of where the camera view is
    camerax = 0
    cameray = 0

    grassObjs = []    # stores all the grass objects in the game
    squirrelObjs = [] # stores all the non-player squirrel objects
    # stores the player object:
    # Can use key value pair to represent differnt types of squirrels AL
    playerObj = {'surface': pygame.transform.scale(L_SQUIR_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'health': MAXHEALTH}
    # keep track of what keys are being held pressed by user SS
    # allows for certain actions to happen when assigned to keys later on   MD
    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

    # start off with some random grass images on the screen
    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True: # main game loop
        # Check if we should turn off invulnerability
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME:
            invulnerableMode = False

        # move all the enemy squirrels
        # could reduce the bounce by decreasing BOUNCERATE to have levitating, ghost squrrels   MD
        for sObj in squirrelObjs:
            # move the squirrel, and adjust for their bounce
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            # adjust movement increments to make ultra fast vampire squirrels   MD
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0 # reset bounce amount

            # random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                if sObj['movex'] > 0: # faces right
                    sObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sObj['width'], sObj['height']))
                else: # faces left
                    sObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sObj['width'], sObj['height']))


        # go through all the objects and see if any need to be deleted.
        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(squirrelObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, squirrelObjs[i]):
                del squirrelObjs[i]

        # add more grass & squirrels if we don't have enough.
        # could adjust NUMGRASS to make a dense grass mode   MD
        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(camerax, cameray))
        while len(squirrelObjs) < NUMSQUIRRELS:
            squirrelObjs.append(makeNewSquirrel(camerax, cameray))

        # Find the distance between game world coordinates of the centre of the camera
        # and the game world codinates of the center of player, if this value is greater than cameraslack
        # move the camera a fixed distacne from the players center AL
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2)
        # move camera left AL
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        # move camera right AL
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        # move camera up AL
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        # move camera down AL
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        #******** DRAWING AL **********
        # draw the green background
        DISPLAYSURF.fill(GRASSCOLOR) 

        # draw all the grass objects on the screen
        for gObj in grassObjs:
            gRect = pygame.Rect( (gObj['x'] - camerax,
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)


        # draw the other squirrels
        for sObj in squirrelObjs:
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])


        # draw the player squirrel
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        # when player runs into enemy squirrel, they flash momentarily. this function creates the flashing effect   MD
        if not gameOverMode and not (invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect']) # could we change the graphics around the squirrel? SS


        # draw the health meter
        drawHealthMeter(playerObj['health'])

        DISPLAYSURF.blit(bestTimeSurf,bestTimeRect) #Display bestime text to screen AL

        # draw current time text AL
        currentTime = round(time.time() - gameStartTime, 1 )
        currentTimeSurf = SMALLFONT.render("Time: %s" % currentTime,True,WHITE).convert_alpha()
        currentTimeRect = currentTimeSurf.get_rect()
        currentTimeRect.topright= (WINWIDTH - 22,40)
        DISPLAYSURF.blit(currentTimeSurf,currentTimeRect)

        for event in pygame.event.get(): # event handling loop, if user exits the windown terminate program AL
            if event.type == pygame.QUIT:
                terminate()

            # Handle key down (pressing key) events AL
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w): #Either the up arrow key or (W) key can be used to move up AL
                    moveDown = False
                    moveUp = True
                elif event.key in (pygame.K_DOWN, pygame.K_s): #Either the down arrow key or (S) key can be used to move down AL
                    moveUp = False
                    moveDown = True
                elif event.key in (pygame.K_LEFT, pygame.K_a): #Either the left arrow key or (A) key can be used to move left AL
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT: # change the player image such that the sprite is facing left AL
                        playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d): #Either the right arrow key or (D) key can be used to move right AL
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT: # change player image such that the sprite is right AL
                        playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif winMode and event.key == pygame.K_r: 
                    return

            
            # Handle key up events (i.e if the user stops pressing a movement key stop moving the player) AL
            elif event.type == pygame.KEYUP:
                # stop moving the player's squirrel
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    moveLeft = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    moveRight = False
                elif event.key in (pygame.K_UP, pygame.K_w):
                    moveUp = False
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    moveDown = False
                elif event.key == pygame.K_ESCAPE: #Escape key can be used to quit program AL 
                    terminate()                    # terminates the game if esc is pressed SS

        if not gameOverMode:
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
                if not pygame.mixer.get_busy(): # ensures sound effect is played to completion before it is played again, might cause issues with later sound effects AL
                    BOUNCESOUND.play()
            if moveRight:
                playerObj['x'] += MOVERATE
                if not pygame.mixer.get_busy():
                    BOUNCESOUND.play()
            if moveUp:
                playerObj['y'] -= MOVERATE
                if not pygame.mixer.get_busy():
                    BOUNCESOUND.play()
            if moveDown:
                playerObj['y'] += MOVERATE
                if not pygame.mixer.get_busy():
                    BOUNCESOUND.play()

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # reset bounce amount

            # check if the player has collided with any squirrels
            for i in range(len(squirrelObjs)-1, -1, -1):
                sqObj = squirrelObjs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):
                    # a player/squirrel collision has occurred using pygames rect module to check AL
                    if sqObj['width'] * sqObj['height'] <= playerObj['size']**2:
                        # player is larger and eats the squirrel
                        playerObj['size'] += int( (sqObj['width'] * sqObj['height'])**0.2 ) + 1
                        # determines how much the player's squirrel grows each time they eat a smaller squirrel   MD

                        del squirrelObjs[i]

                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))

                        if playerObj['size'] > WINSIZE:
                            winMode = True # turn on "win mode"

                            
                            gameCompletionTime = time.time() - gameStartTime #the time it took to win relative to the start of that game AL
                            if gameCompletionTime < bestTime or bestTime == 0: # Check if current time is better than previous best AL
                                timeToSave = int(gameCompletionTime) # prepare new best timn for saving saved in mins AL
                                bestTime = timeToSave # store the new bes time AL
                                writeToFile("besttime.txt", str(timeToSave)) #Save the time to file AL
                                newBestMode = True #turn on the "new best mode" AL
                            

                    elif not invulnerableMode:
                        # player is smaller and takes damage
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True # turn on "game over mode"
                            gameOverStartTime = time.time()  
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            pygame.mixer.music.fadeout(int(time.time() - gameOverStartTime)) #fade out the music over aprox the time it take to start a new game AL
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return # end the current game

        # check if the player has won.
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)
        
        #check if player has set a new best time
        if newBestMode:
            newBestTimeSurf = BASICFONT.render('NEW BEST TIME !!!', True, WHITE)
            newBestTimeRect = newBestTimeSurf.get_rect()
            newBestTimeRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT - 80)
            
            newBestTimeMins = bestTime // 60
            newBestTimeSecs = bestTime - (60 * newBestTimeMins)
            newBestTimeSurf2 = SMALLFONT.render("new best: " + str(newBestTimeMins) + ":" + str(newBestTimeSecs), True, WHITE)
            newBestTimeRect2 = newBestTimeSurf2.get_rect()
            newBestTimeRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT - 40)

            DISPLAYSURF.blit(newBestTimeSurf,newBestTimeRect)   
            DISPLAYSURF.blit(newBestTimeSurf2, newBestTimeRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        # updates the display by defining the frames per second to previously set FPS = 30     MD




def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # draw red health bars, need to find a way to increase maxhealth but not above a limit AL
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    """
    (None) -> None
    Properly terminate program 
    """
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounceRate means a slower bounce.
    # Larger bounceHeight means a higher bounce.
    # currentBounce will always be less than bounceRate
    # Bounce height scales how high the player jumps, could use for powerups AL
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)

def getRandomVelocity(): # randomized speed of antagonist squirrels   MD
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED) #get a random integer speed between the min and the max AL
    if random.randint(0, 1) == 0: # basically 50% odds per function call for the speed to be appllied in one direction or the opposite AL
        return speed
    else:
        return -speed


# random position for new squirrels must be out of camera site but in the active area SS
def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y
    # function that defines the area in which new objects are randomly created   MD
    # they are created in the active area but outside of the camera view   MD

# creates new enemy squirrels  of different sizes with placement, speed and direction determined randomly SS
def makeNewSquirrel(camerax, cameray):
    """
    (int,int) -> dict
    Create a new squirrel "object"
    """
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width']  = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = getRandomVelocity()
    sq['movey'] = getRandomVelocity()
    if sq['movex'] < 0: # squirrel is facing left
        sq['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sq['width'], sq['height']))
    else: # squirrel is facing right
        sq['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq


def makeNewGrass(camerax, cameray):
    """
    (int,int) -> dict
    Create a new grass "object"
    """
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width']  = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr


def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)

def writeToFile (file, data):
    """
    (str, str) -> None 
    
    Writes data to specified file, data must be a String.
    """
    with open(file, "w") as f:
        f.write(data)

def readFromFile (file):
    """
    (str) -> str

    Returns data from a specfied file, if any error is run into returns None.
    """
    with open (file, "r") as f:
        try:
            return f.readline()
        except:
            return None

# script behaviour of program AL
if __name__ == '__main__':
    main()
