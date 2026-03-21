import pygame
from .UIElement import UIElement
from .UIText import UIText


class UIDot(UIElement):

    def __init__(self, x, y, uid = None):
        super().__init__(x, y, 0, 0, uid)
        self.type = "dot"


    def setup(self, radius: int, color ) -> None:
        self.rect.w, self.rect.h = radius * 2, radius * 2
    
        self.radius = radius
        self.color = color
        self.state = None
        self.state_color = None

        pygame.draw.circle( self.image, self.color, (self.rect.center), self.radius )


    def custom_setup(self, x, y, label, color, **kwargs) -> None:

        self.remove_all_child()

        self.setup(5, color)
        self.rect.topleft = x, y

        self.label = UIText(0, 0, label)
        self.label.rect.midleft = self.rect.midleft
        self.label.rect.x += self.radius * 2 + 5
        self.add_child(self.label)


    def set_state(self, dict_states: dict[str, tuple[int, int, int]], pt_state ) -> None:
        ''' Setup un tableau de state -> couleur depuis un dict passer en argument\n
            pt_state: pointeur vers la variable d'etat
        '''
        self.state = pt_state
        self.state_color = dict_states

            
    def update(self, dt):
        
        if not self.state:
            return super().update(dt)
        
        # Update la couleur
        self.color = self.state_color[self.state]

        # Redessine le cecle
        pygame.draw.circle(self.image, self.color, (self.rect.center), self.radius )

        super().update(dt)
        

        
