from ui.UIElement import UIElement
import pygame


class UIRange(UIElement):

    def __init__(self, x: int, y: int, range: int, uid = None):
        
        self.range = range
        self.pos = x, y

        w, h = self.range * 2, self.range * 2

        super().__init__(x, y, w, h, uid)


    def custom_draw(self, surface: pygame.Surface, cam_offset: pygame.math.Vector2):
        """ Appelé UNIQUEMENT par la Caméra (OFFSET APPLIQUÉ) """
        if not self.visible: return
        
        # ATTENTION : get_screen_rect() de Entity renvoie la pos absolue du MONDE ! 
        # (Le nom de la méthode est un peu trompeur, on devrait l'appeler get_world_rect)
        world_rect = self.get_screen_rect()
        
        # World -> Screen (On SOUSTRAIT l'offset pour dessiner manuellement)
        screen_x = world_rect.x - cam_offset.x
        screen_y = world_rect.y - cam_offset.y
        r = self.range

        self.range_circle_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(self.range_circle_surface, (200, 200, 200, 80), (r, r), r, 2)
        
        range_pos = (screen_x + (self.rect.w//2) - r, screen_y + (self.rect.h//2) - r)
        surface.blit(self.range_circle_surface, range_pos)  
    