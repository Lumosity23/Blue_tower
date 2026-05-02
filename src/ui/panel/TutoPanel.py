from typing import TYPE_CHECKING

from ui.element.UIButton import UIButton
from ui.element.UIPanel import UIPanel

if TYPE_CHECKING:
    from main import App


class TutoPanel(UIPanel):
    def __init__(self, game: "App") -> None:
        super().__init__(
            0, 0, game.st.SCREEN_WIDTH, game.st.SCREEN_HEIGHT, uid="TUTO_PANEL"
        )
        self.game = game

        self.btn_next = UIButton()
