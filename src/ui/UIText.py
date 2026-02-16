from .UIElement import UIElement
from settings import Settings
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pygame


class UIText(UIElement):

    def __init__(self, x: int, y: int, callback: str | None, size_text: int=50, color: tuple=(255, 255, 255), align: str='topleft',text_update: bool=False, uid: str=None):
        '''
        callback: est la fonction que dois apperler l'element pour metre a jour son text, pas de fonction alors str\n
        size_text: 100 | 75 | 50 | 25 | 10\n
        color: ( R , G , B )\n
        align: topleft, bottomleft, topright, bottomright\n
               midtop, midleft, midbottom, midright\n
             center'''
        super().__init__(x, y, 0, 0, uid)

        self.uid = uid
        self.text = callback
        self.text_update = text_update
        self.color = color
        self.cache = {}
        self.st = Settings()
        self.font: pygame.font.Font = self.st.get_font(size_text)

        if not self.text_update:
            self.image = self.font.render(self.text, True, self.color)
        else:
            text = self.text()
            self.image = self.font.render(text, True, self.color)

        self.rect = self.image.get_rect()
        
        if hasattr(self.rect, align):
            # Alignement du rect
            setattr(self.rect, align, (x, y))
        
        else: print(f"Erreur lors de l'alignement du text avec : {align}")

    
    def update(self, dt):
        super().update(dt)
        
        # Si pas besoin d'upadte car text statique
        if not self.text_update:
            return
        
        # mise a jour du text
        text = self.text()

        # Si deja en cache alors on recupere
        if text in self.cache:
            self.image = self.cache[text].copy()

        # Si non on render et on cache pour la prochaine fois
        else:
            self.image = self.font.render(text, True, self.color)
            self.cache[text] = self.image