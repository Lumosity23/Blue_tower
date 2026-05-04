import pygame

from .UIElement import UIElement
from .UIText import UIText


class UISlider(UIElement):
    """
    Composant Slider pour régler des valeurs numériques (0.0 à 1.0).
    Utilise la DA du jeu (rectangles et carrés via get_ui_panel).
    """

    def __init__(
        self, x, y, w, h, initial_value=0.5, on_change_callback=None, uid=None
    ):
        super().__init__(x, y, w, h, uid)

        self.type = "slider"
        self.value = initial_value
        self.callback = on_change_callback

        # Design
        self.bar_h = h  # Hauteur de la barre de fond
        self.cursor_size = h  # Le curseur prend toute la hauteur du composant

        # Etat
        self.is_dragging = False
        self.is_hovered = False

        # Texte de valeur
        self.value_text = UIText(
            w + 20,
            h // 2,
            self.get_value_string,
            size_text=30,
            align="midleft",
            text_update=True,
            uid=f"{uid}_val" if uid else None,
        )
        self.add_child(self.value_text)

        self.render_slider()

    def get_value_string(self) -> str:
        return f"{int(self.value * 100)}%"

    def render_slider(self):
        self.image.fill((0, 0, 0, 0))

        # 1. Dessin de la barre de fond (centrée verticalement)
        bar_y = (self.rect.h - self.bar_h) // 2
        bar_color = (80, 80, 80)
        if self.is_hovered:
            bar_color = (100, 100, 100)

        bar_panel = self._SPRITE.get_ui_panel(self.rect.w, self.bar_h, color=bar_color)
        self.image.blit(bar_panel, (0, bar_y))

        # 2. Dessin du curseur (Carré)
        cursor_color = (200, 200, 200)
        if self.is_dragging:
            cursor_color = (255, 255, 255)

        cursor_panel = self._SPRITE.get_ui_panel(
            self.cursor_size, self.cursor_size, color=cursor_color
        )

        # Position X du curseur basée sur la valeur
        # On soustrait la taille du curseur pour qu'il ne dépasse pas
        cursor_x = (self.rect.w - self.cursor_size) * self.value
        self.image.blit(cursor_panel, (int(cursor_x), 0))

    def update_value_from_pos(self, mouse_x):
        abs_rect = self.get_screen_rect()
        # On calcule le ratio (0.0 à 1.0)
        relative_x = mouse_x - abs_rect.x - (self.cursor_size // 2)
        max_dist = self.rect.w - self.cursor_size

        new_value = max(0.0, min(1.0, relative_x / max_dist))

        if new_value != self.value:
            self.value = new_value
            self.render_slider()
            if self.callback:
                self.callback(self.value)

    def handle_event(self, event: pygame.event.EventType) -> bool:
        if not self.visible:
            return False

        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = abs_rect.collidepoint(mouse_pos)

        if was_hovered != self.is_hovered:
            self.render_slider()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_dragging = True
                self.update_value_from_pos(mouse_pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                self.render_slider()
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.update_value_from_pos(mouse_pos[0])
                return True

        return super().handle_event(event)
