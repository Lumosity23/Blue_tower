import pygame
from settings import Settings
from grid import Grid

class Cursor(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((Settings.CELL_SIZE, Settings.CELL_SIZE))
        self.image.set_alpha(50)
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.cell_isOccupied = False


    def update(self, dt, walls, grid: Grid, player, enemis, all_sprites, wallet):
        # aimentation du cursor de build
        mx, my = pygame.mouse.get_pos()
        px = (mx // Settings.CELL_SIZE) * Settings.CELL_SIZE
        py = (my // Settings.CELL_SIZE) * Settings.CELL_SIZE
        self.rect.topleft = (px, py)

        # checker si pas sur un element
        cell_val = grid.get_cell_value(mx, my)

        if cell_val != Settings.EMPTY:
            self.image.fill((255,51,51))
            self.cell_isOccupied = True
            return

        for sprite in all_sprites:
            # Si ce n'est pas un mur (donc c'est un joueur ou ennemi)
            if sprite not in walls:
                if sprite != self:
                    if self.rect.colliderect(sprite.rect):
                        self.image.fill((255,51,51))
                        self.cell_isOccupied = True
                        return

        else:         
            self.image.fill((255,255,255))
            self.cell_isOccupied = False
            return

        #self.image.set_alpha(50)
