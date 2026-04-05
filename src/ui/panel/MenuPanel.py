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

        btn_play = UIButton(100, 100, "PLAY", self.play, (100, 100, 100), size_text=70, uid=f"{child_uid}btn_play")
        btn_play.set_sound("PLAY")
        
        btn_setting = UIButton(100, 100, "SETTINGS", self.open_settings, (255,0,0),size_text=70, uid=f"{child_uid}btn_restart")
        btn_quit = UIButton(100, 100, "QUIT", self.quit, (255,0,0),size_text=70, uid=f"{child_uid}btn_quit")

        text_how_to_play = "HOW TO PLAY : use arrows/WASD to move around and G for open/close the shop..."
        text_more_info = "for more information --> README of the repo on github : "
        text_address = "https://github.com/Lumosity23/Blue_tower.git"
        self.text = UIText(20, 400, text_how_to_play, uid="MENU_text_how_to_play", size_text=40)
        self.info = UIText(20, 400, text_more_info, uid="MENU_text_more_info", size_text=40)
        self.adress = UIText(20, 400, text_address, uid="MENU_text_adress", size_text=30)
        
        """ self.text.rect.bottomleft = 70, self.rect.h - 70
        self.info.rect.bottomleft = 70, self.rect.h - 70
        self.adress.rect.bottomleft = 70, self.rect.h - 70 """

        self.add_child(self.info)
        self.add_child(self.adress)
        self.add_child(self.text)
        self.add_child(btn_quit)
        self.add_child(btn_setting)
        self.add_child(btn_play)


    def open_settings(self) -> None:

        self.game.eventManager.publish("OPEN_SETTINGS", "MENU")
        return

    def quit(self) -> None:

        self.game.eventManager.publish("QUIT")
        return

    def play(self) -> None:

        self.game.eventManager.publish("NEW_GAME")
        return