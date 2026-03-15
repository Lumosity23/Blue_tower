from .UIElement import UIElement
from .UIText import UIText


class UIStat(UIElement):

    def __init__(self, x, y, uid=None):
        super().__init__(x, y, 0, 0, uid)
        self.type = "stat"


    def setup(self, label) -> None:
        ''' Init la stat avec le label '''
        self.stat_label = UIText( self.x, self.y, f"{label} : " )
        
        w = self.stat_label.rect.w
        h = self.stat_label.rect.h

        
        self.add_child(self.stat_label)


    def set_value(self, value) -> None:
        ''' Permet de setup un valeur a surveiller ( dois etre un pointeur )'''
        self.stat_value = UIText( self.rect.x + self.stat_label.rect.width, self.rect.y , value , text_update=True)
        self.add_child(self.stat_value)
