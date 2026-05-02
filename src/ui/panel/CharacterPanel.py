from typing import TYPE_CHECKING

from ui.element.UIButton import UIButton
from ui.element.UIIcon import UIIcon
from ui.element.UIPanel import UIPanel
from ui.element.UITourniquet import UITourniquet

if TYPE_CHECKING:
    from main import App


class CharacterPanel(UIPanel):
    """
    Panneau de personnalisation du personnage.
    Affiche le joueur en grand et un carrousel d'items.
    """

    def __init__(self, game: "App"):

        w, h = game.st.SCREEN_WIDTH * (3 / 4), game.st.SCREEN_HEIGHT * (3 / 4)
        x, y = game.st.SCREEN_WIDTH * (1 / 8), game.st.SCREEN_HEIGHT * (1 / 8)
        # On occupe tout l'écran
        super().__init__(x, y, w, h, color=(40, 40, 50), uid="CharacterPanel")
        self.game = game
        self.image.set_alpha(255)
        self.visible = False
        self.uid = "CharacterPanel"

        # Souscription
        self.game.eventManager.subscribe("SHOW_CHARACTER", self.show)

        # Titre
        self.set_label("CHARACTER", 120)

        # 1. Affichage du joueur en grand (Gauche)
        # On utilise une échelle de 5 comme demandé
        p_w, p_h = game.st.ENTITIES_DATA["PLAYER"]["size"]
        self.player_display = UIIcon(115, 290, uid=f"{self.uid}_player")

        # On récupère le sprite "player" via le SpriteManager
        player_img = self.game.spriteManager.get_sprite_resize(
            "anim_player_move", (p_w * 10, p_h * 10)
        )
        self.player_display.setup(player_img)
        self.add_child(self.player_display)

        # 2. UITourniquet (Droite)
        # Liste d'items fictifs pour la démo
        items = ["turret", "wall", "bank", "kernel", "enemy"]
        tourniquet_w = game.st.SCREEN_WIDTH // 2
        tourniquet_h = 400
        self.tourniquet = UITourniquet(
            self.rect.w // 2,
            self.rect.h // 2 - tourniquet_h // 2,
            tourniquet_w,
            tourniquet_h,
            items,
            uid=f"{self.uid}_tourniquet",
        )
        self.tourniquet.set_title("WEAPONS", size=60)
        self.add_child(self.tourniquet)

        # Bouton Select pour le tourniquet
        self.selected_item = None

        # On initialise le bouton (le centrage X sera forcé dynamiquement)
        self.select_btn = UIButton(
            0,
            self.rect.h // 2 + tourniquet_h // 2 + 20,
            "SELECT",
            self.select_item,
            uid=f"{self.uid}_select_btn",
        )
        self.select_btn.setup_toggle(
            text_off="SELECT",
            color_off=(50, 150, 50),
            text_on="SELECTED",
            color_on=(50, 50, 150),
        )
        self.add_child(self.select_btn)

        # 3. Bouton Retour
        self.back_btn = UIButton(
            50, 50, "X", self.go_back, (100, 100, 100), uid=f"{self.uid}_back"
        )
        self.add_child(self.back_btn)

    def select_item(self):
        """Récupère et sauvegarde l'item actuellement au centre du tourniquet."""
        # Comme le bouton gère son toggle, on regarde son état
        if self.select_btn.toggle_state:
            item = self.tourniquet.get_selected_item()
            if item:
                self.selected_item = item
                print(f"Item sélectionné : {self.selected_item}")
        else:
            self.selected_item = None
            print("Item désélectionné")

    def update(self, dt):
        """Vérifie si l'item courant correspond à la sélection pour mettre à jour le bouton."""
        super().update(dt)
        if not self.visible:
            return

        current_center_item = self.tourniquet.get_selected_item()
        is_selected = current_center_item == self.selected_item

        # Force l'état visuel du bouton selon la sélection réelle
        self.select_btn.set_toggle_state(is_selected)

        # Centrage dynamique (si le texte change, la largeur change)
        self.select_btn.rect.centerx = self.tourniquet.rect.centerx

    def go_back(self):
        """Retourne au menu principal."""
        self.game.eventManager.publish("MENU")
        self.visible = False

    def show(self):
        """Affiche le panneau et désactive les autres éléments du menu."""
        # On masque tous les autres panneaux (Menu, OSD, etc.)
        for child in self.game.ui_manager.root.children:
            child.visible = False

        # On ne centre le player_display que si aucune configuration (layout.json) n'est présente
        if not self.player_display.cfg_loaded:
            self.player_display.rect.center = (self.rect.w // 4, self.rect.h // 2)

        super().show()
