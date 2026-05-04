import pygame

from .UIButton import UIButton
from .UIPanel import UIPanel
from .UIProgressBar import UIProgressBar
from .UIText import UIText


class UIUpgradeBoard(UIPanel):
    """
    Panneau d'upgrade pour une stat.

    Affiche :
        - Nom de la stat (label)
        - Barre de progression  valeur_actuelle / max
        - Bouton d'achat avec prix
        - Taux d'augmentation par upgrade (+X%)

    Les états grisés sont gérés automatiquement :
        • MAXED   → bouton gris, inactif
        • BROKE   → bouton rouge, inactif  (pas assez d'argent)
        • OK      → bouton vert, actif
    """

    def __init__(self):
        super().__init__(0, 0, 0, 0)
        self.progress_bar: UIProgressBar = UIProgressBar(0, 0)
        self.visible = False
        self.active = False

        # État interne
        self._is_maxed = False
        self._can_afford = True
        self._curr_val_fn = lambda: 0
        self._price = 0
        self._max_val = 1
        self._rate = 0
        self._callback = None

    # ------------------------------------------------------------------
    # Setup principal
    # ------------------------------------------------------------------
    def setup(self, x: int, y: int, w: int, h: int, label: str) -> None:
        self.remove_all_child()

        self.rect.topleft = (x, y)
        self.rect.width = w
        self.rect.height = h
        self.image = self._SPRITE.get_ui_panel(w, h, (50, 50, 50))

        self.set_label(label, 50)
        self.label.rect.topleft = (20, 10)

    def set_progress_bar(self, max_val: float, curr_val_fn) -> None:
        """
        max_val    : plafond (valeur réelle, pas un %)
        curr_val_fn: fonction (getter) → valeur actuelle
        """
        self._max_val = max_val
        self._curr_val_fn = curr_val_fn

        self.progress_bar.custom_setup(
            20,
            self.label.rect.bottom + 20,
            self.rect.w - 40,
            30,
            curr_val_fn,
            max_val,
            label=None,
            color=(29, 171, 227),
        )
        self.add_child(self.progress_bar)

        # Texte "valeur_actuelle / max"
        self._val_text = UIText(
            self.rect.w - 20,
            self.label.rect.centery,
            lambda: f"{int(self._curr_val_fn())} / {int(self._max_val)}",
            size_text=30,
            align="midright",
            text_update=True,
            uid=f"{self.uid}_val_range",
        )
        self.add_child(self._val_text)

    def set_upgrade_button(self, callback, price: int, rate: int) -> None:
        """
        callback : fonction appelée si l'upgrade est possible
        price    : coût fixe de cet upgrade (int, lu depuis le JSON)
        rate     : taux % affiché (+X%)
        """
        self._callback = callback
        self._price = price
        self._rate = rate

        self._upgrade_btn = UIButton(
            20,
            self.progress_bar.rect.bottom + 20,
            str(price),
            self._on_click,
            border_radius=0,
            color=(72, 222, 105),
            uid=f"{self.uid}_btn",
        )

        self._rate_text = UIText(0, 0, f"+{rate}%")
        tx = self.rect.w - self._rate_text.rect.w - 20
        ty = self.rect.h - self._rate_text.rect.h - 20
        self._rate_text.rect.topleft = (tx, ty)

        self.add_child(self._upgrade_btn)
        self.add_child(self._rate_text)

        # Forcer un premier rafraîchissement visuel
        self._refresh_button_state()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        if not self.active:
            return
        super().update(dt)
        self._refresh_button_state()

    # ------------------------------------------------------------------
    # Interne
    # ------------------------------------------------------------------
    def _refresh_button_state(self) -> None:
        """Met à jour la couleur et l'état actif du bouton selon la situation."""
        if not hasattr(self, "_upgrade_btn"):
            return

        current_val = self._curr_val_fn()
        wallet_val = self._EVENTBUS.request("GET_WALLET_VAL")

        self._is_maxed = current_val >= self._max_val
        self._can_afford = (
            (wallet_val >= self._price) if wallet_val is not None else True
        )

        if self._is_maxed:
            self._upgrade_btn.set_text("MAXED")
            self._upgrade_btn.set_color((80, 80, 80))  # Gris
            self._upgrade_btn.active = False

        elif not self._can_afford:
            self._upgrade_btn.set_text(str(self._price))
            self._upgrade_btn.set_color((160, 50, 50))  # Rouge sombre
            self._upgrade_btn.active = False  # Bloqué (pas de clic)

        else:
            self._upgrade_btn.set_text(str(self._price))
            self._upgrade_btn.set_color((72, 222, 105))  # Vert
            self._upgrade_btn.active = True

    def _on_click(self) -> None:
        """Appelé par le bouton — vérifie les conditions avant d'appliquer."""
        if self._is_maxed:
            return

        if not self._can_afford:
            self._EVENTBUS.publish("PLAY_SFX", "ERROR")
            return

        if self._callback:
            self._callback()

        # Floating text feedback
        self._EVENTBUS.publish(
            "SHOW_FT",
            {
                "xy": self.get_screen_rect().topleft,
                "text": f"+{self._rate}%",
                "static": True,
            },
        )
