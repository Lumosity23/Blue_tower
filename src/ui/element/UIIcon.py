from .UIElement import UIElement
from .UIText import UIText
import pygame


class UIIcon(UIElement):

    def __init__(self, x, y, uid=None):
        super().__init__(x, y, 0, 0, uid)
        self.type = "icon"
    
    def setup(self, sprite: pygame.Surface) -> None:

        self.image = sprite
        x, y = self.rect.topleft
        self.rect = self.image.get_rect(**{"topleft": (x, y)})
    

    def custom_setup(self, mid_pos, y, label, sprite: pygame.Surface, **kwargs) -> None:
        
        # Nettoyer d'abord les anciens enfants
        self.remove_all_child()

        # Setup des nouveaux parametres
        self.image = sprite
        
        # On ne redéfinit la position que si aucune config n'a été chargée
        if not self.cfg_loaded:
            self.rect = self.image.get_rect()
            self.rect.midtop = mid_pos, y
        else:
            # Sinon on garde le topleft chargé mais on met à jour la taille via l'image
            x, y = self.rect.topleft
            self.rect = self.image.get_rect(topleft=(x, y))

        self.label = UIText(0, 0, label)
        self.label.rect.midtop = self.rect.width / 2, self.rect.height + 10
        self.add_child(self.label)

        