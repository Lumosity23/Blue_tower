import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class Building(pygame.sprite.Sprite):

    BUILDING_TYPES = {}

    def __init_subclass__(cls, **kargs):
        super().__init_subclass__(**kargs)
        
        # Nom de la classe enfants en maj
        # Enregistrement de la classe dans le dico
        cls.BUILDING_TYPES[cls.__name__.upper()] = cls


    def __init__(self, x, y, game: "App"):
        super().__init__()
        self.game = game
        self.pos = x, y

        # Valeur par defaut pour le building
        self.image = pygame.Surface((self.game.st.CELL_SIZE, self.game.st.CELL_SIZE))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(topleft=self.pos)
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.cost = 25

    
    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.die()
    

    def die(self):
        self.kill()