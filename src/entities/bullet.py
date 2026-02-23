import pygame
import math
from .Entity import Entity
from settings import Settings

class Bullet(Entity):
    def __init__(self, x, y, target_pos, owner=None, uid=None):
        # On utilise les dimensions des settings
        w, h = Settings.BULLET_SIZE, Settings.BULLET_SIZE // 3
        super().__init__(x, y, w, h, uid)
        
        self.owner = owner  # L'entité qui a tiré (Joueur, Tourelle, etc.)
        self.velocity = Settings.BULLET_VELOCITY
        self.damage = 7
        self.current_hp = self.damage # La balle "meurt" quand elle n'a plus de HP (pénétration)

        # Préparation du mouvement (sera reset dans spawn)
        self.velocity_vector = pygame.math.Vector2(0, 0)
        self.setup_movement(target_pos)

    def setup_movement(self, target_pos):
        ''' Calcule la direction et l'angle de l'image '''
        target = pygame.math.Vector2(target_pos)
        direction = target - self.pos
        
        if direction.length() > 0:
            direction.normalize_ip()
            self.velocity_vector = direction * self.velocity
            
            # Rotation de l'image pour qu'elle pointe vers la cible
            angle = math.degrees(math.atan2(-direction.y, direction.x))
            # On pourrait transformer self.image ici si c'est un sprite allongé
            
        # Visuel temporaire (un petit cercle rouge)
        self.image.fill((0,0,0,0)) # Transparent
        pygame.draw.circle(self.image, "Red", (self.rect.w//2, self.rect.h//2), 5)

    def spawn(self, x, y, target_pos, owner=None, uid=None):
        ''' Réinitialisation pour le Pooling '''
        super().spawn(x, y, uid)
        self.owner = owner
        self.current_hp = self.damage
        self.setup_movement(target_pos)

    def update(self, dt):
        if not self.active: return

        # Mouvement précis
        self.pos += self.velocity_vector * dt
        self.rect.center = self.pos

        # Suppression si sortie du MONDE (et pas seulement de l'écran)
        if not self.game.st.WORLD_RECT.colliderect(self.rect):
            self.kill()

    def on_hit(self, target_entity):
        ''' Appelée quand la balle touche une cible '''
        target_entity.take_damage(self.damage)
        
        # SI LA CIBLE MEURT : On prévient le propriétaire !
        if not target_entity.alive and self.owner:
            if hasattr(self.owner, "increment_kills"):
                self.owner.increment_kills()
        
        # La balle disparaît après l'impact (ou perd 1 HP pour la pénétration)
        self.kill()