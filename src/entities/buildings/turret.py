from typing import TYPE_CHECKING

from ..bullet import Bullet
from .Building import Building

if TYPE_CHECKING:
    from main import App


class Turret(Building):
    def __init__(self, x: int, y: int, data: dict, game: "App", uid):
        super().__init__(x, y, data, game, tag="TURRET", uid=uid)

        ## DAMAGE SECTION
        self.damage = 10

        ## RANGE SECTION
        self.range = self.data["range"]

    def update(self, dt):

        if self.delay(1, dt) and not self.game.sceneManager.waveManager.end_wave:
            target = self.game.sceneManager.waveManager.nearest_enemy(self.rect.center)
            # target.pos: pygame.math.Vector2
            if target:
                if target.pos.distance_to(self.pos) <= self.range:
                    self.shoot(target.rect.center)

    def shoot(self, target: tuple):
        self.game.sceneManager.entityManager.spawn(
            Bullet,
            self.rect.centerx,
            self.rect.centery,
            uid=f"{self.uid}_Bullet",
            target_pos=target,
            owner=self,
            bullet_damage=self.damage,
        )


Turret.ui_config(
    ("ICON", "TURRET", "image"),
    ("BAR", "Vie", "current_hp", "max_hp"),
    ("STAT", "kills", "kills"),
    ("STAT", "CHUNK", "chunk"),
)

Turret.upgrade_config(
    ("Damage", "damage", 100, 200, 10),
    ("Range", "range", 1000, 300, 5),
)
