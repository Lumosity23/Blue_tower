import pygame
from .Building import Building
from ..bullet import Bullet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class Turret(Building):

    def __init__(self, x: int, y: int, data: dict, game: "App", uid):
        super().__init__(x, y, data, game, tag="TURRET", uid=uid)

        self.last_shoot = pygame.time.get_ticks()

    
    def update(self, dt):

        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot > self.cooldown and not self.game.sceneManager.waveManager.end_wave:
            target = self.game.sceneManager.waveManager.nearest_enemy(self.rect.center)
            #target.pos: pygame.math.Vector2
            if target:
                if target.pos.distance_to(self.pos) <= self.range:
                    self.shoot(target.rect.center)
                    self.last_shoot = current_time
        
    
    def shoot(self, target: tuple):
        self.game.sceneManager.entityManager.spawn(Bullet, self.rect.centerx, self.rect.centery, uid=f"{self.uid}_Bullet", target_pos=target, owner=self, bullet_damage=self.damage)


Turret.ui_config(
    ("BAR",  "Vie", "current_hp", "max_hp"),
    ("TEXT", "Dégâts", "damage")
)