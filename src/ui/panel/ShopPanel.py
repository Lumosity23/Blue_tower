import pygame
from ui.UIPanel import UIPanel
from ui.UIButton import UIButton
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class ShopPanel(UIPanel):

    def __init__(self, game: "App"):
        self.game = game
        self.st = self.game.st
        super().__init__(self.st.SCREEN_WIDTH - 340, 40, 500, self.st.SCREEN_HEIGHT - 80)
        self.uid = "ShopPanel"
        self.visible = False

        if self.uid:
            child_uid = f"{self.uid}_"
        else:
            child_uid = ""

        # 2. Création des Boutons DANS le panneau
        btn_wall = UIButton(10, 10, 120, 80, "Wall", self.buy_wall, (154, 139, 230), 50, uid=f"{child_uid}btn_wall_buy")
        self.add_child(btn_wall)
        
        btn_turret = UIButton(140, 10, 120, 80, "Tourelle", self.buy_turret, (25, 100, 155), 25, uid=f"{child_uid}btn_turret_buy")
        self.add_child(btn_turret)

        btn_test = UIButton(140, 10, 120, 80, "I", self.buy_turret, (25, 100, 155), 25, border_radius=25, uid=f"{child_uid}btn_test")
        self.add_child(btn_test)

    def buy_wall(self):
        # Ici tu appelles ton EventBus ou ton BuildManager
        self.game.buildManager.attemp_build(pygame.mouse.get_pos(), "WALL")

    def buy_turret(self):
        self.game.buildManager.attemp_build(pygame.mouse.get_pos(), "TURRET")