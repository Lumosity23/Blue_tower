import pygame
from UIElement import UIElement


class UIDot(UIElement):

    def __init__(self, x, y, radius, color, uid = None):
        # Creation du point simple
        w, h = radius * 2, radius * 2
        super().__init__(x, y, w, h, uid)
    
        self.radius = radius
        self.color = color
        self.state = None
        self.state_color = None

        pygame.draw.circle( self.image, self.color, (self.rect.center), self.radius )


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
        

        
