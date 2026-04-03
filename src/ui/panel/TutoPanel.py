from ui.UIPanel import UIPanel
from ui.UIButton import UIButton
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class TutoPanel(UIPanel):
    
    def __init__(self, game: "App") -> None:
        super().__init__(0,0,game.st.SCREEN_WIDTH, game.st.SCREEN_HEIGHT, uid="TUTO_PANEL")
        self.game = game

        

