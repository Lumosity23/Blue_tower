from settings import Settings
import pygame

class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int=Settings.CELL_SIZE, height: int=Settings.CELL_SIZE, color: tuple=(0,153,153), align: str='topleft', alpha: bool=False):
        super().__init__()
        self.x = x
        self.y = y
        self.image = pygame.Surface((width, height))
        # Transparent
        if alpha:
            self.image.set_alpha(50)

        self.color = self.image.fill(color)

        if align == 'bottom':
            self.rect = self.image.get_rect(bottom=(x, y))

        elif align == 'midtop':
            self.rect = self.image.get_rect(midtop=(x, y))

        elif align == 'midleft':
            self.rect = self.image.get_rect(midleft=(x, y))

        elif align == 'center':
            self.rect = self.image.get_rect(center=(x, y))

        elif align == 'topright':
            self.rect = self.image.get_rect(topright=(x, y))

        else: self.rect = self.image.get_rect(topleft=(x, y))