import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class Enemie(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, size: tuple, game: "App", type:int=0):
        super().__init__()
        self.game = game
        self.type = type
        self.image = self.game.spriteManager.get_custom_sprite(self.game.st.ENEMIE_SPRITE, size, 'circle')
        self.rect = self.image.get_rect(center=(x,y))
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        self.director_vector = pygame.math.Vector2()
        self.velocity = 90
        self.max_hp = self.game.st.ENEMIE_HEALTH # * (WaveManager.wave_difficulty / 10) <<< risquer car on multiplie p-e par 0
        self.current_hp = self.max_hp
        self.health_bar = None
        self.size = size
        self.arrived = True
        self.target_pos = None


    def update(self, dt):
        
        if self.arrived:

            nx, ny = self.next_target()
        
            dx = ((nx * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2) - self.size[0] / 2
            dy = ((ny * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2) - self.size[1] / 2

            self.target_pos = pygame.math.Vector2(dx, dy)
            self.arrived = False
              
        self.director_vector = self.target_pos - self.pos
        length = self.director_vector.length()

        if length > 0:
            self.director_vector = self.director_vector.normalize()

        if length > 10:
            # mise a jour de la position du joueur
            self.pos += self.director_vector * self.velocity * dt
            self.rect.center = self.pos

        else:
            self.arrived = True

    def take_damage(self, amount):
        self.current_hp -= amount
        # si 0 HP alors -> mort
        if self.current_hp <= 0:
            self.die()


    def die(self):
        '''
            mort de l'enemis et ajout au event
        '''
        self.kill()
        self.game.eventManager.publish("ENEMY_KILLED", self.type)

        
    def next_target(self):

        cx, cy = self.game.grid.get_cell_pos(self.pos.x, self.pos.y)

        neighbors = self.game.grid.get_neighbors(cx, cy)
        next_cell = None
        cheapest_cell = float('inf')
        
        for n, cost in neighbors.items():
            if cost < cheapest_cell:
                cheapest_cell = cost
                next_cell = n

        return next_cell