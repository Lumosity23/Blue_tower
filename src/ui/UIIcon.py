from .UIElement import UIElement
from .UIText import UIText
import pygame


class UIIcon(UIElement):

    def __init__(self, x, y, uid=None):
        super().__init__(x, y, 0, 0, uid)
        self.type = "icon"
    
    def setup(self, sprite: pygame.Surface) -> None:

        self.image = sprite
        self.rect = self.image.get_rect()
    

    def custom_setup(self, x, y, label, sprite: pygame.Surface, **kwargs) -> None:
        
        # Nettoyer d'abord les anciens enfants
        self.remove_all_child()

        # Setup des nouveaux parametres
        self.image = sprite
        self.rect.topleft = x, y
        self.label = UIText(0, 0, label, 200, uid="icon_text")
        self.label.rect.midtop = self.rect.width / 2, self.rect.height + 10
        self.add_child(self.label)

        