# Test update
import pgzrun
from random import random
import time

# ---GLOBAL GAME VARIABLES--- #
WIDTH = 800 # Sets the game window size in Pygame Zero
HEIGHT = 450
TILESIZE = images.dirt.get_height()

# Optimises image drawing
def remove_alpha(image): # allows for more efficient image drawing
    return image.convert_alpha()

# ----------CLASSES---------- #
class Background(object):
    images = {"background": images.background,
              "dirt" : images.dirt,
              "life": images.life_icon}

    def __init__(self, speed = 7):
        self.dirt_height = self.dirt_width = self.grass_height = TILESIZE
        self.backgroundimage = remove_alpha(self.images["background"])
        self.background_x = 0
        self.background2_x = self.backgroundimage.get_width()
        self.speed = speed
        self.life_x = 0
        self.life_icon = remove_alpha(self.images["life"])

    def draw(self, lives): # draws side scrolling background and no. of lives
        screen.blit(self.backgroundimage, (self.background_x, 0)) # 2 moving background images are required to create side scrolling background animation
        screen.blit(self.backgroundimage, (self.background2_x, 0))
        life_x, life_y = 750, 20

        for life in range(lives):
            screen.blit(self.life_icon, (life_x - life * 35, life_y)) # Draws number of lives left on screen

        self.background_x -= self.speed
        self.background2_x -= self.speed

        if self.background_x < self.images["background"].get_width() * -1:
            self.background_x = self.images["background"].get_width()

        if self.background2_x < self.images["background"].get_width() * -1:
            self.background2_x = self.images["background"].get_width()

class GameState(object):
    def __init__(self, speed = 7):
        self.game_over = False
        self.score = 0
        self.player_hit = False
        self.speed = speed
        self.lives = 10
        self.obstacle_probability = 0.005

    def make_invulnerable(self):
        self.player_hit = False

    def make_vulnerable(self): # When player is hit and loses a life, they are invulnerable for 1 second before they can be hit again and lose another life
        self.player_hit = True
        self.lives -= 1
        sounds.eep.play()
        if self.lives < 1:
            self.game_over = True
        clock.schedule_unique(self.make_invulnerable,1.0)

    def game_over_screen(self):
        time.sleep(0.03)
        screen.draw.text("GAME OVER", midtop=(400,100), color = "white",
                      fontsize=128, shadow = (1,1), scolor="black")
        screen.draw.text("PRESS SPACEBAR TO PLAY AGAIN", midtop= (400,200), color = "black",
                         fontsize = 35)
        # TODO: Restart game - at present the gameplay & lives can restart, but the map does not restart
        if keyboard.space:
            self.game_over = False
            self.score = 0
            self.player_hit = False
            self.speed = game.speed
            self.lives = 5

class Character(object):
    player_images_with_alpha = {"RUN": [images.player0, images.player1, images.player2, images.player3, images.player4,
                                        images.player5, images.player6, images.player7, images.player8, images.player9,
                                        images.player10, images.player11, images.player12, images.player13, images.player14,
                                        images.player15, images.player16, images.player17],
                                "JUMP": [images.jump0, images.jump1]} # Image frames to animate character running

    player_images = {"RUN": [remove_alpha(image) for image in player_images_with_alpha["RUN"]],
                     "JUMP": [remove_alpha(image) for image in player_images_with_alpha["JUMP"]]} # Optimising image drawing

    def __init__(self):
        self.player_x = TILESIZE * 2
        self.player_y = HEIGHT - TILESIZE - self.player_images["RUN"][0].get_height() + 3
        self.player_frame = 0
        self.player_image = self.player_images["RUN"][0]
        self.jump_frame = 0
        self.jump = False
        self.jumpcount = 10
        self.width = self.player_images["RUN"][self.player_frame].get_width()
        self.height = self.player_images["RUN"][self.player_frame].get_height()
        self.hitbox = Rect((self.player_x, self.player_y), (self.player_images["RUN"][0].get_width(), self.player_images["RUN"][0].get_height())) # Used to detect if player hits obstacle and loses a life
        self.got_hit = False

    def draw(self):
        if not self.jump:
            self.player_frame += 1
            image_to_draw = self.player_images["RUN"][self.player_frame]
            screen.blit(image_to_draw, (self.player_x, self.player_y))
            self.hitbox = Rect((self.player_x, self.player_y), (image_to_draw.get_width(), image_to_draw.get_height()))
            if self.player_frame == len(self.player_images["RUN"])-1:
                self.player_frame = 1

        elif self.jump: # Image animations and positions of character when jumping
            image_to_draw = self.player_images["JUMP"][self.jump_frame]
            screen.blit(image_to_draw, (self.player_x, self.player_y))
            self.hitbox = Rect((self.player_x, self.player_y), (image_to_draw.get_width(), image_to_draw.get_height()))
            if self.jumpcount >= -10:
                self.jump_frame = 0
                neg = 1
                if self.jumpcount < 0:
                    neg = -1
                self.player_y -= (self.jumpcount ** 2) * 0.5 * neg
                self.jumpcount -= 1
                self.jump_frame = 1
            else:
                self.jump = False
                self.jumpcount = 10
        # TODO: Hit box - delete before production
        screen.draw.rect(self.hitbox, color="RED")

