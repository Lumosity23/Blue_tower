from ui.UIPanel import UIPanel
from ui.UIButton import UIButton
from ui.UIProgressBar import UIProgressBar
from ui.UIText import UIText


class UIUpgradeBoard(UIPanel):

    def __init__(self):
        
        super().__init__(0, 0, 0, 0)
        self.progress_bar = UIProgressBar(0 ,0)
        self.visible = False
        self.active = False


    def setup(self, x, y, w, h, label) -> None:

        self.remove_all_child()
        # le nom du cadre
        self.rect.topleft = x, y
        self.rect.width, self.rect.height = w, h
        self.image = self._SPRITE.get_ui_panel(self.rect.w, self.rect.h, (50,50,50))

        self.set_label(label, 50)
        self.label.rect.topleft = 20, 10


    def set_progress_bar(self, max_val, curr_val) -> None:
        
        self.max_val = max_val

        self.progress_bar.custom_setup(20, self.label.rect.bottom + 20, self.rect.w - 40, 30, curr_val, max_val, label=None, color=(29, 171, 227))
        self.add_child(self.progress_bar)


    def set_upgrade_button(self, callBack, price: int, rate: int) -> None:
        
        self.rate = rate
        self.price = price
        self.callBack = callBack

        self.upgrade_btn = UIButton(20, self.progress_bar.rect.bottom + 20, str(price), self.upgrade, border_radius=0, color=(72, 222, 105)) 
        self.rate_text = UIText(0, 0, f"+{rate}%")
        pos_text_x = self.rect.w - self.rate_text.rect.w - 20
        pos_text_y = self.rect.h - self.rate_text.rect.h - 20
        self.rate_text.rect.topleft = pos_text_x, pos_text_y

        for e in [self.upgrade_btn, self.rate_text]:
            self.add_child(e)
    

    def upgrade(self) -> None:

        self.callBack()

        mapping = {
            "xy" : self.get_screen_rect().topleft, # .center
            "text" : f"+{self.rate * self.max_val}",
            "static" : True
        }

        self._EVENTBUS.publish("SHOW_FT", mapping)