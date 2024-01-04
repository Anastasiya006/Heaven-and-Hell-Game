#############################################
## File Name: main.py
## Description: a platformer with two different kinds of gravities; characters are controlled with the same keys
#############################################

import pygame
import math
import levels

pygame.init()
clock = pygame.time.Clock()
FPS = 60

# screen attributes
SCREEN_WIDTH = 1296
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Heaven and Hell')

# maps
current_level_map = [levels.level1_map, levels.level2_map, levels.level3_map, levels.level4_map, levels.level5_map,
                     levels.level6_map, levels.level7_map, levels.level8_map, levels.level9_map, levels.level10_map,
                     levels.level11_map, levels.level12_map, levels.level13_map, levels.level14_map, levels.level15_map]

# diamonds collected variables
collected_blue = 0 # amount of blue diamonds collected per level
blue_diamonds_req = 0 # amount of blue diamonds required to be collected per level
collected_red = 0 # amount of red diamonds collected per level
red_diamonds_req = 0 # amount of red diamonds required to be collected per level

# holds all the blocks (diamonds, doors) that are removed from the level
# so that they can be reinserted if they player dies or resets the level
deleted_blocks = []

# lives
lives = 3

# colours
BLACK = (0, 0, 0)

# tile attributes
TILE_SCALE = 48 # the number all the game tiles are scaled by

# player coordinate attributes (starting position for each level)
angel_x = 0
angel_y = 0
devil_x = 0
devil_y = 0

jump_speed = -16
gravity = 1
doublejump = 0

# scrolling variables
bg_scroll_num = 0 # cloud background scrolling
level_scroll_num = 0 # level scrolling

# level attributes
current_level = 1 # current level player is on
levels_unlocked = 1 # number of total levels a player has unlocked

# screens
start = True # start screen
objective = False # explanation of game objective
controls = False # explanation of game controls
level_selection = False # level selection screen
game = False # game
gameover = False # gameover screen

## music & sound
music = True
pygame.mixer.music.load("BG MUSIC.wav")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1) # infite music loop

diamond_collected = pygame.mixer.Sound('DIAMOND_COLLECT.ogg')

# functions and classes
def side_panel():
    global lives
    unused_lives = [(15.5, 20), (15.5, 54), (15.5, 88)] # list of images of unused hearts
    used_lives = [(15.5, 20), (15.5, 54), (15.5, 88)] # list of images of used hearts
    screen.blit(pygame.image.load('SIDE PANEL/PANEL.png'), (0, 0))
    screen.blit(pygame.image.load('SIDE PANEL/PANEL.png'), (1219, 0))
    font = pygame.font.SysFont("Helvetica", 20)
    # diamond counter
    blue_diamonds_text = font.render(str(collected_blue) + "/" + str(blue_diamonds_req), True, BLACK) # displays the number of blue diamonds you have collected in comparision to the total amount you must collect
    red_diamonds_text = font.render(str(collected_red) + "/" + str(red_diamonds_req), True, BLACK) # displays the number of red diamonds you have collected in comparision to the total amount you must collect
    screen.blit(pygame.transform.scale(pygame.image.load('GAME TILES/TILE_B10.png'), (48, 48)), (15.5, 198))
    screen.blit(blue_diamonds_text, (24, 178))
    screen.blit(pygame.transform.scale(pygame.image.load('GAME TILES/TILE_R10.png'), (48, 48)), (15.5, 522))
    screen.blit(red_diamonds_text, (24, 572))
    # lives remaining
    for i in range(0, 3):
        if i == lives - 1:
            for x in range(0, i + 1):
                screen.blit(pygame.transform.scale(pygame.image.load('SIDE PANEL/HEART_ALIVE.png'), (48, 48)), (unused_lives[x])) # displays the amount of unused hearts (lives left)
        elif i < lives - 1:
            for x in range(0, i + 1):
                screen.blit(pygame.transform.scale(pygame.image.load('SIDE PANEL/HEART_DEAD.png'), (48, 48)), (used_lives[x])) # displays the amount of used hearts (lives used)
        else:
            screen.blit(pygame.transform.scale(pygame.image.load('SIDE PANEL/HEART_DEAD.png'), (48, 48)), (used_lives[i])) # displays the amount of used hearts (lives used)

