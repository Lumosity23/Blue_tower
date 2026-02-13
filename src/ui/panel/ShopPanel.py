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
        super().__init__(self.st.SCREEN_WIDTH - 340, 40, 300, self.st.SCREEN_HEIGHT - 80, self.game)
        self.visible = False

        # 2. Création des Boutons DANS le panneau
        # Note : x=10 est relatif au panneau (donc 20 pixels du bord gauche de l'écran)
        btn_wall = UIButton(10, 10, 120, 80, self.game, "Wall", self.buy_wall, (154, 139, 230), 50)
        self.add_child(btn_wall)
        
        btn_turret = UIButton(140, 10, 120, 80, self.game, "Tourelle", self.buy_turret, (25, 100, 155), 25)
        self.add_child(btn_turret)

    def buy_wall(self):
        # Ici tu appelles ton EventBus ou ton BuildManager
        self.game.buildManager.attemp_build(pygame.mouse.get_pos(), "WALL")

    def buy_turret(self):
        self.game.buildManager.attemp_build(pygame.mouse.get_pos(), "TURRET")