# class ObstacleGeneration(object):
#     def __init__(self, speed = 7):
#         self.level = 1
#         self.object_id = {1: 'spike', 2:'shrub'}
#         self.speed = speed
#     def map_generator(self, obstacle_probability = 0.005, frames = 25):
#         self.buffer_multiplier = 0.75 # Controls space between objects on map
#         self.obstacle_x_buffer = int(player.width * self.buffer_multiplier * 2) # minimum space between obstacles to allow for player have a chance to jump and land to avoid obstacles
#         self.shrub_buffer = int(Shrub.image.get_width() * self.buffer_multiplier)
#         self.rock_buffer = int(Rock.image.get_width() * self.buffer_multiplier)
#         self.door_buffer = int(Door.image.get_width() * self.buffer_multiplier)
#         game_map = [0] * int(WIDTH * 0.5) # First 2 frames of all games will have no objects generated
#         for frame in range(1, frames + 1):
#             for _ in range(self.obstacle_x_buffer): # Ensure that the starts and ends of object frames do not have objects generating too close to each other
#                 game_map.append(0)
#             while len(game_map) < WIDTH * frame:
#                 rand = random()
#                 if rand < obstacle_probability:
#                     game_map.append(1)
#                     for _ in range(self.obstacle_x_buffer):
#                         if len(game_map) < WIDTH * frame:
#                             game_map.append(0)
#                 if rand > obstacle_probability and rand < (obstacle_probability+0.001):
#                     game_map.append(2)
#                     for _ in range(self.shrub_buffer):
#                         if len(game_map) < WIDTH * frame:
#                             game_map.append(0)
#                 if rand > (obstacle_probability+0.001) and rand < (obstacle_probability+0.002):
#                     game_map.append(3)
#                     for _ in range(self.rock_buffer):
#                         if len(game_map) < WIDTH * frame:
#                             game_map.append(0)
#                 if rand > (obstacle_probability + 0.002) and rand < (obstacle_probability + 0.003):
#                     game_map.append(4)
#                     for _ in range(self.door_buffer):
#                         if len(game_map) < WIDTH * frame:
#                             game_map.append(0)
#                 else:
#                     game_map.append(0)
#
#         print(game_map)
#
#         self.obj_list = []
#         for pixel in enumerate(game_map): #TODO: Only store subset of objects in obj_list
#             if pixel[1] == 1:
#                 self.obj_list.append(Spike(speed=self.speed, x=pixel[0]*4))
#             if pixel[1] == 2:
#                 self.obj_list.append(Shrub(speed = self.speed, x = pixel[0]*4))
#             if pixel[1] == 3:
#                 self.obj_list.append(Rock(speed = self.speed, x = pixel[0]*4))
#             if pixel[1] == 4:
#                 self.obj_list.append(Door(speed=self.speed, x=pixel[0]*4))
#         return self.obj_list

class ObstacleGeneration(object):
    def __init__(self, speed=7):
        self.level = 1
        self.speed = speed

    def map_generator(self, obstacle_probability=0.005, frames=50):
        self.buffer_multiplier = 0.75  # Controls space between objects on map
        self.obstacle_x_buffer = int(player.width * self.buffer_multiplier * 2)  # minimum space between obstacles to allow for player have a chance to jump and land to avoid obstacles
        self.shrub_buffer = int(Shrub.image.get_width() * self.buffer_multiplier)
        self.rock_buffer = int(Rock.image.get_width() * self.buffer_multiplier)
        self.door_buffer = int(Door.image.get_width() * self.buffer_multiplier)
        game_map = [[0] * WIDTH, [0] * WIDTH]  # First 2 frames of all games will have no objects generated
        for _ in range(frames):
            frame = [0] * self.obstacle_x_buffer # Create buffer at start of frame to ensure that objects are not drawn too closely to each other at the start & end edges of frames
            while len(frame) < WIDTH:
                rand = random()
                if rand < obstacle_probability:
                    frame.append(1)
                    for _ in range(self.obstacle_x_buffer):
                        if len(frame) < WIDTH:
                            frame.append(0)
                if rand > obstacle_probability and rand < (obstacle_probability + 0.001):
                    frame.append(2)
                    for _ in range(self.shrub_buffer):
                        if len(frame) < WIDTH:
                            frame.append(0)
                if rand > (obstacle_probability + 0.001) and rand < (obstacle_probability + 0.002):
                    frame.append(3)
                    for _ in range(self.rock_buffer):
                        if len(frame) < WIDTH:
                            frame.append(0)
                if rand > (obstacle_probability + 0.002) and rand < (obstacle_probability + 0.003):
                    frame.append(4)
                    for _ in range(self.door_buffer):
                        if len(frame) < WIDTH:
                            frame.append(0)
                else:
                    frame.append(0)

            game_map.append(frame)

        print(game_map)
        return game_map

    def obj_generator(self, map_frame):
        obj_list = []
        for pixel in enumerate(map_frame):  # TODO: Only store subset of objects in obj_list
            if pixel[1] == 1:
                obj_list.append(Spike(speed=self.speed, x=pixel[0] * 4))
            if pixel[1] == 2:
                obj_list.append(Shrub(speed=self.speed, x=pixel[0] * 4))
            if pixel[1] == 3:
                obj_list.append(Rock(speed=self.speed, x=pixel[0] * 4))
            if pixel[1] == 4:
                obj_list.append(Door(speed=self.speed, x=pixel[0] * 4))
        return obj_list


