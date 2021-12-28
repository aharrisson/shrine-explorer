import pygame
from pygame.locals import *
from pygame.math import Vector2 as vector
import pytmx
import sys
import random

pygame.init()

# Game constants
SCREEN_WIDTH = 64 * 32
SCREEN_HEIGHT = 32 * 32
FPS = 60

# Physics constants
ACCELERATION = 0.5
FRICTION = -0.12

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platform game")


class SpriteSheet(object):
    def __init__(self, fileName, tile_width, tile_height):
        self.sheet = pygame.image.load(fileName)
        self.tile_width = tile_width
        self.tile_height = tile_height

    def image_at(self, row, column):
        rectangle = pygame.Rect(
            (
                self.tile_width * column,
                self.tile_height * row,
                self.tile_width,
                self.tile_height,
            )
        )
        image = pygame.Surface(rectangle.size, pygame.SRCALPHA, 32).convert_alpha()
        image.blit(self.sheet, (0, 0), rectangle)
        return image


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.spritesheet = SpriteSheet("images/player.png", 64, 64)
        self.sprite = 0
        self.surf = self.spritesheet.image_at(9, self.sprite)
        self.rect = self.surf.get_rect()

        self.pos = vector((10, 360))
        self.vel = vector(0, 0)
        self.acc = vector(0, 0)

    def move(self):
        self.acc = vector(0, ACCELERATION)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACCELERATION
            self.sprite = 0 if self.sprite > 7 else self.sprite + 1
            self.surf = self.spritesheet.image_at(9, self.sprite)
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACCELERATION
            self.sprite = 0 if self.sprite > 7 else self.sprite + 1
            self.surf = self.spritesheet.image_at(11, self.sprite)
        self.acc.x += self.vel.x * FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.x > SCREEN_WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = SCREEN_WIDTH
        self.rect.midbottom = self.pos

    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.vel.y = -15

    def update(self):
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            if collisions:
                self.vel.y = 0
                self.pos.y = collisions[0].rect.top + 1


class Platform(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height):
        super().__init__()
        self.rect = pygame.Rect(pos_x, pos_y, width, height)

    def move(self):
        pass


class TiledMap:
    def __init__(self, map_file):
        self.tiled_map = pytmx.load_pygame(map_file, pixels_alpha=True)
        self.tiles = []
        for layer in self.tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        self.tiles.append(
                            (
                                tile,
                                x * self.tiled_map.tilewidth,
                                y * self.tiled_map.tileheight,
                            )
                        )
        self.platforms = []
        for platform in self.tiled_map.objects:
            if platform.name == "platform":
                self.platforms.append(
                    Platform(platform.x, platform.y, platform.width, platform.height)
                )

    def draw(self):
        for tile in self.tiles:
            screen.blit(tile[0], (tile[1], tile[2]))


map = TiledMap("maps/map.tmx")
player = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(player)

platforms = pygame.sprite.Group()
for platform in map.platforms:
    platforms.add(platform)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player.jump()

    screen.fill((0, 0, 0))
    map.draw()
    player.update()

    for entity in all_sprites:
        entity.move()
        screen.blit(entity.surf, entity.rect)

    pygame.display.update()
    clock.tick(FPS)
