# To run this game, open a command prompt terminal, type in: cd <the folder path this script is in>. Then type in the command :pgzrun game.py
import pgzrun
import time
import random

# ---GLOBAL GAME VARIABLES--- #
WIDTH = 800
HEIGHT = 450
TILESIZE = images.dirt.get_height()

class GameState():
    game_over = False
    score = 0
    player_hit = False

class Character():
    player_images = {"RUN":
                         [images.player0, images.player1, images.player2, images.player3,
                          images.player4, images.player5, images.player6, images.player7,
                          images.player8, images.player9, images.player10, images.player11,
                          images.player12, images.player13, images.player14, images.player15,
                          images.player16, images.player17],
                     "JUMP":
                         [images.jump0, images.jump1]}

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
            time.sleep(0.03)
            if self.player_frame == 17:
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

    def player_hit(self):
        sounds.eep.play()
        print('hit')


class Background():
    images = {"background": images.background,
              "dirt" : images.dirt,
              "grass" : images.grassbackground
    }

    def __init__(self):
        self.dirt_height = self.dirt_width = self.grass_height = TILESIZE
        self.grass_width = self.images["grass"].get_width()
        self.background_x = 0
        self.background2_x = self.images["background"].get_width()
        self.grass_x = 0
        self.grass2_x = self.images["grass"].get_width()
        self.grass_y = HEIGHT - TILESIZE

    def draw(self):
        screen.blit(self.images["background"], (self.background_x, 0))
        screen.blit(self.images["background"], (self.background2_x, 0))
        screen.blit(self.images["grass"], (self.grass_x, self.grass_y))
        screen.blit(self.images["grass"], (self.grass2_x, self.grass_y))

        self.background_x -= 5
        self.background2_x -= 5
        self.grass_x -= 5
        self.grass2_x -= 5

        if self.background_x < self.images["background"].get_width() * -1:
            self.background_x = self.images["background"].get_width()

        if self.background2_x < self.images["background"].get_width() * -1:
            self.background2_x = self.images["background"].get_width()

        if self.grass_x < self.images["grass"].get_width() * -1:
            self.grass_x = self.images["grass"].get_width()

        if self.grass2_x < self.images["grass"].get_width() * -1:
            self.grass2_x = self.images["grass"].get_width() - 2

class ObstacleGeneration():
    def __init__(self):
        self.level = 1
        self.empty_map_width = [0] * WIDTH
        self.object_id = {1: 'spike'}
        self.obstacle_list = []

    def map_width_generator(self, probability):
        map_width = self.empty_map_width
        for pixel in enumerate(map_width):
            rand = random.random()
            if rand < probability:
                map_width[pixel[0]] = 1
        return map_width

    def obstacale_generator(self,objectid,x):
        #[objectid, x, y]
        self.obstacle_list.append([objectid,x,HEIGHT - TILESIZE - 15])

class Spike(object):
    image = images.spike
    def __init__(self, x = WIDTH,hitbox = Rect(0,0,0,0)):
        self.x = x
        self.hitbox = hitbox
        self.y = HEIGHT - TILESIZE - 15
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        #self.hitbox = Rect((x, self.y), (self.width, self.height))
        self.hit_once = False

    def draw(self):
        screen.blit(self.image,(self.x,self.y))
        self.hitbox = Rect((self.x, self.y), (self.width, self.height))
        screen.draw.rect(self.hitbox, color="RED")
        self.x -= 5
        return self.hitbox

    def collide(self,rect):
        if self.hitbox.colliderect(rect):
            return True
        return False

game = GameState()
player = Character()
background = Background()
obstaclegeneration = ObstacleGeneration()
#spike = Spike()
map = obstaclegeneration.map_width_generator(0.005)
obj_list = []
for pixel in enumerate(map):
    if pixel[1] == 1:
        obj_list.append(Spike(x=pixel[0]))

def draw():
    background.draw()
    player.draw()
    for obj in obj_list:
        obj.draw()


def game_loop():
    if GameState.game_over:
        return
    if keyboard.up:
        player.jump = True

    if game.player_hit == False:
        for obj in obj_list:
            if obj.collide(player.hitbox):
                player.player_hit()
                game.player_hit = True

clock.schedule_interval(game_loop, 0.03)
pgzrun.go()