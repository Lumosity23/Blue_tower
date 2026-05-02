from typing import TYPE_CHECKING

from ui.element.UIButton import UIButton
from ui.element.UIPanel import UIPanel
from ui.element.UIScroll import UIScroll
from ui.element.UISwitch import UISwitch
from ui.element.UIText import UIText
from ui.element.UITourniquet import UITourniquet

if TYPE_CHECKING:
    from main import App


class DemoUIPanel(UIPanel):
    """
    Panneau de démonstration pour tester les capacités de UIScroll
    en hébergeant divers composants UI (UIButton, UISwitch, UITourniquet, etc.)
    """

    def __init__(self, game: "App", uid="DemoUIPanel"):

        w = game.st.SCREEN_WIDTH - 200
        h = game.st.SCREEN_HEIGHT - 200

        super().__init__(100, 100, w, h, color=(40, 40, 50), uid=uid)

        self.game = game
        self.visible = False

        self.set_label("Demo UI Scroll", 100)

        # Création de la zone scrollable (UIScroll)
        scroll_w = w - 100
        scroll_h = h - 250
        self.scroll = UIScroll(
            50, 200, scroll_w, scroll_h, color=(30, 30, 35), uid=f"{uid}_scroll"
        )

        current_y = 30

        # 1. Titre informatif
        txt_title = UIText(
            50,
            current_y,
            "Demonstration des capacites du UIScroll",
            size_text=50,
            color=(200, 200, 255),
        )
        self.scroll.add_child(txt_title)
        current_y += 100

        # 2. Ajout de boutons
        for i in range(3):
            btn = UIButton(
                50,
                current_y,
                f"Test Action {i + 1}",
                lambda val=i: print(f"Demo Action : Clic sur le bouton {val + 1} !"),
                size_text=35,
                color=(100, 100, 200),
                uid=f"{uid}_btn_{i}",
            )
            self.scroll.add_child(btn)
            current_y += 80

        current_y += 40

        # 3. Ajout de Switchs
        txt_switch = UIText(50, current_y, "Test des UISwitch :", size_text=40)
        self.scroll.add_child(txt_switch)
        current_y += 70

        for i in range(3):
            sw = UISwitch(
                50,
                current_y,
                f"Option de fou {i + 1}",
                lambda val=i: print(f"Demo Action : Switch {val + 1} change d'etat !"),
                start_state=(i % 2 == 0),
                size_text=35,
                color_on=(50, 150, 50),
                color_off=(150, 50, 50),
                uid=f"{uid}_sw_{i}",
            )
            self.scroll.add_child(sw)
            current_y += 90

        current_y += 50

        # 4. Ajout d'un UITourniquet pour tester l'imbrication
        txt_tourniquet = UIText(
            50, current_y, "Test d'un UITourniquet imbrique :", size_text=40
        )
        self.scroll.add_child(txt_tourniquet)
        current_y += 60

        items = ["turret", "wall", "bank", "kernel", "enemy"]
        t_w = 600
        t_h = 300

        # Centré dans le scroll
        tourniquet = UITourniquet(
            scroll_w // 2,
            current_y + t_h // 2,
            t_w,
            t_h,
            items,
            uid=f"{uid}_tourniquet",
        )
        tourniquet.set_title("Demo Tourniquet", size=50)
        self.scroll.add_child(tourniquet)

        current_y += t_h + 100

        # 5. Longue liste pour s'assurer que le scroll a de quoi défiler
        txt_list = UIText(
            50, current_y, "Encore des elements pour faire defiler :", size_text=40
        )
        self.scroll.add_child(txt_list)
        current_y += 70

        for i in range(15):
            txt = UIText(
                80,
                current_y,
                f"Element de remplissage n° {i + 1}",
                size_text=30,
                color=(150, 150, 150),
            )
            self.scroll.add_child(txt)
            current_y += 50

        self.add_child(self.scroll)

        # Bouton Retour (Fixe en haut à gauche, en dehors du scroll)
        back_btn = UIButton(
            40,
            40,
            "X",
            self.go_back,
            (200, 50, 50),
            size_text=50,
            uid=f"{uid}_back_btn",
        )
        self.add_child(back_btn)

    def go_back(self):
        """Retourne au menu principal."""
        self.game.eventManager.publish("MENU")
        self.visible = False
