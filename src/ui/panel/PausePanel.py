from ui.UIPanel import UIPanel
from ui.UIButton import UIButton
from ui.UIText import UIText
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class PausePanel(UIPanel):

    def __init__(self, game: "App", uid = None):
        super().__init__(-50, -50, game.st.SCREEN_WIDTH + 100, game.st.SCREEN_HEIGHT + 100, (45, 45, 45), uid)
        self.game = game
        self.st = game.st
        self.visible = False
        self.image.set_alpha(230)
        self.uid = "PausePanel"
        if self.uid:
            child_uid = f"{self.uid}_"
        else:
            child_uid = ""

        text = UIText(self.rect.w // 2, 40, "PAUSE", 100, uid=f"{child_uid}title_PAUSE")
        btn_resume = UIButton(100, 100, "RESUME", self.resume, (100, 100, 100), uid=f"{child_uid}btn_resume")
        btn_restart = UIButton(100, 100, "RESTART", self.restart_game, (255,0,0), uid=f"{child_uid}btn_restart")
        btn_quit = UIButton(100, 100, "QUIT", self.quit, (255,0,0), uid=f"{child_uid}btn_quit")

        self.add_child(btn_quit)
        self.add_child(btn_restart)
        self.add_child(btn_resume)
        self.add_child(text)


    def restart_game(self) -> None:

        self.game.eventManager.publish("RESTART_GAME")
        return

    def quit(self) -> None:

        self.game.eventManager.publish("QUIT")
        return

    def resume(self) -> None:

        self.game.eventManager.publish("PAUSE")
        return