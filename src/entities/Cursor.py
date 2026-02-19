import pygame
from grid import Grid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App
    from entities.buildings.Building import Building


class Cursor(pygame.sprite.Sprite):
    
    def __init__(self, game: "App"):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((self.game.st.CELL_SIZE, self.game.st.CELL_SIZE))
        self.image.set_alpha(50)
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.cell_isOccupied = False


    def update(self, dt):
        # aimentation du cursor de build
        mx, my = pygame.mouse.get_pos()
        px = (mx // self.game.st.CELL_SIZE) * self.game.st.CELL_SIZE
        py = (my // self.game.st.CELL_SIZE) * self.game.st.CELL_SIZE
        self.rect.topleft = (px, py)

        # checker si pas sur un element
        cell_val = self.game.grid.get_cell_value(mx, my)

        if cell_val != self.game.st.EMPTY:
            self.image.fill((255,51,51))
            self.cell_isOccupied = True
            return

        for sprite in self.game.all_sprites:
            # Si ce n'est pas un mur (donc c'est un joueur ou ennemi)
            sprite: "Building"
            if sprite not in self.game.builds:
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
    
    
    def handle_event(self, event) -> bool:

        pass