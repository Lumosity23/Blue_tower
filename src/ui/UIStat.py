from .UIText import UIText


class UIStat(UIText):

    def __init__(self, x, y, uid=None):
        super().__init__(x, y, "stat", uid=uid)
        self.type = "stat"


    def setup(self, label) -> None:
        ''' Init la stat avec le label '''
        self.set_text(f"{label} : ")


    def set_value(self, value) -> None:
        ''' Permet de setup un valeur a surveiller ( dois etre un pointeur )'''
        self.value = value
        stat_value = UIText(0, 0 , value , text_update=True)
        stat_value.rect.left = self.rect.right - 20
        self.add_child(stat_value)


    def custom_setup(self, x, y ,label, value, **kwargs) -> None:

        self.remove_all_child()
        self.setup(label)
        self.rect.topleft = x, y
        self.set_value(value)