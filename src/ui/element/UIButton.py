import pygame

from .UIElement import UIElement
from .UIText import UIText


class UIButton(UIElement):
    def __init__(
        self,
        x,
        y,
        text,
        on_click_callback,
        color: tuple[int, int, int] = (0, 0, 0),
        size_text: int = 50,
        text_color: tuple[int, int, int] = (255, 255, 255),
        border_radius: int = 15,
        uid=None,
    ):
        # Init le text du bouton
        if uid:
            uid_text = f"{uid}_text"
        else:
            uid_text: str | None = None
        self.text = UIText(20, 10, text, size_text, text_color, uid=uid_text)

        super().__init__(x, y, self.text.rect.w + 40, self.text.rect.h + 20, uid)
        self.add_child(self.text)
        self.text.rect.topleft = 20, 10
        self.type = "button"

        # Arrondi des coins du bouton
        self.border_radius = border_radius

        # Fonction qui realise lors de la pression du bouton
        self.callback = on_click_callback
        self.sound = "click_default"

        # Variables pour le mode Toggle
        self.current_color = color
        self.is_toggle = False
        self.toggle_state = False
        self.toggle_config = {}

        # Couleur
        self.shape = {}
        self.set_color(color)

        # Etat
        self.state = "IDLE"
        self.image = self.shape[self.state]

    def set_color(self, color) -> None:
        self.current_color = color
        # Savoir si c'est un couleur sombre ou claire
        color_pressed = ()
        color_hover = ()

        r, g, b = color
        l = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)

        if l > 128:
            for c in list(color):
                color_hover += (c * 0.9,)

        else:
            for c in color:
                new_color = 255 - c  # c * 1.1
                if new_color == 255:
                    new_color -= 50
                elif new_color == 0:
                    new_color += 50
                color_hover += (new_color,)

        for c in list(color):
            color_pressed += (int(c * 0.8),)

        state_color = {"IDLE": color, "HOVER": color_pressed, "PRESSED": color_hover}

        self.shape = self.make_shape_from_color(state_color)
        # Met à jour l'image immédiatement si on est déjà initialisé
        if hasattr(self, "state") and self.state in self.shape:
            self.image = self.shape[self.state]

    def make_shape_from_color(self, dico_color) -> dict[str, pygame.Surface]:

        panel = self._SPRITE.get_ui_panel
        dico = {}

        for state, color in dico_color.items():
            img = panel(self.rect.w, self.rect.h, color)
            dico[state] = img

        return dico

    def set_sound(self, sound: str) -> None:
        self.sound = sound

    def set_text(self, text: str) -> None:
        """Modifie le texte et adapte automatiquement la taille du bouton."""
        self.text.set_text(text)
        # Recalcul de la taille
        self.rect.w = self.text.rect.w + 40
        self.rect.h = self.text.rect.h + 20
        # Régénère le fond avec la nouvelle taille
        self.set_color(self.current_color)

    def setup_toggle(
        self,
        text_off: str,
        color_off: tuple,
        text_on: str,
        color_on: tuple,
        start_state: bool = False,
    ) -> None:
        """Configure le bouton comme un interrupteur à deux états (On/Off)."""
        self.is_toggle = True
        self.toggle_config = {
            False: {"text": text_off, "color": color_off},
            True: {"text": text_on, "color": color_on},
        }
        self.set_toggle_state(start_state)

    def update_toggle_visuals(self) -> None:
        """Met à jour l'apparence selon l'état du toggle."""
        if not self.is_toggle:
            return
        cfg = self.toggle_config[self.toggle_state]
        self.text.set_text(cfg["text"])
        self.rect.w = self.text.rect.w + 40
        self.rect.h = self.text.rect.h + 20
        self.set_color(cfg["color"])

    def set_toggle_state(self, state: bool) -> None:
        """Force le bouton dans un état spécifique sans déclencher le callback."""
        if self.toggle_state != state or not self.shape:
            self.toggle_state = state
            self.update_toggle_visuals()

    def render(self) -> None:

        # On choisit la couleur selon l'état
        state = self.shape["IDLE"]
        if self.state == "HOVER":
            state = self.shape["HOVER"]
        elif self.state == "PRESSED":
            state = self.shape["PRESSED"]

        # On dessine le rectangle arrondi avec la bonne couleur
        # pygame.draw.rect(self.image, color, (0, 0, self.rect.w, self.rect.h), border_radius=self.border_radius)  # (0, 0, self.rect.w, self.rect.h)
        self.image = self.shape[state]

    def handle_event(self, event: pygame.event.EventType) -> bool:
        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = abs_rect.collidepoint(mouse_pos)

        old_state = self.state

        # Logique de mise à jour de l'état
        if event.type == pygame.MOUSEMOTION:
            self.state = "HOVER" if is_hovered else "IDLE"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if is_hovered and event.button == 1:
                self.state = "PRESSED"

                # Gestion du basculement (toggle)
                if self.is_toggle:
                    self.toggle_state = not self.toggle_state
                    self.update_toggle_visuals()

                if self.callback:
                    self._EVENTBUS.publish("CLICK_BUTTON", self.sound)
                    self.callback()

                # On force le render ici car l'état vient de changer
                self.image = self.shape[self.state]
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.state = "HOVER" if is_hovered else "IDLE"

        # Si changement d'etat
        if self.state != old_state:
            self.image = self.shape[self.state]

        return False
