import pygame
from .bullet import Bullet
from ui.UIProgressBar import UIProgressBar
from entities.Entity import Entity # Import de la nouvelle base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class Kernel(Entity):
    def __init__(self, game: "App"):
        # 1. Initialisation de la base Entity
        # On le place au centre du monde
        self.game = game
        
        self.stats = self.game.st.KERNEL_STATS
        w, h = self.stats['size']

        spawn_x = (game.st.WORLD_WIDTH / 2) - (w / 2)
        spawn_y = (game.st.WORLD_HEIGHT / 2) - (h / 2)
        
        super().__init__(spawn_x, spawn_y, w, h, tag="KERNEL", uid="KERNEL")
        
        # Setup visuel
        self.image = self.game.spriteManager.get_custom_sprite(game.st.KERNEL, (w, h), 'circle')
        
        # Stats
        self.max_hp = self.stats["hp"]
        self.current_hp = self.max_hp
        self.kills = 0
        self.last_shoot = pygame.time.get_ticks()
        self.cooldown = self.stats["cooldown"]
        self.alive = True

        # Souscription
        self.game.eventManager.subscribe("NEW_GAME", self.reset)


    def update(self, dt):
        if not self.active: return

        # Logique de tir
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot > self.cooldown and not self.game.wave_manager.end_wave:
            # On utilise le centre du Kernel pour chercher l'ennemi
            target = self.game.wave_manager.nearest_enemy(self.rect.center)
            if target:
                self.shoot(target.rect.center)
                self.last_shoot = current_time

        # Propagation automatique de l'update aux enfants (comme la barre de vie)
        super().update(dt)


    def take_damage(self, damage: int) -> None:
        self.current_hp -= damage
        # Mise à jour visuelle de la barre (enfant)
        self.game.eventManager.post("UPDATE_KERNEL_HP", self.current_hp)
        
        if self.current_hp <= 0:
            self.alive = False
            self.active = False # On arrête de tirer
            self.visible = False # On disparaît
            # On pourrait déclencher un event GAME_OVER ici
            self.game.eventManager.publish("GAME_OVER")


    def reset(self):
        # On utilise spawn pour remettre l'entité en état "neuf"
        w, h = self.rect.size
        spawn_x = (self.game.st.WORLD_WIDTH / 2) - (w / 2)
        spawn_y = (self.game.st.WORLD_HEIGHT / 2) - (h / 2)
        
        self.spawn(spawn_x, spawn_y, "KERNEL")
        self.current_hp = self.max_hp
        self.kills = 0
        self.game.eventManager.publish("UPDATE_KERNEL_HP", self.current_hp)
        self.alive = True
    

    def shoot(self, target: tuple) -> None:
        # NOTE : Plus tard, tes projectiles (Bullet) devraient aussi 
        # être gérés par l'EntityManager pour le pooling !
        bullet = Bullet(self.rect.centerx, self.rect.centery, target_pos=target)
        
        # Pour l'instant on garde ton système de groupe, 
        # mais on l'ajoute aussi à la caméra pour le rendu
        self.game.bullets.add(bullet)
        if self.game.sceneManager.camera:
            self.game.sceneManager.camera.add_child(bullet)