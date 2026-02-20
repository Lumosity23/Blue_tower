import pygame
from settings import Settings


class Cell(pygame.sprite.Sprite):

    def __init__(self, posx: int, posy: int, cell_type: str):
        super().__init__()
        self.grid_x = posx
        self.grid_y = posy
        self.type = cell_type
        self.size = Settings.CELL_SIZE
        self.rect = pygame.Rect(posx * self.size, posy * self.size, self.size, self.size)
                            #   pos x             pos y             longeur x  largeur y
        self.isOccupied: bool = False