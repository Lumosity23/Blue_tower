import pygame
from ui.UIPanel import UIPanel
from ui.UIButton import UIButton
from ui.UICompose import UICompose
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class ShopPanel(UIPanel):

    def __init__(self, game: "App"):
        self.game = game
        self.st = self.game.st
        super().__init__(self.st.SCREEN_WIDTH - 530, 90, 490, 800)
        self.uid = "ShopPanel"
        self.visible = False

        if self.uid:
            child_uid = f"{self.uid}_"
        else:
            child_uid = ""

        self.set_label("SHOP")

        # 2. Création des Boutons DANS le panneau
        sprite_id = self.game.st.BUILDINGS_DATA["TURRET"]["sprite_id"]
        
        size = self.game.st.CELL_SIZE, self.game.st.CELL_SIZE
        for col in range(2):
            for row in range(3):
                if (col + row) % 2 == 0:
                    action = self.buy_turret
                    sprite_id = self.game.st.BUILDINGS_DATA["TURRET"]["sprite_id"]
                    cost = self.game.st.BUILDINGS_DATA["TURRET"]["cost"]
                else:
                    action = self.buy_wall
                    sprite_id = self.game.st.BUILDINGS_DATA["WALL"]["sprite_id"]
                    cost = self.game.st.BUILDINGS_DATA["WALL"]["cost"]

                element = UICompose(30 + (col * 230), 160 + (row * 230), 200, 200, "test",
                                     self.game.spriteManager.get_sprite_resize(sprite_id, size),
                                       action,
                                         f"{str(cost)} $", f"{child_uid}{col}{row}" )
                self.add_child(element)


    def buy_wall(self):
        self.game.eventManager.publish("SELECT_BUILD", "WALL")

    def buy_turret(self):
        self.game.eventManager.publish("SELECT_BUILD", "TURRET")