import pygame
from settings import *
from sprite_custom import *


class Kernel(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.size = (Settings.KERNEL_SIZE, Settings.KERNEL_SIZE)
        self.image = get_custom_sprite(Settings.KERNEL_SPRITE, self.size, 'circle')
        self.rect = self.image.get_rect(center=(Settings.SCREEN_WIDTH / 2, Settings.SCREEN_HEIGHT / 2))
        self.pos = self.rect.x, self.rect.y
        self.max_hp = Settings.KERNEL_HP
        self.current_hp = self.max_hp
        self.alive = True

    
    def take_damage(self, damage: int) -> None:
        self.current_hp -= damage
        # si 0 HP alors -> mort
        if self.current_hp <= 0:
            self.alive = False


    def reset(self):
        self.current_hp = self.max_hp
        self.damage = self.current_hp
        self.alive = True