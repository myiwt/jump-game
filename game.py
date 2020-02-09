# To run this game, open a command prompt terminal, type in: cd <the folder path this script is in>. Then type in the command :pgzrun game.py
import pgzrun
from random import random

# ---GLOBAL GAME VARIABLES--- #
WIDTH = 800 # Game window size
HEIGHT = 450
TILESIZE = images.dirt.get_height()

def remove_alpha(image): # allows for more efficient image drawing
    return image.convert_alpha()

class Background():
    images = {"background": images.background,
              "dirt" : images.dirt}

    def __init__(self, speed):
        self.dirt_height = self.dirt_width = self.grass_height = TILESIZE
        self.backgroundimage = remove_alpha(self.images["background"])
        self.background_x = 0
        self.background2_x = self.backgroundimage.get_width()
        self.speed = speed

    def draw(self): # draws moving side scrolling background
        screen.blit(self.backgroundimage, (self.background_x, 0))
        screen.blit(self.backgroundimage, (self.background2_x, 0))

        self.background_x -= self.speed
        self.background2_x -= self.speed

        if self.background_x < self.images["background"].get_width() * -1:
            self.background_x = self.images["background"].get_width()

        if self.background2_x < self.images["background"].get_width() * -1:
            self.background2_x = self.images["background"].get_width()

class GameState():
    def __init__(self, speed = 7):
        self.game_over = False
        self.score = 0
        self.player_hit = False
        self.speed = speed
        #TODO: Define levels and probability levels & speed levels

    def make_invulnerable(self):
        self.player_hit = False

    def make_vulnerable(self): # When player is hit, they are invulnerable for 1 second before they can be hit again
        self.player_hit = True
        sounds.eep.play()
        print('hit')
        clock.schedule_unique(self.make_invulnerable,1.0)

class Character():
    player_images_with_alpha = {"RUN": [images.player0, images.player1, images.player2, images.player3, images.player4,
                                        images.player5, images.player6, images.player7, images.player8],
                                "JUMP": [images.jump0, images.jump1]}

    player_images = {"RUN": [remove_alpha(image) for image in player_images_with_alpha["RUN"]],
                     "JUMP": [remove_alpha(image) for image in player_images_with_alpha["JUMP"]]}

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
        self.hitbox = Rect((self.player_x, self.player_y), (self.player_images["RUN"][0].get_width(), self.player_images["RUN"][0].get_height()))
        self.got_hit = False

    def draw(self):
        if not self.jump:
            self.player_frame += 1
            image_to_draw = self.player_images["RUN"][self.player_frame]
            screen.blit(image_to_draw, (self.player_x, self.player_y))
            self.hitbox = Rect((self.player_x, self.player_y), (image_to_draw.get_width(), image_to_draw.get_height()))
            if self.player_frame == len(self.player_images["RUN"])-1:
                self.player_frame = 1

        elif self.jump:
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
        # Hit box - delete before production
        screen.draw.rect(self.hitbox, color="RED")

class ObstacleGeneration():
    def __init__(self, player):
        self.level = 1
        self.object_id = {1: 'spike'}
        self.obstacle_list = []
        self.player = player
        self.obstacle_x_buffer = player.width * 4 # minimum space between obstacles to allow for player to land

    def map_generator(self, probability = 0.005, frames = 5):
        game_map = [0] * WIDTH * 2 # First 2 frames of all games will have no objects generated
        for frame in range(1, frames+ 1):
            while len(game_map) < WIDTH * frame:
                rand = random()
                if rand < probability:
                    game_map.append(1)
                    for _ in range(self.obstacle_x_buffer):
                        if len(game_map) < WIDTH * frame:
                            game_map.append(0)
                else:
                    game_map.append(0)
        print(game_map)
        return game_map

class Spike(object):
    image = images.spike
    def __init__(self, speed, x = WIDTH, hitbox = Rect(0,0,0,0)):
        self.x = x
        self.hitbox = hitbox
        self.y = HEIGHT - TILESIZE - 15
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hit_once = False
        self.speed = speed

    def draw(self):
        screen.blit(self.image,(self.x,self.y))
        self.hitbox = Rect((self.x, self.y), (self.width, self.height))
        screen.draw.rect(self.hitbox, color="RED")
        self.x -= self.speed
        return self.hitbox

    def collide(self,rect):
        if self.hitbox.colliderect(rect):
            return True
        return False

game = GameState()
speed = game.speed
player = Character()
background = Background(speed=speed)
obstaclegeneration = ObstacleGeneration(player = player)
map = obstaclegeneration.map_generator(probability = 0.005, frames = 20)
obj_list = []
for pixel in enumerate(map):
    if pixel[1] == 1:
        obj_list.append(Spike(speed = speed, x=pixel[0]))

def draw():
    background.draw()
    player.draw()
    for obj in obj_list:
        obj.draw()

def game_loop():
    if game.game_over:
        return
    if keyboard.up:
        player.jump = True

    if game.player_hit == False:
        for obj in obj_list:
            if obj.collide(player.hitbox):
                game.make_vulnerable()

clock.schedule_interval(game_loop, 0.03)
pgzrun.go()