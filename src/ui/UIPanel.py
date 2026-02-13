import pygame
from .UIElement import UIElement
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class UIPanel(UIElement):

    def __init__(self, x, y, w, h, game: "App", color=(50, 50, 50)):
        super().__init__(x, y, w, h, game)
        self.image.fill(color)
        self.image.set_alpha(200)

        self.border_color = (255, 255, 255) # Blanc par defaut
        self.border_width = 2 # Pixel

    
    def draw(self, surface):
        super().draw(surface)
    
        if not self.visible:
            return
        
        else:
            abs_rect = self.get_absolute_rect()
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
        