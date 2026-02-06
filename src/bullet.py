import pygame
import math
from grid import Grid
from settings import Settings


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.size = (Settings.BULLET_SIZE, 1/3 * Settings.BULLET_SIZE)
        self.image = pygame.Surface(self.size)
        self.color = self.image.fill(('Yellow'))
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = Settings.BULLET_VELOCITY
        mx, my = pygame.mouse.get_pos()
        target_pos = pygame.math.Vector2(mx, my)
        
        self.direction_vector = target_pos - self.pos
        if self.direction_vector.length() > 0:
            self.direction_vector = self.direction_vector.normalize()
            
        self.velocity_vector = self.direction_vector * self.velocity
        self.angle = math.degrees(math.atan2(-self.direction_vector.y, self.direction_vector.x))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        self.damage = 7
        self.current_hp = self.damage
    

    def update(self, dt, walls: list[object], grid: Grid, player, enemis, all_sprites): # on met Walls car pas enccore de *args
        # Mouvement
        self.pos += self.velocity_vector * dt
        self.rect.center = self.pos

        # Verifier si toujours visible
        self.isOutside()


    def isOutside(self): # SUPPRESION SI EN DEHORS DE L'ECRAN
        # Gaucher
        if self.rect.left > Settings.SCREEN_WIDTH or \
           self.rect.right < 0 or \
           self.rect.top > Settings.SCREEN_HEIGHT or \
           self.rect.bottom < 0:
            self.kill()
            # print("Bullet deleted") # Décommenter pour debug uniquement
    

    def take_damage(self, amount):
        self.current_hp -= amount
        # si 0 HP alors -> mort
        if self.current_hp <= 0:
            self.kill()
