from typing import TYPE_CHECKING

from ui.element.UIButton import UIButton
from ui.element.UICompose import UICompose
from ui.element.UIPanel import UIPanel

if TYPE_CHECKING:
    from main import App


class ShopPanel(UIPanel):
    def __init__(self, game: "App"):
        self.game = game
        self.st = self.game.st
        self.building = self.st.BUILDINGS_LIST
        mid_pos = (self.st.SCREEN_HEIGHT - 800) / 2
        super().__init__(self.st.SCREEN_WIDTH, mid_pos, 250, 800)
        self.uid = "ShopPanel"
        self.open = False

        if self.uid:
            child_uid = f"{self.uid}_"
        else:
            child_uid = ""

        self.set_label("SHOP")
        self.set_animation(
            (self.st.SCREEN_WIDTH - 280, mid_pos), (self.st.SCREEN_WIDTH, mid_pos), 1000
        )

        # Souscription
        self.game.eventManager.subscribe("OPEN_SHOP", self.show)
        self.game.eventManager.subscribe("CLOSE_SHOP", self.kill)

        # 2. Création des Boutons DANS le panneau
        size = self.game.st.CELL_SIZE, self.game.st.CELL_SIZE

        for row, build in enumerate(self.building):
            data = self.st.get_build_data(build)
            sprite_id = data.get("sprite_id")
            sprite = self.game.spriteManager.get_sprite_resize(sprite_id, size)
            cost = data.get("cost", 100)
            action = lambda a=build: self.buy_building(a)

            element = UICompose(
                30,
                120 + (row * 230),
                200,
                200,
                build,
                sprite,
                action,
                f"{str(cost)} $",
                f"{child_uid}_{row}",
            )
            self.add_child(element)

    def buy_building(self, type: str) -> None:
        self.game.eventManager.publish("SELECT_BUILD", str(type))
        self.game.eventManager.publish("BUILD_MODE", True)

    def show(self):

        self.open = True
        super().show()

    def kill(self):

        self.open = False
        super().kill()
