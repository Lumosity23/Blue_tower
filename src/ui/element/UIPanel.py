from .UIElement import UIElement
from .UIText import UIText


class UIPanel(UIElement):
    def __init__(self, x, y, w, h, color=(91, 110, 225), uid: str = None):
        super().__init__(x, y, w, h, uid)

        self.image = self._SPRITE.get_ui_panel(w, h, color=color)
        self.image.set_alpha(230)

        self.border_color = (255, 255, 255)  # Blanc par defaut
        self.border_width = 2  # Pixel

        self.type = "panel"

    def set_label(self, text, size_text: int = 100) -> None:
        self.label = UIText(
            self.rect.centerx,
            self.rect.top - 30,
            text,
            size_text,
            uid=f"{text}_text_panel",
        )
        self.add_child(self.label)

    def draw(self, surface):

        if not self.visible:
            return

        super().draw(surface)

        """ if not self.debug:
            abs_rect = self.get_screen_rect()
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width) """