class GameObject(object): # Class for obstacles & scenery objects
    image = images.shrub
    def __init__(self, speed, x=WIDTH):
        self.x = x
        self.speed = speed
        self.width = self.image.get_width()
        self.height = self.image.get_height()

class Spike(GameObject):
    image = remove_alpha(images.spike1)
    def __init__(self, speed, x, hitbox = Rect(0,0,0,0)):
        super().__init__(speed,x)
        self.hitbox = hitbox
        self.y = HEIGHT - TILESIZE - 15
        self.hit_once = False

    def draw(self):
        screen.blit(self.image,(self.x,self.y))
        self.hitbox = Rect((self.x, self.y), (self.width, self.height))
        screen.draw.rect(self.hitbox, color="RED")
        self.x -= self.speed
        return self.hitbox

    def collide(self,rect): # If the player hits a spike a life is lost
        if self.hitbox.colliderect(rect):
            return True
        return False

class Door(GameObject):
    image = remove_alpha(images.door)
    def __init__(self, speed, x, hitbox = Rect(0,0,0,0)):
        super().__init__(speed,x)
        self.hitbox = hitbox
        self.y = HEIGHT - self.image.get_height() - TILESIZE + 14
        self.hit_once = False

    def draw(self):
        screen.blit(self.image,(self.x,self.y))
        self.hitbox = Rect((self.x, self.y), (self.width, self.height))
        screen.draw.rect(self.hitbox, color="RED")
        self.x -= self.speed
        return self.hitbox

    def enter_door(self,rect): # If the player fully intersects a door, the player will teleport
        if self.hitbox.contains(rect):
            rand = random()
            if rand < 0.7:
                travel = rand
            else:
                travel = -(1 - rand)
            print(travel)
            return travel
        else:
            return False

class Shrub(GameObject):
    image = remove_alpha(images.shrub)

    def __init__(self, speed, x = WIDTH):
        super().__init__(speed, x)
        self.y = HEIGHT - TILESIZE - self.image.get_height() + 8

    def draw(self):
        screen.blit(self.image,(self.x,self.y))
        self.x -= self.speed

class Rock(Shrub):
    image = remove_alpha(images.rock)

    def __init__(self, speed, x = WIDTH,):
        super().__init__(speed, x)
# ------GAME INITIATION------ #
game = GameState()
player = Character()
background = Background()
obstaclegeneration = ObstacleGeneration()
game_map = obstaclegeneration.map_generator(obstacle_probability = game.obstacle_probability, frames = 50)


def draw():
    if not game.game_over:
        background.draw(lives = game.lives)
        for frame in game_map:
            print('frame', frame)
            obj_list = obstaclegeneration.obj_generator(frame)
            for obj in obj_list:
                obj.draw()
        player.draw()
    if game.game_over:
        return

def levelup(level = 1):
    levelspeed = {1:7, 2:11, 3:13, 4:15}
    game.speed = background.speed = levelspeed[level]
    for obj in obj_list:
        obj.speed = levelspeed[level]

def game_loop():
    elapsed_time = time.perf_counter() # Tracks time (in seconds) so that the game speeds up as time progresses
    if keyboard.up:
        player.jump = True
    if game.player_hit == False:
        for obj in obj_list:
            if hasattr(obj,'collide'):
                if obj.collide(player.hitbox):
                    game.make_vulnerable()
            elif hasattr(obj,'enter_door'):
                if obj.enter_door(player.hitbox):
                    game.travel()
    if elapsed_time < 60:
        levelup(level=1)
    elif elapsed_time < 60 * 2:
        levelup(level=2)
    elif elapsed_time < 60 * 3:
        levelup(level=3)
    elif elapsed_time < 60 * 4:
        levelup(level=4)

def update():
    if not game.game_over:
        clock.schedule_interval(game_loop, 0.5)
    if game.game_over:
        game.game_over_screen()
        clock.unschedule(game_loop)
        clock.unschedule(draw)
        if keyboard.space:
            game.game_over = False
            start_game()
            clock.schedule_interval(game_loop,0.5)
            clock.schedule_interval(draw,0.5)

pgzrun.go()