def background_scroll(bg, scroll_num):
    global bg_scroll_num
    bg_width = bg.get_width()
    tiles = math.ceil(SCREEN_WIDTH / bg_width) + 1 # number of background images required to fill the screen
    for i in range(0, tiles):
        screen.blit(bg, (i * bg_width + bg_scroll_num, 0))

    bg_scroll_num  -= scroll_num # the x coordinate of each image that makes up the background is slowly shifted leftwards

    if abs(bg_scroll_num) > bg_width:
        bg_scroll_num = 0 # scroll number if reset if it exceeds the width of the screen

def reset(): # reset everything
    global collected_blue, collected_red, lives, deleted_blocks
    global angel_x, angel_y, devil_x, devil_y
    global blue_diamonds_req, red_diamonds_req
    global angel_door, devil_door
    # reset players at the level spawning point
    angel.rect.x = angel_x
    angel.rect.y = angel_y
    devil.rect.x = devil_x
    devil.rect.y = devil_y
    # reset player speed
    angel.dx = 0
    devil.dx = 0
    # reset the amount of diamonds require (and re-count - see below)
    blue_diamonds_req = 0
    red_diamonds_req = 0
    # append all tiles that had been deleted (doors and diamonds)
    for a in deleted_blocks:
        map.level_map.append(a)
    deleted_blocks.clear() # clear the list so that only the delete tiles for the next time the user plays are appended not ones from previous attempts
    # variables for door resetting
    i = 0
    door1 = 0 # angel door
    door2 = 0 # devil door
    for final_block in map.level_map:
        i += 1
        # store the index of each open door (to properly delete them later)
        if final_block[2] == 25:
            door1 = map.level_map.index(final_block)
        if final_block[2] == -25:
            door2 = map.level_map.index(final_block)
        # re-count the amount of diamonds needed to be collected
        if final_block[2] == 10:
            blue_diamonds_req += 1
        if final_block[2] == -10:
            red_diamonds_req += 1
        # remove all "open" doors from the screen
        if i >= len(map.level_map):
            # remove both "open" doors
            if door1 != 0 and door2 != 0:
                if door1 < door2:
                    map.level_map.pop(door1)
                    map.level_map.pop(door2 - 1)
                else:
                    map.level_map.pop(door2)
                    map.level_map.pop(door1 - 1)
            # remove "open" angel door
            elif door1 != 0 and door2 == 0:
                map.level_map.pop(door1)
            # remove "open" devil door
            elif door2 != 0 and door1 == 0:
                map.level_map.pop(door2)
        final_block[1].x = final_block[3] # set all game tile x coordinates back to their original x coordinates
   # reset the number of collected diamonds back to 0
    collected_blue = 0
    collected_red = 0
    # reset door collision to false
    angel_door = False
    devil_door = False
    lives = 3 # reset lives to full

def black_transition():
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 300): # sets background to be less transparent (black becomes stronger)
        fade.set_alpha(alpha)
        map.draw()
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(1)

def white_transition():
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.fill((255, 255, 255))
    for alpha in range(0, 300): # same but for white background
        fade.set_alpha(alpha)
        map.draw()
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(2)

