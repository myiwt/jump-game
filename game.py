# To run this game, open a command prompt terminal, type in: cd <the folder path this script is in>. Then type in the command: pgzrun game.py
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

class Background(object):
    images = {"background": images.background,
              "dirt" : images.dirt,
              "life": images.life_icon}

    def __init__(self, speed):
        self.dirt_height = self.dirt_width = self.grass_height = TILESIZE
        self.backgroundimage = remove_alpha(self.images["background"])
        self.background_x = 0
        self.background2_x = self.backgroundimage.get_width()
        self.speed = speed
        self.life_x = 0
        self.life_icon = remove_alpha(self.images["life"])

    def draw(self, lives): # draws side scrolling background and no. of lives
        screen.blit(self.backgroundimage, (self.background_x, 0))
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
    def __init__(self, speed = 10):
        self.game_over = False
        self.score = 0
        self.player_hit = False
        self.speed = speed
        self.lives = 5
        self.probability = 0.005
        #TODO: Define levels and probability levels & speed levels
        level_info = {1: {"probability": 0.001,"speed": 10},
                      2: {"probability": 0.05 , "speed": 5},
                      3: {"probability": 0.05, "speed": 5},
                      4: {"probability": 0.05, "speed": 5}}

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
            self.speed = 20
            self.lives = 5

class Character(object):
    player_images_with_alpha = {"RUN": [images.player0, images.player1, images.player2, images.player3, images.player4,
                                        images.player5, images.player6, images.player7, images.player8],
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

class ObstacleGeneration(object):
    def __init__(self):
        self.level = 1
        self.object_id = {1: 'spike', 2:'shrub'}

    def map_generator(self, probability = 0.005, frames = 5):
        self.obstacle_x_buffer = player.width * 6 # minimum space between obstacles to allow for player have a chance to land and jump to avoid obstacles
        self.shrub_buffer = images.shrub.get_width() * 3
        self.rock_buffer = images.rock.get_width()* 3
        game_map = [0] * WIDTH * 2 # First 2 frames of all games will have no objects generated
        for frame in range(1, frames+ 1):
            while len(game_map) < WIDTH * frame:
                rand = random()
                if rand < probability:
                    game_map.append(1)
                    for _ in range(self.obstacle_x_buffer):
                        if len(game_map) < WIDTH * frame:
                            game_map.append(0)
                if rand > probability and rand < 0.006:
                    game_map.append(2)
                    for _ in range(self.shrub_buffer):
                        if len(game_map) < WIDTH * frame:
                            game_map.append(0)
                if rand > 0.006 and rand < 0.007:
                    game_map.append(3)
                    for _ in range(self.rock_buffer):
                        if len(game_map) < WIDTH * frame:
                            game_map.append(0)
                else:
                    game_map.append(0)

        print(game_map)
        self.obj_list = []
        for pixel in enumerate(game_map):
            if pixel[1] == 1:
                self.obj_list.append(Spike(speed=game.speed, x=pixel[0]))
            if pixel[1] == 2:
                self.obj_list.append(Scenery(speed = game.speed, x = pixel[0], image = 'shrub'))
            if pixel[1] == 3:
                self.obj_list.append(Scenery(speed = game.speed, x = pixel[0], image = 'rock'))
        return self.obj_list

#    def draw(self, obj_list):
#        obj_list = self.obj_list
#        for obj in obj_list:
#            screen.blit(obj.image, (obj.x, obj.y))
class GameObject(object): # Parent / super class for obstacles & scenery objects in game
    image = images.shrub
    def __init__(self, speed, x=WIDTH):
        self.x = x
        self.speed = speed
        self.width = self.image.get_width()
        self.height = self.image.get_height()

class Spike(GameObject):
    image = remove_alpha(images.spike)
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

class Scenery(GameObject):
    images = {'shrub': remove_alpha(images.shrub),
              'rock': remove_alpha(images.rock)}

    def __init__(self, speed, x = WIDTH, image = 'rock'):
        super().__init__(speed, x)
        self.image = self.images[image]
        self.y = HEIGHT - TILESIZE - self.image.get_height() + 8
        #self.width = self.image.get_width()
        #self.height = self.image.get_height()

    def draw(self):
        screen.blit(self.image,(self.x,self.y))
        self.x -= self.speed

game = GameState(speed = 10)
player = Character()
background = Background(speed=game.speed)
obstaclegeneration = ObstacleGeneration()
obj_list = obstaclegeneration.map_generator(probability = game.probability, frames = 20)


def draw():
    if not game.game_over:
        background.draw(lives = game.lives)
        player.draw()
        for obj in obj_list:
            obj.draw()
    if game.game_over:
        return
#def obstacle_draw():
#    obstaclegeneration.draw(obj_list = obj_list)


def start_game():
    game = GameState()
    player = Character()
    background = Background(speed=game.speed)
    obj_list = obstaclegeneration.map_generator(probability=game.probability, frames=20)
    draw()
    return obj_list


def game_loop():
    if keyboard.up:
        player.jump = True
    if game.player_hit == False:
        for obj in obj_list:
            if hasattr(obj,'collide'):
                if obj.collide(player.hitbox):
                    game.make_vulnerable()

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