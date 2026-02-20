import pygame
from .bullet import Bullet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App
    

    
class Kernel(pygame.sprite.Sprite):

    def __init__(self, game: "App"):
        super().__init__()
        self.game = game
        self.size = (game.st.KERNEL_SIZE, game.st.KERNEL_SIZE)
        self.image = self.game.spriteManager.get_custom_sprite(game.st.KERNEL, self.size, 'circle')
        self.rect = self.image.get_rect(center=(game.st.SCREEN_WIDTH / 2, game.st.SCREEN_HEIGHT / 2))
        self.pos = self.rect.x, self.rect.y
        self.max_hp = game.st.KERNEL_HP
        self.current_hp = self.max_hp
        self.last_shoot = pygame.time.get_ticks()
        self.cooldown = self.game.st.TURRET_COOLDOWN
        self.alive = True

        # Declaration des Subscribe
        self.game.eventManager.subscribe("NEW_GAME", self.reset)

    def update(self, dt):

        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot > self.cooldown and not self.game.wave_manager.end_wave:
            target = self.game.wave_manager.nearest_enemy(self.rect.center)
            if target:
                self.shoot(target.rect.center)
                self.last_shoot = current_time

    def take_damage(self, damage: int) -> None:
        self.current_hp -= damage
        # si 0 HP alors -> mort
        if self.current_hp <= 0:
            self.alive = False


    def reset(self):
        self.current_hp = self.max_hp
        self.damage = self.current_hp
        self.alive = True

    
    def shoot(self, target: tuple) -> None:
        # Creation d'un projectile si clic de souris
        bullet = Bullet(self.rect.centerx, self.rect.centery, target_pos=target)
        self.game.bullets.add(bullet)
        self.game.all_sprites.add(bullet)