class Button():
    def __init__(self, x, y, w, h, image, imageHover, open=None, page=None, level_num=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = image
        self.imageHover = imageHover
        self.open = open
        self.page = page
        self.level_num = level_num
        self.clicked = False

    def check_collide(self): # checks mouse collisions for buttons
        global on_button, current_level_map, game, level_selection, map, start, objective, gameover
        global current_level, red_diamonds_req, blue_diamonds_req, music, levels_unlocked
        mouse_pos = pygame.mouse.get_pos()

        on_button = self.rect.collidepoint(pygame.mouse.get_pos()) # get position of mouse

        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]: # left click
                self.clicked = True
        if self.clicked == True:
            # 'PLAY' button
            if self.page == 'start':
                # when pressed the user is redirected to the level selection screen
                start = False
                level_selection = True

            # 'RULES' button
            elif self.page == 'rules':
                # when pressed the user is redirected to the objective screen
                start = False
                objective = True

            # 'LEVEL 1-15' buttons
            elif self.page == 'level':
                # when pressed the user is redirected to the appropriate level (based on the number of
                # the button they pressed)
                current_level = self.level_num - 1 # current level is set to the button's level num minus one (to be able
                # to properly index through the map current_level_map list)
                map = Map(current_level_map[current_level]) # map is set to the level the user pressed
                game = True
                level_selection = False

            # level selection button (right side panel controls)
            elif self.page == 'level_selection':
                # when pressed the user is redirected to the level selection screen
                # required amount of diamonds is reset
                red_diamonds_req = 0
                blue_diamonds_req = 0
                game = False
                level_selection = True

            # start screen button (right side panel controls)
            elif self.page == 'start_screen':
                # when pressed the user is redirected to the start screen
                # required amount of diamonds is reset
                red_diamonds_req = 0
                blue_diamonds_req = 0
                game = False
                start = True

            elif self.page == 'reset':
                # when pressed the user is redirection to the start screen and all their progress is reset
                current_level = 1
                levels_unlocked = 1
                gameover = False
                start = True

            elif self.page == 'quit':
                # when pressed the game is quit
                pygame.quit()

            # volume buttom (right side panel controls)
            elif self.page == 'volume':
                # turn volume off
                if self.clicked == True and music == True:
                    music = False

                # turn volume on
                elif self.clicked == True and music == False:
                    music = True
            self.clicked = False
        else:
            # if the user hasn't click or isn't hovering over any button, then the unhighlighted image (darker image) is displayed
            screen.blit(self.image, self.image.get_rect(center=self.rect.center))

    def draw(self, surf):
        global image, current_level, levels_unlocked
        # unlock level button (when level is passed or currently being played)
        if self.page == 'level':
            if self.level_num <= levels_unlocked:
                self.open = "unlocked"

        # draw locked buttons
        if self.open == "locked":
            self.image = pygame.image.load('LEVELS BUTTONS/LEVEL_LOCKED.png')
            surf.blit(self.image, self.image.get_rect(center=self.rect.center))
        else:
            # draw unlocked level buttons
            if self.page == 'level':
                self.image = pygame.image.load('LEVELS BUTTONS/LEVEL_' + str(self.level_num) + '.png')

            # draw volume button
            elif self.page == 'volume':
                # volume on button
                if music == True:
                    self.image = pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/VOLUME_ON.png'), (32, 30))
                    self.imageHover = pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/VOLUME_ON_HOVER.png'), (32, 30))
                # volume off button
                else:
                    self.image = pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/VOLUME_OFF.png'), (32, 30))
                    self.imageHover = pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/VOLUME_OFF_HOVER.png'), (32, 30))

            self.check_collide() # check button collision
            if on_button:
                surf.blit(self.imageHover, self.imageHover.get_rect(center=self.rect.center)) # change image to its hovering image (lighter colour)

