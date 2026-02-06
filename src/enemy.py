from settings import Settings
from sprite_custom import get_custom_sprite
from grid import Grid
import pygame


class Enemie(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, size: tuple):
        super().__init__()
        self.image = get_custom_sprite(Settings.ENEMIE_SPRITE, size, 'circle')
        # self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(center=(x,y))
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        self.director_vector = pygame.math.Vector2()
        self.velocity = 90
        self.max_hp = Settings.ENEMIE_HEALTH # * (WaveManager.wave_difficulty / 10) <<< risquer car on multiplie p-e par 0
        self.current_hp = self.max_hp
        self.health_bar = None
        self.size = size
        self.arrived = True
        self.target_pos = None


    def update(self, dt, walls, grid: Grid, player,enemis,all_sprites):
        
        if self.arrived:

            nx, ny = self.next_target(grid)
        
            dx = ((nx * Settings.CELL_SIZE) + Settings.CELL_SIZE / 2) - self.size[0] / 2
            dy = ((ny * Settings.CELL_SIZE) + Settings.CELL_SIZE / 2) - self.size[1] / 2

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
            self.kill()


    def next_target(self, grid: Grid):

        cx, cy = grid.get_cell_pos(self.pos.x, self.pos.y)

        neighbors = grid.get_neighbors(cx, cy)
        next_cell = None
        cheapest_cell = float('inf')
        
        for n, cost in neighbors.items():
            if cost < cheapest_cell:
                cheapest_cell = cost
                next_cell = n

        return next_cell