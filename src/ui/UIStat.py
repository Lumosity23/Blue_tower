from .UIText import UIText


class UIStat(UIText):

    def __init__(self, x, y, uid=None):
        super().__init__(x, y, "stat", uid=uid)
        self.type = "stat"


    def setup(self, label, size=50) -> None:
        ''' Init la stat avec le label '''
        self.set_text(f"{label} : ", size=size)


    def set_value(self, value, color) -> None:
        ''' Permet de setup un valeur a surveiller ( dois etre un pointeur )'''
        self.value = value
        self.stat_value = UIText(0, 0 , value , size_text=self.text_size, color=color, text_update=True)
        self.stat_value.rect.left = self.rect.right - 20
        self.add_child(self.stat_value)


    def custom_setup(self, x, y ,label, value, text_size=50, color=(255,255,255), **kwargs) -> None:

        self.remove_all_child()
        self.text_size = text_size
        self.setup(label)
        self.rect.topleft = x, y
        self.set_value(value, color)