class Sprite():
    def __init__(self, x, y, NAME):
        self.NAME = NAME
        self.images_right = [] # list of all right facing character images
        self.images_left = [] # list of all left facing character images
        self.index = 0 # required for animation
        self.counter = 0 # required for animation cooldown
        for n in range(0, 3): # 3 images in each character's animation
            img_right = pygame.image.load('SPRITES/' + self.NAME + '_' + str(n) + '.png')
            if NAME == 'DEVIL': # flip all devil images upside-down
                img_right = pygame.transform.flip(img_right, False, True)
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index] # current character image
        self.rect = self.image.get_rect() # character rectangle (for collision)
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = None
        self.dx = 0 # speed
        self.collision = False

    def update(self):
        global collected_blue, collected_red, lives, deleted_blocks
        global current_level_map, game, level_selection, blue_diamonds_req, red_diamonds_req
        global level_scroll_num, doublejump, jump1time, jump2time
        global angel_door, devil_door, dy

        # constantly resetting these variables
        self.dx = 0
        dy = 0
        cooldown = 5
        angel_door = False
        devil_door = False
        level_scroll_num = 0

        # key presses
        key = pygame.key.get_pressed()

        # jumping
        if key[pygame.K_SPACE]:
            self.jumped = True
        elif key[pygame.K_SPACE] == False:
            self.jumped = False
        if self.jumped:
            if doublejump == 0 and angel.vel_y == 0 and devil.vel_y == 0:
                jump1time = pygame.time.get_ticks() / 1000
                angel.vel_y = jump_speed
                devil.vel_y = jump_speed
                doublejump = 1
            elif doublejump == 1:
                jump2time = pygame.time.get_ticks() / 1000
                jumpdiff = jump2time - jump1time
                if jumpdiff >= 0.3:
                    angel.vel_y = jump_speed
                    devil.vel_y = jump_speed
                    doublejump = 2
        if angel.vel_y == 0 and devil.vel_y == 0 and self.jumped == True:
            doublejump = 0

        # left movement
        if key[pygame.K_LEFT]:
            self.counter += 1 # animation counter
            self.direction = 'left' # character direction (left)
            # loops through all game tiles in the current map
            for final_block in map.level_map:
                if final_block[1].colliderect(self.rect.x - 4, self.rect.y, self.width, self.height) == False and self.direction == 'left':
                    self.collision = False # set collision to false if no longer colliding when moving left

                if final_block[2] == 70: # 70 is the invisible block
                    # scrolling stops once the invisible block's x reaches the beginning of the screen
                    if final_block[1].x == 0:
                        self.dx -= 4
                        level_scroll_num = 0
                    else:
                        # scrolling (right)
                        if angel.collision == False and devil.collision == False and min(angel.rect.x, devil.rect.x) < SCREEN_WIDTH // 2: # the leftmost player's x must be less than half the screen
                            self.dx = 0 # player stops moving
                            level_scroll_num = 4 # screen starts scrolling
                        else:
                            # no scrolling
                            self.dx -= 4 # player starts moving
                            level_scroll_num = 0 # screen stops scrolling

        # right movement
        if key[pygame.K_RIGHT]:
            self.counter += 1 # animation counter
            self.direction = 'right' # character direction (right)
            # loops through all game tiles in the current map
            for final_block in map.level_map:
                if final_block[1].colliderect(self.rect.x + 4, self.rect.y, self.width, self.height) == False and self.direction == 'right':
                    self.collision = False # set collision to false if no longer colliding when moving right

                if final_block[2] == 8 or final_block[2] == 25: # 8 is the closed door, 25 is the open door
                    # scrolling stops once the open or closed door's x reaches the end of the screen
                    if final_block[1].x == SCREEN_WIDTH - 48:
                        self.dx += 4
                        level_scroll_num = 0
                    else:
                        # scrolling (left)
                        if angel.collision == False and devil.collision == False and max(angel.rect.x, devil.rect.x) > SCREEN_WIDTH // 2: # the rightmost player's x must be more than half the screen
                            self.dx = 0 # player stops moving
                            level_scroll_num = -4 # screen starts scrolling
                        else:
                            # no scrolling
                            self.dx += 4 # player starts moving
                            level_scroll_num = 0 # screen stops scrolling

        # standing
        if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
            self.counter = 0 # animation counter is reset
            self.index = 0 # standing image is displayed for each character
            if self.direction == 'right':
                self.image = self.images_right[self.index] # right facing standing image
            if self.direction == 'left':
                self.image = self.images_left[self.index] # left facing standing image

        # animation
        if self.counter > cooldown: # if the counter exceeds the cooldown, it is reset
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right) - 1: # if the index of the current image exceeds the list of images, the index is reset
                self.index = 0
            # right movement animation
            if self.direction == 'right':
                # right jumping animation
                if key[pygame.K_SPACE]:
                    self.image = self.images_right[2]
                else:
                    # right walking animation
                    self.image = self.images_right[self.index]
            # left movement animation
            if self.direction == 'left':
                # left jumping animation
                if key[pygame.K_SPACE]:
                    self.image = self.images_left[2]
                else:
                    # left walking animation
                    self.image = self.images_left[self.index]

        # gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # decorations list
        decorations = map.decorations # see map class for more information :)

        # collision
        # loops through all game tiles in the current map
        for final_block in map.level_map:

            # blue diamond collision
            if final_block[2] == 10: # 10 is the blue diamond
                if final_block[1].colliderect(angel.rect.x, angel.rect.y, angel.width, angel.height):
                    # if angel collides with the diamond the counter increases by 1 and the diamond is removed from the screen
                    pygame.mixer.Sound.play(diamond_collected)
                    collected_blue += 1
                    deleted_blocks.append(final_block)
                    map.level_map.remove(final_block)

            # red diamond collision
            if final_block[2] == -10: # -10 is the red diamond
                if final_block[1].colliderect(devil.rect.x, devil.rect.y, devil.width, devil.height):
                    # if devil collides with the diamond the counter increases by 1 and the diamond is removed from the screen
                    pygame.mixer.Sound.play(diamond_collected)
                    collected_red += 1
                    deleted_blocks.append(final_block)
                    map.level_map.remove(final_block)

            # angel spike collision
            if final_block[2] == 23: # 23 is the blue spike
                if final_block[1].colliderect(angel.rect.x, angel.rect.y, angel.width, angel.height):
                    # if the angel collides with the spikes the are pushed back (if they touch it from the side)
                    # or up (if they fall on it) and the user losses a life
                    if final_block[1].y - (angel.rect.height - final_block[1].height) > angel.rect.y:
                        angel.rect.y -= 100
                    elif final_block[1].x >= angel.rect.x:
                        angel.rect.x -= 30
                    elif final_block[1].x <= angel.rect.x:
                        angel.rect.x += 30
                    lives -= 1

            # devil spike collision
            if final_block[2] == -23 or final_block[2] == 26: # -23 is the red spike, 26 is the upside-down blue spike
                if final_block[1].colliderect(devil.rect.x, devil.rect.y, devil.width, devil.height):
                    # if the devil collides with the spikes the are pushed back (if they touch it from the side)
                    # or down (if they fall on it) and the user losses a life
                    if final_block[1].y < devil.rect.y:
                        devil.rect.y += 100
                    elif final_block[1].x >= devil.rect.x:
                        devil.rect.x -= 30
                    elif final_block[1].x <= devil.rect.x:
                        devil.rect.x += 30
                    lives -= 1

            # open angel door
            if final_block[2] == 8 and collected_blue == blue_diamonds_req: # 8 is the blue door
                # if the amount of collected blue diamonds equals to the required amount, then the door is opened
                # the closed door image is replaced with the open door image
                deleted_blocks.append(final_block)
                map.level_map.remove(final_block)
                block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_B25.png'), (48, 48))
                block_rect = final_block[1]
                block_rect.x = final_block[1].x
                block_rect.y = final_block[1].y
                original_x = block_rect.x
                final_block = (block, block_rect, 25, original_x)
                map.level_map.append(final_block)

            # open devil door
            if final_block[2] == -8 and collected_red == red_diamonds_req: # -8 is the red door
                # if the amount of collected red diamonds equals to the required amount, then the door is opened
                # the closed door image is replaced with the open door image
                deleted_blocks.append(final_block)
                map.level_map.remove(final_block)
                block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_R25.png'), (48, 48))
                block_rect = final_block[1]
                block_rect.x = final_block[1].x
                block_rect.y = final_block[1].y
                original_x = block_rect.x
                final_block = (block, block_rect, -25, original_x)
                map.level_map.append(final_block)

            # angel door collision ("walked" through)
            if final_block[2] == 25: # 25 is the open blue door
                if final_block[1].x == angel.rect.x and final_block[1].y == angel.rect.y:
                    #if the angel is on top of the door, the collision equals true
                    angel_door = True

            # devil door collision ("walked" through)
            if final_block[2] == -25: # -25 is the open blue door
                if final_block[1].x == devil.rect.x and final_block[1].y == devil.rect.y:
                    # if the devil is on top of the door, the collision equals true
                    devil_door = True

            # player x collision (for all other tiles that aren't decoration)
            # loops through all game tiles in the current map and that are also not in the decorations list
            if final_block[2] not in decorations:

                # right direction collision
                if final_block[1].colliderect(self.rect.x + 4, self.rect.y, self.width, self.height) and self.direction == 'right':
                    # if the characters is moving right and they collide with a tile, collision equals true
                    self.dx = 0
                    self.collision = True

                # left direction collision
                elif final_block[1].colliderect(self.rect.x - 4, self.rect.y, self.width, self.height) and self.direction == 'left':
                    # if the characters is moving left and they collide with a tile, collision equals true
                    self.dx = 0
                    self.collision = True

                if self.collision == True:
                    # if either character collides with a tile the screen scrolling stops and so does that character's movement
                    self.dx = 0
                    level_scroll_num = 0

                # angel collision
                if self.NAME == 'ANGEL':
                    # angel y collision
                    if final_block[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                        # jumping
                        if self.vel_y < 0:
                            dy = final_block[1].bottom - self.rect.top
                            self.vel_y = 0
                        # falling
                        elif self.vel_y >= 0:
                            dy = final_block[1].top - self.rect.bottom
                            self.vel_y = 0

                # devil collision
                if self.NAME == 'DEVIL':
                    # devil y collision
                    if final_block[1].colliderect(self.rect.x, self.rect.y - dy, self.width, self.height):
                        # jumping
                        if self.vel_y < 0:
                            dy = self.rect.bottom - final_block[1].top
                            self.vel_y = 0
                        # falling
                        elif self.vel_y >= 0:
                            dy = self.rect.top - final_block[1].bottom
                            self.vel_y = 0

        # players fall off map
        if (angel.rect.y > SCREEN_HEIGHT) or (devil.rect.y + devil.rect.height < 0):
            lives = 0

        # when all lives are used up, the level is reset
        if lives <= 0:
            black_transition() # refer to black_transition function
            reset() # refer to reset function

        # boundaries (players cannot leave the screen horizontally)
        if self.rect.x <= 0:
            # if the character reach the end of the left side of the screen, their x is set to 0
            self.rect.x = 0
        elif self.rect.x >= 1248:
            # if the character reach the end of the right side of the screen, their x is set to the screen width minus their width (1248)
            self.rect.x = 1248

        # update player coordinates
        if self.NAME == 'ANGEL':
            self.rect.x += self.dx
            self.rect.y += dy
        elif self.NAME == 'DEVIL':
            self.rect.x += self.dx
            self.rect.y -= dy

        # draw players
        screen.blit(self.image, self.rect)

class Map():
    def __init__(self, level):
        self.level_map = []
        self.decorations = []

        global blue_diamonds_req, red_diamonds_req, angel_x, angel_y, devil_x, devil_y

        # add tile function
        def add_block(y_difference):
            block_rect = block.get_rect()
            block_rect.x = tile_x * TILE_SCALE
            block_rect.y = (tile_y * TILE_SCALE) + y_difference
            original_x = block_rect.x # starting x position is stored for level resetting
            final_block = (block, block_rect, tile, original_x) # each tile has 4 values (the image, rectangle, tile number, its starting x position)
            self.level_map.append(final_block) # tile is appended to the map list

        tile_y = 0
        # puts together tiles into a full map, using the level layout
        for layer in level:
            tile_x = 0
            for tile in layer:
                # blue tiles
                if tile > 0 and tile <= 49:
                    # blue spikes
                    if tile == 23:
                        block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_B' + str(tile) + '.png'), (48, 24))
                        add_block(24)
                    elif tile == 26:
                        block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_B' + str(tile) + '.png'), (48, 24))
                        add_block(0)
                    # all other blue tiles
                    else:
                        block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_B' + str(tile) + '.png'), (48, 48))
                        add_block(0)
                    # blue arrow
                    if tile == 9:
                        # player spawns behind the arrow
                        angel_x = (tile_x * TILE_SCALE) - 48
                        angel_y = tile_y * TILE_SCALE
                    # blue diamonds counter
                    if tile == 10:
                        blue_diamonds_req += 1

                # red tiles
                if tile < 0 and tile >= -49:
                    # red spikes
                    if tile == -23:
                        block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_R23.png'), (48, 24))
                        add_block(0)
                    # all other red tiles
                    else:
                        block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_R' + str(abs(tile)) + '.png'), (48, 48))
                        add_block(0)
                    # red arrow
                    if tile == -9:
                        # player spawns behind the arrow
                        devil_x = (tile_x * TILE_SCALE) - 48
                        devil_y = tile_y * TILE_SCALE
                    # red diamonds counter
                    if tile == -10:
                        red_diamonds_req += 1

                # chains
                if tile >= 50 and tile <= 53:
                    block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_' + str(tile) + '.png'), (48, 48))
                    add_block(0)
                if tile <= -50 and tile >= -53:
                    block = pygame.transform.scale(pygame.image.load('GAME TILES/TILE_' + str(tile) + '.png'), (48, 48))
                    add_block(0)

                # invisible block (for screen scrolling)
                if tile == 70:
                    block = pygame.transform.scale(pygame.image.load('GAME TILES/TRANSPARENT.png'), (48, 48))
                    add_block(0)

                tile_x += 1
            tile_y += 1

        self.decorations = [9, -9, 51, -51, 52, -52, 53, -53, 10, -10, 23, -23, 25, -25, 70, -71] # items that shouldn't be collided with, or have a special collision

    def draw(self):
        global level_scroll_num
        for final_block in self.level_map:

            # level scrolling
            final_block[1].x += level_scroll_num

            # level draw
            screen.blit(final_block[0], final_block[1])

# buttons
START_BUTTONS = [Button(875, 225, 272, 120, pygame.image.load('START BUTTONS/PLAY.png'), pygame.image.load('START BUTTONS/PLAY_HOVER.png'), None, "start", None),
                 Button(875, 400, 272, 120, pygame.image.load('START BUTTONS/RULES.png'), pygame.image.load('START BUTTONS/RULES_HOVER.png'), None, "rules", None)]

LEVEL_BUTTONS = [Button(268, 250, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_1.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_1_HOVER.png'), "locked", "level", 1),
                 Button(434, 250, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_2.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_2_HOVER.png'), "locked", "level", 2),
                 Button(600, 250, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_3.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_3_HOVER.png'), "locked", "level", 3),
                 Button(766, 250, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_4.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_4_HOVER.png'), "locked", "level", 4),
                 Button(932, 250, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_5.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_5_HOVER.png'), "locked", "level", 5),
                 Button(268, 390, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_6.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_6_HOVER.png'), "locked", "level", 6),
                 Button(434, 390, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_7.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_7_HOVER.png'), "locked", "level", 7),
                 Button(600, 390, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_8.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_8_HOVER.png'), "locked", "level", 8),
                 Button(766, 390, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_9.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_9_HOVER.png'), "locked", "level", 9),
                 Button(932, 390, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_10.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_10_HOVER.png'), "locked", "level", 10),
                 Button(268, 530, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_11.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_11_HOVER.png'), "locked", "level", 11),
                 Button(434, 530, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_12.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_12_HOVER.png'), "locked", "level", 12),
                 Button(600, 530, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_13.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_13_HOVER.png'), "locked", "level", 13),
                 Button(766, 530, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_14.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_14_HOVER.png'), "locked", "level", 14),
                 Button(932, 530, 96, 90, pygame.image.load('LEVELS BUTTONS/LEVEL_15.png'), pygame.image.load('LEVELS BUTTONS/LEVEL_15_HOVER.png'), "locked", "level", 15)]

CONTROL_BUTTONS = [Button(1242, 30, 32, 30, pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/VOLUME_ON.png'), (32, 30)), pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/VOLUME_ON_HOVER.png'), (32, 30)), None, "volume", None),
                   Button(1242, 70, 32, 30, pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/LEVEL_SELECTION.png'), (32, 30)), pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/LEVEL_SELECTION_HOVER.png'), (32, 30)), None, "level_selection", None),
                   Button(1242, 110, 32, 30, pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/START_SCREEN.png'), (32, 30)), pygame.transform.scale(pygame.image.load('CONTROL BUTTONS/START_SCREEN_HOVER.png'), (32, 30)), None, "start_screen", None)]

GAMEOVER_BUTTONS = [Button(512, 290, 272, 120, pygame.image.load('GAMEOVER BUTTONS/RESET.png'), pygame.image.load('GAMEOVER BUTTONS/RESET_HOVER.png'), None, "reset", None),
                    Button(512, 450, 272, 120, pygame.image.load('GAMEOVER BUTTONS/QUIT.png'), pygame.image.load('GAMEOVER BUTTONS/QUIT_HOVER.png'), None, "quit", None)]

# main game loop
while True:
    clock.tick(FPS)
    # volume on
    if music == True:
        pygame.mixer.music.unpause()
        diamond_collected.set_volume(0.1)
    # volume off
    else:
        pygame.mixer.music.pause()
        diamond_collected.set_volume(0)

    key = pygame.key.get_pressed()

    enter_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            enter_pressed = True
        if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            enter_pressed = False

    # ways to quit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    if key[pygame.K_ESCAPE]:
        pygame.quit()

    # start screen
    if start == True:
        background_scroll(pygame.image.load('CLOUD_BG.png'), 2) # refer to background_scroll function

        screen.blit(pygame.transform.scale(pygame.image.load('LOGO.png'), (750, 450)), (50, 150))

        # draw start screen buttons
        for s in START_BUTTONS:
            s.draw(screen)

    # objective of the game screen
    elif objective == True:
        background_scroll(pygame.image.load('CLOUD_BG.png'), 2) # refer to background_scroll function

        screen.blit(pygame.image.load('TEXT/OBJECTIVE_TEXT.png'), (468, 170))
        screen.blit(pygame.transform.scale(pygame.image.load('TEXT/OBJECTIVE_TEXT2.png'), (1000, 700)), (148, 20))

        if enter_pressed == True:
            # when pressed the user is redirected to the controls screen
            objective = False
            controls = True

    # explanation of controls screen
    elif controls == True:
        background_scroll(pygame.image.load('CLOUD_BG.png'), 2) # refer to background_scroll function

        screen.blit(pygame.image.load('TEXT/CONTROLS_TEXT.png'), (488, 170))
        screen.blit(pygame.transform.scale(pygame.image.load('TEXT/CONTROLS_TEXT2.png'), (1200, 672)), (48, 48))
        screen.blit(pygame.transform.scale(pygame.image.load('TEXT/CONTROLS_TEXT3.png'), (1000, 700)), (148, 20))

        if enter_pressed == True:
            # when pressed the user is redirected to the level selection screen
            controls = False
            level_selection = True

    # level selection screen
    elif level_selection == True:
        background_scroll(pygame.image.load('CLOUD_BG.png'), 2) # refer to background_scroll function

        screen.blit(pygame.image.load('TEXT/SELECT_A_LEVEL_TEXT.png'), (372, 140))

        # draw level selection buttons
        for b in LEVEL_BUTTONS:
            b.draw(screen)

        # draw control buttons
        for c in CONTROL_BUTTONS:
            c.draw(screen)

        angel = Sprite(angel_x, angel_y, 'ANGEL')
        devil = Sprite(devil_x, devil_y, 'DEVIL')

    # game screen
    elif game == True:
        global angel_door, devil_door, dy
        background_scroll(pygame.image.load('GAME_BG.png'), 3) # refer to background_scroll function

        # draw map
        map.draw()

        # updated characters
        angel.update()
        devil.update()


        # reset level
        if key[pygame.K_r]:
            reset() # refer to reset function

        # pass onto the next level
        if angel_door == True and devil_door == True:
            white_transition() # refer to white_transition function
            reset() # refer to reset function
            current_level += 1 # current level increases by 1
            if levels_unlocked == 15:
                # if all 15 levels have been completed, the user is redirected to the gameover screen
                game = False
                gameover = True
            elif not levels_unlocked > current_level:
                levels_unlocked += 1 # if the level has not already been unlocked, then the number of unlocked levels increaes by 1
                map = Map(current_level_map[current_level]) # next level's map is set
                # required amount of diamonds is reset and re-counted
                blue_diamonds_req = 0
                red_diamonds_req = 0
                for final_block in map.level_map:
                    if final_block[2] == 10:
                        blue_diamonds_req += 1
                    if final_block[2] == -10:
                        red_diamonds_req += 1

        side_panel() # refer to side_panel function

        # draw control buttons
        for c in CONTROL_BUTTONS:
            c.draw(screen)

    # gameover screen
    elif gameover == True:
        background_scroll(pygame.image.load('CLOUD_BG.png'), 2) # refer to background_scroll function

        screen.blit(pygame.image.load('CONGRATULATIONS_BG.png'), (0, 0))

        # draw gameover buttons
        for g in GAMEOVER_BUTTONS:
            g.draw(screen)

    pygame.display.update()

pygame.quit()