from .UIElement import UIElement
from .UIText import UIText


class UIStat(UIElement):

    def __init__(self, x, y, uid=None):
        super().__init__(x, y, 0, 0, uid)
        self.type = "stat"


    def setup(self, label) -> None:
        ''' Init la stat avec le label '''
        self.stat_label = UIText( 0, 0, f"{label} : " )

        
        self.add_child(self.stat_label)


    def set_value(self, value) -> None:
        ''' Permet de setup un valeur a surveiller ( dois etre un pointeur de fonction qui retourne un str 'la dite value' )'''
        self.value = value
        self.stat_value = UIText(self.stat_label.rect.width, 0 , self._get_value , text_update=True)
        self.add_child(self.stat_value)


    def _get_value(self):
        return str(self.value)


    def custom_setup(self, x, y ,label, value, **kwargs) -> None:

        self.remove_all_child()

        self.rect.topleft = x, y
        self.setup(label)
        self.set_value(value)