import pygame
from .Building import Building
from ..bullet import Bullet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class Turret(Building):

    def __init__(self, x: int, y: int, data: dict, game: "App", uid):
        super().__init__(x, y, data, game,tag="TURRET", uid=uid)

        self.stats = self.game.st.BUILDINGS_DATA["TURRET"]
        self.image = self.game.spriteManager.get_custom_sprite(self.stats['sprite_id'])
        self.source_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_hp = self.stats['hp']
        self.current_hp = self.max_hp
        self.cost = self.stats['cost']
        self.damage = self.stats['damage']
        self.kills = 0
        self.last_shoot = pygame.time.get_ticks()
        self.cooldown = self.stats['cooldown']

    
    def update(self, dt):

        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot > self.cooldown and not self.game.sceneManager.waveManager.end_wave:
            target = self.game.sceneManager.waveManager.nearest_enemy(self.rect.center)
            if target:
                self.shoot(target.rect.center)
                self.last_shoot = current_time
    
    
    def shoot(self, target: tuple):
        self.game.sceneManager.entityManager.spawn(Bullet, self.rect.centerx, self.rect.centery, uid=f"{self.uid}_Bullet", target_pos=target, owner=self, bullet_damage=self.damage)