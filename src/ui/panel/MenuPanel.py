from ui.UIPanel import UIPanel
from ui.UIButton import UIButton
from ui.UIText import UIText
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class MenuPanel(UIPanel):

    def __init__(self, game: "App", uid = None):
        super().__init__(-50, -50, game.st.SCREEN_WIDTH + 100, game.st.SCREEN_HEIGHT + 100, (45, 45, 45), uid)
        self.game = game
        self.st = game.st
        self.visible = False
        self.set_label("Blue Tower", 200)
        self.uid = "MenuPanel"
        if self.uid:
            child_uid = f"{self.uid}_"
        else:
            child_uid = ""

        btn_resume = UIButton(100, 100, "PLAY", self.play, (100, 100, 100), size_text=70, uid=f"{child_uid}btn_resume")
        btn_restart = UIButton(100, 100, "SETTINGS", self.open_settings, (255,0,0),size_text=70, uid=f"{child_uid}btn_restart")
        btn_quit = UIButton(100, 100, "QUIT", self.quit, (255,0,0),size_text=70, uid=f"{child_uid}btn_quit")

        self.add_child(btn_quit)
        self.add_child(btn_restart)
        self.add_child(btn_resume)


    def open_settings(self) -> None:

        self.game.eventManager.publish("OPEN_SETTINGS")
        return

    def quit(self) -> None:

        self.game.eventManager.publish("QUIT")
        return

    def play(self) -> None:

        self.game.eventManager.publish("NEW_GAME")
        return