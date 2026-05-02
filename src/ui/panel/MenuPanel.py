from typing import TYPE_CHECKING, Optional

from ui.element.UIButton import UIButton
from ui.element.UIPanel import UIPanel

if TYPE_CHECKING:
    from main import App


class MenuPanel(UIPanel):
    """Panneau du menu principal de l'application."""

    # --- Constantes (Évite les "Nombres Magiques" dispersés dans le code) ---
    BG_COLOR = (45, 45, 45)
    BTN_DEFAULT_COLOR = (100, 100, 100)
    BTN_DANGER_COLOR = (255, 0, 0)

    # Textes du menu
    TEXT_HOW_TO_PLAY = (
        "HOW TO PLAY : use arrows/WASD to move around and G for open/close the shop..."
    )
    TEXT_MORE_INFO = "For more information --> README of the repo on GitHub : "
    TEXT_ADDRESS = "https://github.com/Lumosity23/Blue_tower.git"

    def __init__(self, game: "App", uid: Optional[str] = "MenuPanel") -> None:
        # Calcul des dimensions pour plus de clarté
        width = game.st.SCREEN_WIDTH + 100
        height = game.st.SCREEN_HEIGHT + 100

        super().__init__(-50, -50, width, height, self.BG_COLOR, uid)

        self.game = game
        self.st = game.st
        self.visible = False
        self.uid = uid  # Utilise l'UID passé en paramètre ou la valeur par défaut

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialise et assemble tous les composants de l'interface utilisateur."""
        self.set_label("Blue Tower", 200)
        prefix = f"{self.uid}_"

        # --- Création des Boutons ---
        btn_play = UIButton(
            100,
            100,
            "PLAY",
            self.play,
            self.BTN_DEFAULT_COLOR,
            size_text=70,
            uid=f"{prefix}btn_play",
        )
        btn_play.set_sound("PLAY")

        btn_settings = UIButton(
            100,
            100,
            "SETTINGS",
            self.open_settings,
            self.BTN_DANGER_COLOR,
            size_text=70,
            uid=f"{prefix}btn_settings",
        )

        btn_character = UIButton(
            100,
            100,
            "CHARACTER",
            self.open_character,
            self.BTN_DEFAULT_COLOR,
            size_text=70,
            uid=f"{prefix}btn_character",
        )

        btn_quit = UIButton(
            100,
            100,
            "QUIT",
            self.quit,
            self.BTN_DANGER_COLOR,
            size_text=70,
            uid=f"{prefix}btn_quit",
        )

        # --- Création des Textes ---
        # self.text_how_to = UIText(20, 400, self.TEXT_HOW_TO_PLAY, uid=f"{prefix}text_how_to_play", size_text=40)
        # self.text_info = UIText(20, 400, self.TEXT_MORE_INFO, uid=f"{prefix}text_more_info", size_text=40)
        # self.text_address = UIText(20, 400, self.TEXT_ADDRESS, uid=f"{prefix}text_address", size_text=30)

        # --- Bouton Demo UI en bas à gauche ---
        btn_demo_ui = UIButton(
            50,
            900,
            "DEMO UI",
            self.open_demo_ui,
            (50, 150, 200),
            size_text=50,
            uid=f"{prefix}btn_demo_ui",
        )

        # --- Ajout des enfants au panneau ---
        # Utiliser une boucle rend le code plus propre et facile à modifier
        components = [
            # self.text_info,
            # self.text_address,
            # self.text_how_to,
            btn_quit,
            btn_character,
            btn_settings,
            btn_play,
            btn_demo_ui,
        ]

        for component in components:
            self.add_child(component)

    # --- Callbacks d'événements ---
    def open_demo_ui(self) -> None:
        self.game.eventManager.publish("SHOW_DEMO_UI")

    def open_character(self) -> None:
        self.game.eventManager.publish("SHOW_CHARACTER")

    def open_settings(self) -> None:
        self.game.eventManager.publish("OPEN_SETTINGS", "MENU")

    def quit(self) -> None:
        self.game.eventManager.publish("QUIT")

    def play(self) -> None:
        self.game.eventManager.publish("NEW_GAME")
