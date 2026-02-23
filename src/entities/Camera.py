import pygame
from entities.Entity import Entity


class Camera(Entity):

    def __init__(self, screen_w: int, screen_h: int) -> None:
        super().__init__(0, 0, screen_w, screen_h, "camera", "main_camera")

        self.screen_center = pygame.math.Vector2(screen_w / 2, screen_h / 2)
        self.target_pos = None # L'entité à suivre (le joueur)
        self.smoothing = 0.1 # Vitesse de suivi (0.1 = 10% de la distance par frame)


    def follow(self, target_vector2: pygame.math.Vector2):
        # On viens recupere la position de notre sujet de scene
        self.target_pos = target_vector2


    def update(self, dt):
        if self.target_pos:
            # On veut que le centre de l'écran soit sur le centre du sujet (ex : joueur)
            # Calcul de la destination idéale
            dest = self.screen_center - self.target_pos

            # On déplace la caméra vers la destination (Lerp fluide)
            self.pos += (dest - self.pos) * self.smoothing

            # Synchronisation du Rect pour que get_absolute_rect() fonctionne
            self.rect.topleft = self.pos

        # On update les enfants (ennemis, etc.)
        super().update(dt)


    def draw(self, surface):
        '''
        Override de draw pour ajouter le Z-Sorting
        '''
        if not self.visible: return

        # --- LE Z-SORTING ---
        # On trie les enfants par leur coordonnée 'bottom' 
        # pour que ceux plus "bas" sur l'écran soient dessinés devant.
        sorted_children = sorted(self.children, key=lambda e: e.rect.bottom)

        child: "Entity"
        for child in sorted_children:
            child.draw(surface)