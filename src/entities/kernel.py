import pygame
from .bullet import Bullet
from .buildings.Building import Building # Import de la nouvelle base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class Kernel(Building):
    def __init__(self, game: "App"):
        # 1. Initialisation de la base Entity
        # On le place au centre du monde
        data =  game.st.BUILDINGS_DATA["KERNEL"]
        w, h = data['size']

        spawn_x = (game.st.WORLD_WIDTH // 2) - (w // 2)
        spawn_y = (game.st.WORLD_HEIGHT // 2) - (h // 2)
        
        super().__init__(spawn_x, spawn_y, data, game, tag="KERNEL", uid="KERNEL")
        
        self.rect.center = self.pos.xy
        # print(self.rect.center)

        # Stats
        self.last_shoot = pygame.time.get_ticks()
        
        ## DAMAGE SECTION
        self.damage = 10
        self.max_dm = 100
        self.price_dm = 200
        self.rate_dm = 10

        ## RANGE SECTION
        self.range = self.data["range"]
        self.max_rg = 1000
        self.price_rg =300
        self.rate_rg = 5


    def update(self, dt):
        if not self.active: return

        # Logique de tir
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot > self.cooldown and not self.game.sceneManager.waveManager.end_wave:
            # On utilise le centre du Kernel pour chercher l'ennemi
            target = self.game.sceneManager.waveManager.nearest_enemy(self.rect.center)
            if target:
                if self.pos.distance_to(target.pos) <= self.range:
                    self.shoot(target.rect.center)
                    self.last_shoot = current_time

        # Propagation automatique de l'update aux enfants (comme la barre de vie)
        super().update(dt)


    def take_damage(self, damage: int) -> None:
        
        mapping = {
            "xy" : self.rect.center,
            "text" : damage
        }

        self.game.eventManager.publish("SHOW_FT", mapping)

        self.current_hp -= damage
        # Mise à jour visuelle de la barre (enfant)
        self.game.eventManager.publish("UPDATE_KERNEL_HP", self.current_hp)
        
        if self.current_hp <= 0:
            self.alive = False
            self.active = False # On arrête de tirer
            self.visible = False # On disparaît
            # On pourrait déclencher un event GAME_OVER ici
            self.game.eventManager.publish("GAME_OVER")


    def reset(self):
        # On utilise spawn pour remettre l'entité en état "neuf"
        w, h = self.rect.size
        spawn_x = (self.game.st.WORLD_WIDTH // 2) - (w // 2)
        spawn_y = (self.game.st.WORLD_HEIGHT // 2) - (h // 2)
        
        self.spawn(spawn_x, spawn_y, "KERNEL")
        self.current_hp = self.max_hp
        self.kills = 0
        self.game.eventManager.publish("UPDATE_KERNEL_HP", self.current_hp)
        self.alive = True
        self.range_circle.visible = False
        self.hp_bar.visible = False

        for corner in [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]:
            # print(f"{corner} dois donner ce chunk -> :{self.game.grid.get_chunk_cell(corner)}")
            self.game.grid.set_entity_at_chunk(self, corner)
            # self.game.grid.show_chunk()


    def shoot(self, target: tuple) -> None:
        # Systeme de pooling
        self.game.sceneManager.entityManager.spawn(Bullet, self.rect.centerx, self.rect.centery, uid="Kernel_Bullet", target_pos=target, owner=self, bullet_damage=self.damage)


Kernel.ui_config(
    ("ICON", "your base", "image"),
    ("BAR", "Vie", "current_hp", "max_hp"),
    ("STAT", "kills", "kills"),
    ("STAT", "CHUNK", "chunk")
)

Kernel.upgrade_config(
    ("Damage", "damage", "max_dm", "price_dm", "rate_dm"),
    ("Range", "range", "max_rg", "price_rg", "rate_rg")
)