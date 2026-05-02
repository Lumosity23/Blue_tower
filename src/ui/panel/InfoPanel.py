import json
from typing import TYPE_CHECKING

from ui.element import UIDot, UIIcon, UIProgressBar, UIStat
from ui.element.UIButton import UIButton
from ui.element.UIPanel import UIPanel
from utils.path import resource_path as rp

if TYPE_CHECKING:
    from element.UIElement import UIElement

    from entities.Entity import Entity
    from main import App


class InfoPanel(UIPanel):
    def __init__(self, game: "App"):

        self.game = game
        w, h = 400, game.st.SCREEN_HEIGHT - 40
        self.size = w, h

        # Dans ton UIManager ou InfoPanel
        with open(rp(self.game.st.UI_SCHEMA_PATH), "r") as f:
            self.schemas: dict[dict] = json.load(f)

        super().__init__(game.st.SCREEN_WIDTH, 20, w, h, uid="InfoPanel")

        self.set_label("INFO", 100)
        self.set_animation(
            (self.game.st.SCREEN_WIDTH - self.size[0] - 20, 20),
            (self.game.st.SCREEN_WIDTH, 20),
            1000,
        )
        self.visible = False

        action_up = lambda: self.game.eventManager.publish(
            "ELEMENT_UPGRADE", self.game.ui_manager.info.current_entity
        )

        self.upgrade_btn = UIButton(
            20,
            self.rect.h - 70,
            "UPGRADE",
            action_up,
            (255, 157, 0),
            border_radius=0,
            uid=f"{self.uid}_btn_upgrade",
        )
        self.sell_btn = UIButton(
            20,
            self.rect.h - (90 + self.upgrade_btn.rect.h),
            "SELL",
            self.sell_building,
            (107, 9, 9),
            border_radius=0,
            uid=f"{self.uid}_btn_sell",
        )

        for e in [self.upgrade_btn, self.sell_btn]:
            self.add_child(e)

        # Entity INFO
        self.current_entity: Entity = None
        self.ui_pool = {}
        self.active_children: list["UIElement"] = []
        self.amount_ui_elements: dict[str, list[int, "UIElement"]] = {
            "icon": [1, UIIcon.UIIcon],
            "bar": [5, UIProgressBar.UIProgressBar],
            "dot": [3, UIDot.UIDot],
            "stat": [4, UIStat.UIStat],
        }
        self.init_pool_child()

        # Souscription
        self.game.eventManager.subscribe("ELEMENT_SELECTED", self.show_element)
        self.game.eventManager.subscribe("ELEMENT_UNSELECTED", self.kill)

    def init_pool_child(self) -> None:
        for uielement, numAndClass in self.amount_ui_elements.items():
            num, cls = numAndClass
            self.ui_pool[uielement] = []
            for _ in range(num):
                element: "UIElement" = cls(0, 0)
                element.active = False
                self.ui_pool[uielement].append(element)

    def show_element(self, entity: "Entity") -> None:

        self.game.eventManager.publish("CLOSE_SHOP")
        self.make_data(entity)

        super().show()

    def reset_data_child(self) -> None:

        while self.active_children:
            child = self.active_children.pop(0)
            child.active = False
            self.remove_child(child)

    def sell_building(self) -> None:

        self._EVENTBUS.publish("EARN_MONEY", (self.current_entity.cost // 2))
        self.current_entity.kill()
        self.kill()

    def make_data(self, entity: "Entity") -> None:

        # Setup de notre nouvelle entite
        self.reset_data_child()
        self.current_entity = entity

        if (
            self.current_entity.type == "BUILDING"
            and self.current_entity.tag != "KERNEL"
        ):
            if self.sell_btn not in self.children:
                self.add_child(self.sell_btn)

        else:
            self.remove_child(self.sell_btn)

        if entity.tag in self.schemas:
            entity_schema = self.schemas.get(entity.tag)
        else:
            return

        # Variable de pos pour les different elements
        pos_x = 20  # constante le long de notre infoPanel
        pos_y = (
            self.label.rect.bottom + 70
        )  # valeur qui va augmenter au cours de la boucle de creation
        padding = 20

        for item in entity_schema:
            # Recupere un element correspondant encore non utiliser
            for e in self.ui_pool[item["type"]]:
                if not e.active:
                    element: "UIElement" = e
                    element.active = True
                    self.add_child(element)
                    self.active_children.append(element)

                    # Recuperation des info utile
                    label = item["label"]
                    map: dict = item["mapping"]

                    # Recupere les eventuelles pointers
                    def get_attribut(attr):
                        if attr is None:
                            return None
                        if hasattr(entity, attr):
                            return entity.__getattribute__(attr)
                        print(
                            f"aucun attribut du nom de {attr} n'as ete trouver sur {entity.__name__()}"
                        )

                    def get_attribut_pointer(attr):
                        if attr is None:
                            return lambda: (
                                None
                            )  # Retourne une fonction qui renvoie None

                        if hasattr(entity, attr):
                            # On retourne une fonction (un "getter")
                            return lambda name=attr: getattr(entity, name)

                        print(
                            f"aucun attribut du nom de {attr} sur {type(entity).__name__}"
                        )
                        return lambda: None

                    sprite = get_attribut(map.get("icon_id"))
                    value = get_attribut_pointer(map.get("string"))
                    max_val = get_attribut(map.get("max"))
                    current_val = get_attribut_pointer(map.get("current"))

                    # Activation de l'element
                    element.custom_setup(
                        x=pos_x,
                        y=pos_y,
                        w=self.rect.w - 40,
                        h=20,
                        label=label,
                        sprite=sprite,
                        color=map.get("color", (255, 255, 255)),
                        current_val=current_val,
                        max_val=max_val,
                        value=value,
                        mid_pos=self.rect.w // 2,
                    )
                    rect = element.get_size()
                    pos_y += rect.height + padding
                    # print(f" ma taille : {rect.h} et mon topleft = {rect.topleft} -> la soustraction des deux dois faire mon topleft = {element.rect.h - pos_y}")
                    break
