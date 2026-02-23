import pygame
from .UIElement import UIElement
from .UIText import UIText


class UIPanel(UIElement):

    def __init__(self, x, y, w, h, color=(50, 50, 50), uid: str=None):
        super().__init__( x, y, w, h, uid )
        self.image.fill(color)
        self.image.set_alpha(200)

        self.border_color = (255, 255, 255) # Blanc par defaut
        self.border_width = 2 # Pixel
    

    def set_label(self, text) -> None:
        self.label = UIText(self.rect.centerx, self.rect.top - 30, text, 100, uid="text_panel")
        self.add_child(self.label)
    
    def draw(self, surface):
        super().draw(surface)
    
        if not self.visible:
            return
        
        if not self.debug:
            abs_rect = self.get_absolute_rect()
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
            
            
        