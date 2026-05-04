import json
from typing import TYPE_CHECKING

from ui.element.UIButton import UIButton
from ui.element.UIPanel import UIPanel
from ui.element.UIScroll import UIScroll  # ← nouveau
from ui.element.UIUpgradeBoard import UIUpgradeBoard
from utils.path import resource_path as rp

if TYPE_CHECKING:
    from entities.Entity import Entity
    from main import App


# Hauteur fixe d'un UIUpgradeBoard + espacement entre deux cartes
_BOARD_H = 220
_BOARD_PAD = 20


class UpgradePanel(UIPanel):
    """
    Panneau latéral affiché quand on clique sur "Upgrade" d'une entité.

    • Lit le schéma depuis le JSON généré par upgrade_config.py
    • Construit dynamiquement autant de UIUpgradeBoard que nécessaire
    • Les cartes sont placées dans un UIScroll → nombre illimité d'upgrades
    • Chaque carte grise automatiquement le bouton si :
          - la stat est au maximum (valeur réelle atteinte)
          - le joueur n'a pas assez d'argent
    """

    def __init__(self, game: "App"):
        self.game = game
        w = 400
        h = game.st.SCREEN_HEIGHT - 40

        # Chargement du schéma JSON (généré au lancement via upgrade_config)
        with open(rp(game.st.UPGRADE_SCHEMA_PATH), "r", encoding="utf-8") as f:
            self._schemas: dict = json.load(f)

        super().__init__(game.st.SCREEN_WIDTH - 20, 20, w, h, uid="UpgradePanel")

        self.set_label("Upgrades", 100)
        self.set_animation(
            (game.st.SCREEN_WIDTH - w - 20, 20),
            (game.st.SCREEN_WIDTH, 20),
            1000,
        )
        self.visible = False

        # Bouton fermeture
        self._back_btn = UIButton(
            w - 40,
            10,
            "X",
            lambda: self.kill(back=True),
            (50, 50, 50),
            uid=f"{self.uid}_btn_back",
        )
        self.add_child(self._back_btn)

        # Zone scrollable — placée sous le titre
        scroll_top = self.label.rect.bottom + 70
        scroll_h = h - scroll_top - 10

        self._scroll = UIScroll(
            x=10,
            y=scroll_top,
            w=w - 20,
            h=scroll_h,
            uid=f"{self.uid}_scroll",
        )
        self.add_child(self._scroll)

        # État courant
        self._current_entity: "Entity | None" = None
        self._boards: list[UIUpgradeBoard] = []

        # Abonnements
        game.eventManager.subscribe("ELEMENT_UPGRADE", self.show_element)
        game.eventManager.subscribe("ELEMENT_UNUPGRADE", self.kill)

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------
    def show_element(self, entity: "Entity") -> None:
        self.game.eventManager.publish("ELEMENT_UNSELECTED")
        self._current_entity = entity
        self._build_boards(entity)
        super().show()

    def kill(self, back: bool = False) -> None:
        if not self.visible:
            return
        if back and self._current_entity is not None:
            self._EVENTBUS.publish("ELEMENT_SELECTED", self._current_entity)
        super().kill()

    # ------------------------------------------------------------------
    # Construction des cartes d'upgrade
    # ------------------------------------------------------------------
    def _clear_boards(self) -> None:
        """Désactive et retire toutes les cartes précédentes."""
        for board in self._boards:
            board.active = False
            board.visible = False
            self._scroll.remove_child(board)
        self._boards.clear()

    def _build_boards(self, entity: "Entity") -> None:
        self._clear_boards()

        entity_tag = entity.tag
        if entity_tag not in self._schemas:
            # Aucun upgrade déclaré pour cette entité
            return

        upgrades = self._schemas[entity_tag]  # liste de dicts
        pos_y = 0  # position Y relative dans le scroll

        board_w = self._scroll.rect.w - 20  # marge intérieure du scroll

        for upgrade in upgrades:
            label = upgrade["label"]
            attr = upgrade["attr"]
            max_val = upgrade["max"]
            price = upgrade["price"]
            rate = upgrade["rate"]

            # Getter live sur l'entité
            def make_getter(a=attr):
                return lambda: getattr(entity, a, 0)

            curr_val_fn = make_getter()

            # Callback d'upgrade
            def make_callback(e=entity, a=attr, r=rate, p=price):
                return lambda: self._apply_upgrade(e, a, r, p)

            board = UIUpgradeBoard()
            board.active = True
            board.visible = True

            board.setup(0, pos_y, board_w, _BOARD_H, label)
            board.set_progress_bar(max_val, curr_val_fn)
            board.set_upgrade_button(make_callback(), price, rate)

            self._scroll.add_child(
                board
            )  # update_content_size() appelé automatiquement
            self._boards.append(board)

            pos_y += _BOARD_H + _BOARD_PAD

        # Remettre le scroll en haut à chaque nouvelle entité
        self._scroll.scroll_offset.y = 0
        self._scroll.target_scroll_offset.y = 0

    # ------------------------------------------------------------------
    # Application d'un upgrade
    # ------------------------------------------------------------------
    def _apply_upgrade(
        self,
        entity: "Entity",
        attr_name: str,
        rate: int,
        price: int,
    ) -> None:
        """
        1. Vérifie le portefeuille
        2. Calcule la nouvelle valeur (+rate %)
        3. Plafonne à max (lu depuis le schéma)
        4. Applique sur l'entité
        """
        if not self.game.walletManager.buy(price):
            self._EVENTBUS.publish("PLAY_SFX", "ERROR")
            return

        # Plafond depuis le schéma JSON
        entity_schema = self._schemas.get(entity.tag, [])
        max_val = next(
            (u["max"] for u in entity_schema if u["attr"] == attr_name),
            None,
        )

        current_val = getattr(entity, attr_name)
        new_val = round(current_val * (1 + rate / 100))

        if max_val is not None:
            new_val = min(new_val, max_val)

        setattr(entity, attr_name, new_val)
        # self._EVENTBUS.publish("PLAY_SFX", "UPGRADE_SUCCESS")
