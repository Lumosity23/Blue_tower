import pygame
from .UIElement import UIElement
from settings import Settings
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class UIButton(UIElement):

    def __init__(self, x, y, w, h, game, text, on_click_callback, color: tuple=(0, 0, 0), size_text: int=50):
        super().__init__(x, y, w, h, game)
        self.text = text
        self.size_text = size_text
        self.callback = on_click_callback

        # Couleur
        self.color_idle: tuple = color
        self.color_hover: tuple = ()
        self.color_pressed: tuple = ()
        self.set_color(color)

        # Etat
        self.state = "IDLE"
        self.image.set_alpha(1000)
        self.image.fill(self.color_idle)
        

    def set_color(self, color) -> None:

        # Savoir si c'est un couleur sombre ou claire
        r, g, b = color
        l = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
        
        if l > Settings.VISION_HUMAIN:
            for c in list(color):
                self.color_hover += (c * 0.9,)
        
        else:
            for c in list(color):
                new_color = c * 1.1
                if new_color > 255:
                    new_color = 255
                self.color_hover += (new_color,)
        
        for c in list(color):
            self.color_pressed += (c * 0.8,)

    
    def draw(self, surface):
        super().draw(surface)
        if self.visible:
            self.game.spriteManager.draw_text(self.game._display_surf, self.text, self.absolute_rect.centerx, self.absolute_rect.centery, align='center', size=self.size_text)


    def handle_event(self, event: pygame.event.EventType) -> bool:

        abs_rect = self.get_absolute_rect()
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = abs_rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEMOTION:
            if is_hovered:
                self.image.fill(self.color_hover)
            else:
                self.image.fill(self.color_idle)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if is_hovered and event.button == 1:
                self.image.fill(self.color_pressed)

            if self.callback:
                self.callback()
            return True

        if event.type == pygame.MOUSEBUTTONUP:
            if is_hovered:
                self.image.fill(self.color_hover)
            else:
                self.image.fill(self.color_idle)

        return False