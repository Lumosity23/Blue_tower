from .UIElement import UIElement
import pygame


class UIIcon(UIElement):

    def __init__(self, x, y, uid=None):
        super().__init__(x, y, 0, 0, uid)
        self.type = "icon"
    
    def setup(self, sprite: pygame.Surface) -> None:

        self.image = sprite
        self.rect = self.image.get_rect()

        