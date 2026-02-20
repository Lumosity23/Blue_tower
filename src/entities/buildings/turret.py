import pygame
from .Building import Building
from ..bullet import Bullet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class Turret(Building):

    def __init__(self, x: int, y: int, game: "App"):
        super().__init__(x, y, game)

        self.st = self.game.st
        self.type = self.game.st.TURRET
        self.image = self.game.spriteManager.get_custom_sprite(self.st.TURRET, (self.st.CELL_SIZE, self.st.CELL_SIZE))
        self.source_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_hp = self.st.TURRET_HP
        self.current_hp = self.max_hp
        self.cost = self.st.TYPE_COST[self.type]
        self.last_shoot = pygame.time.get_ticks()
        self.cooldown = self.st.TURRET_COOLDOWN

    
    def update(self, dt):

        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot > self.cooldown and not self.game.wave_manager.end_wave:
            target = self.game.wave_manager.nearest_enemy(self.rect.center)
            if target:
                self.shoot(target.rect.center)
                self.last_shoot = current_time
    
    
    def shoot(self, target: tuple):

        bullet = Bullet(self.rect.centerx, self.rect.centery, target_pos=target)
        self.game.bullets.add(bullet)
        self.game.all_sprites.add(bullet)
    