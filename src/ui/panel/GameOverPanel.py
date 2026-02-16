from ui.UIPanel import UIPanel
from ui.UIButton import UIButton
from ui.UIText import UIText
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class GameOverPanel(UIPanel):

    def __init__(self, game: "App", uid = None):
        super().__init__(50, 50, game.st.SCREEN_WIDTH - 100, game.st.SCREEN_HEIGHT - 100, (45, 45, 45), uid)
        self.game = game
        self.st = game.st
        self.visible = False

        text = UIText(self.st.SCREEN_WIDTH / 2, 100, "GAME OVER !", 100, align='center')
        btn_restart = UIButton(self.st.SCREEN_WIDTH / 2, self.st.SCREEN_HEIGHT / 2, 150, 70, "RESTART", self.restart_game, (255,0,0))
        btn_quit = UIButton(self.st.SCREEN_WIDTH / 2, self.st.SCREEN_HEIGHT / 2 + 100, 150, 70, "QUIT", self.quit, (255,0,0))

        self.add_child(btn_quit)
        self.add_child(btn_restart)
        self.add_child(text)


    def restart_game(self) -> None:

        self.game.eventManager.publish("RESTART_GAME")
        return

    def quit(self) -> None:

        self.game.eventManager.publish("QUIT")
        return