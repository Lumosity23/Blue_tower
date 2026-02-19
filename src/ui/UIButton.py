import pygame
from .UIElement import UIElement
from .UIText import UIText
from settings import Settings
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class UIButton(UIElement):

    def __init__(self, x, y, w, h, text, on_click_callback, color: tuple=(0, 0, 0), size_text: int=50, text_color: tuple=(255, 255, 255), border_radius: int=15, uid=None):
        # Init le text du bouton
        if uid:
            uid_text = f"{uid}_text"
        else: uid_text = None
        self.text = UIText(20, 10, text, size_text, text_color, uid=uid_text)
        super().__init__(x, y, self.text.rect.w + 40, self.text.rect.h + 20, uid)
        self.add_child(self.text)

        # Arrondi des coins du bouton
        self.border_radius = border_radius
        
        # Fonction qui realise lors de la pression du bouton
        self.callback = on_click_callback

        # Couleur
        self.color_idle: tuple = color
        self.color_hover: tuple = ()
        self.color_pressed: tuple = ()
        self.set_color(color)

        # Etat
        self.state = "IDLE"
        self.render()
        

    def set_color(self, color) -> None:

        # Savoir si c'est un couleur sombre ou claire
        r, g, b = color
        l = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
        
        if l > Settings.VISION_HUMAIN:
            for c in list(color):
                self.color_hover += (c * 0.9,)
        
        else:
            for c in color:
                new_color = 255 - c #c * 1.1
                if new_color == 255:
                    new_color -= 50
                elif new_color == 0:
                    new_color += 50
                self.color_hover += (new_color,)
        
        for c in list(color):
            self.color_pressed += (c * 0.8,)

    
    def draw(self, surface):
        super().draw(surface)

    def render(self) -> None:

        # On choisit la couleur selon l'état
        color = self.color_idle
        if self.state == "HOVER":
            color = self.color_hover
        elif self.state == "PRESSED":
            color = self.color_pressed

        # On dessine le rectangle arrondi avec la bonne couleur
        pygame.draw.rect(self.image, color, (0, 0, self.rect.w, self.rect.h), border_radius=self.border_radius)

    
    def handle_event(self, event: pygame.event.EventType) -> bool:
        abs_rect = self.get_absolute_rect()
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = abs_rect.collidepoint(mouse_pos)

        old_state = self.state

        # Logique de mise à jour de l'état
        if event.type == pygame.MOUSEMOTION:
            self.state = "HOVER" if is_hovered else "IDLE"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if is_hovered and event.button == 1:
                self.state = "PRESSED"
                if self.callback:
                    self.callback()
                # On force le render ici car l'état vient de changer
                self.render() 
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.state = "HOVER" if is_hovered else "IDLE"

        # Si changement d'etat
        if self.state != old_state:
            self.render()

        return False