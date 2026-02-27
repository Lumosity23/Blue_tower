import pygame
from entities.Entity import Entity


class Camera:

    def __init__(self, screen_w: int, screen_h: int) -> None:
        
        # Systeme de position pour la camera
        self.rect = pygame.Rect(0, 0, screen_w, screen_h)
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.offset = pygame.math.Vector2()

        self.entities_to_show: set[Entity] = set()
        self.screen_center = pygame.math.Vector2(screen_w / 2, screen_h / 2)
        self.target = None # L'entité à suivre (le joueur)
        self.smoothing = 0.1 # Vitesse de suivi (0.1 = 10% de la distance par frame)
        self.speed = 5.0


    def follow(self, target_entity: Entity):
        # On viens recupere la position de notre sujet de scene
        self.target = target_entity


    def add_entity(self, entity: Entity):
        self.entities_to_show.add(entity)
        for child in entity.children:
            self.add_entity(child)
    

    def remove_entity(self, entity: Entity):
        self.entities_to_show.discard(entity)
        for child in entity.children:
            self.remove_entity(child)


    def update(self, dt):
        if not self.target or not self.target.active: 
            return

        # On récupère le centre absolu du rect de l'entité
        target_center = pygame.math.Vector2(self.target.get_screen_rect().center)

        ideal_offset = target_center - self.screen_center
        self.offset += (ideal_offset - self.offset) * (self.speed * dt)


    def draw(self, surface: pygame.Surface):
        
        sorted_entities = sorted(
            self.entities_to_show, 
            key=lambda e: e.get_screen_rect().bottom
        )

        # 2. Rendu
        fast_blit = surface.blit
        for e in sorted_entities:
            # Si pour la logic l'entite est invisible alors on ne dessine pas
            if not e.visible:
                continue

            if hasattr(e, 'custom_draw'):
                # On passe la surface ET l'offset à l'entité !
                e.custom_draw(surface, self.offset)

            else:
                # --- Ancien comportement standard ---
                rect = e.get_screen_rect()
                pos_on_screen = (rect.x - self.offset.x, rect.y - self.offset.y)
                fast_blit(e.image, pos_on_screen)