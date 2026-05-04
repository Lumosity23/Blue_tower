from typing import TYPE_CHECKING

import pygame

from entities.Entity import Entity  # Ta nouvelle base
from ui.element.UIProgressBar import UIProgressBar

if TYPE_CHECKING:
    from main import App


class Enemie(Entity):
    def __init__(
        self, x: int, y: int, size: tuple, game: "App", type: int = 1, uid: str = None
    ):
        # 1. Init de la base Entity
        super().__init__(x, y, size[0], size[1], "ENEMY", uid)

        self.game = game
        self.type = type
        self.pos: pygame.Vector2
        self.old_chunk = self.chunk
        self.director_vector = pygame.math.Vector2(0, 0)
        self.target_pos = pygame.math.Vector2(x, y)
        self.is_prio_target = False
        self.is_obstacle = False

        # Activation des states
        self.set_states(type)

        # Pipeline de vie
        self.state = "MOVE"
        self.action = {"IDLE": self.idle, "MOVE": self.move, "ATTACK": self.attack}

    def spawn(self, x, y, type, uid=None, **kwargs):
        """Surcharge de spawn pour réinitialiser la logique de l'ennemi"""
        super().spawn(x, y, uid)
        self.set_states(type)

    def set_states(self, type) -> None:
        for child in self.children:
            self.remove_child(child)

        self.stats = self.game.st.ENEMIES_DATA[type]
        self.size = self.stats["size"]
        self.image = self.game.spriteManager.get_custom_sprite(
            self.stats["sprite_id"], self.size, "circle"
        )
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.xy
        self.max_hp = self.stats["hp"]
        self.velocity = self.stats["velocity"]
        self.damage = self.stats["damage"]
        self.reward = self.stats["reward"]
        self.armor = self.stats["armor"]
        self.current_hp = self.max_hp
        self.hp_bar = UIProgressBar(
            x=0, y=-10, uid=f"{self.uid}_hp" if self.uid else None
        )
        self.hp_bar.setup(w=self.rect.w, h=5, show_text=False)
        self.hp_bar.dynamic_color = True
        self.add_child(self.hp_bar)
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        self.arrived = True

    def update(self, dt):
        if not self.active:
            return

        # Debut du Pipline
        self._view()
        output = self._think()

        # Effectuer l'action de son statment
        self.action[self.state](dt, output)

        self.check_chunk()
        # Update des enfants (Barre de vie)
        super().update(dt)

    def next_target(self, cell_pos=False) -> tuple[float, float]:
        cx, cy = self.game.grid.get_cell_pos(self.pos.x, self.pos.y)
        neighbors = self.game.grid.getNeighborsAndCost(cx, cy)

        cheapest_cell = float("inf")
        nx, ny = cx, cy

        if neighbors:
            for n, cost in neighbors.items():
                if cost < cheapest_cell:
                    cheapest_cell = cost
                    nx, ny = n

        if cell_pos:
            return nx, ny

        dx = (nx * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2
        dy = (ny * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2

        return dx, dy

    def check_chunk(self) -> None:
        # Verifier si on a changer de chunk
        self.new_chunk = self.game.grid.get_chunk_cell(self.rect.center)
        if self.new_chunk != self.old_chunk:
            self.chunk_changed = True
            self.old_chunk = self.chunk

    def take_damage(self, amount):
        if not self.active:
            return

        super().take_damage(amount)
        self.hp_bar.update_values(self.current_hp, self.max_hp)

    def kill(self):
        """Mort de l'ennemi : on désactive au lieu de supprimer (Pooling)"""
        # On prévient le reste du jeu
        self.game.eventManager.publish("ENEMY_KILLED", self.reward)
        super().kill()

    def _view(self) -> None:
        self.is_obstacle = False
        center = pygame.Vector2(self.rect.center)
        
        # 1. Regarder si target_prio (player) in range
        if self.game.player in self.game.grid.get_entities_around(center, radius=2):
            player_pos = pygame.Vector2(self.game.player.rect.center)
            kernel_pos = pygame.Vector2(self.game.kernel.rect.center)
            
            if center.distance_to(player_pos) < center.distance_to(kernel_pos):
                self.target_pos.update(player_pos)
                
                # Check si un bâtiment bloque le passage vers le joueur
                dir_to_player = player_pos - center
                if dir_to_player.length() > 0:
                    check_pos = center + dir_to_player.normalize() * (self.rect.width / 2 + 10)
                    if self.game.grid.get_cell_isOccupied(check_pos.x, check_pos.y):
                        self.target_pos.update(check_pos)
                        self.is_obstacle = True
                        return

                if center.distance_to(self.target_pos) <= (self.rect.width / 2 + 15):
                    self.is_obstacle = True
                return

        # 2. Verifier si on est pres du kernel
        kernel_pos = pygame.Vector2(self.game.kernel.rect.center)
        if center.distance_to(kernel_pos) <= (self.rect.width / 2 + self.game.kernel.rect.width / 2 + 10):
            self.target_pos.update(kernel_pos)
            self.is_obstacle = True
            return

        # 3. Prendre la prochaine case (centre) via Flow Field
        nx, ny = self.next_target(cell_pos=True)
        target_world_x = (nx * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2
        target_world_y = (ny * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2
        
        self.target_pos.update(target_world_x, target_world_y)

        # 4. Regarder si un obstacle (bâtiment) est devant sur la grille
        cell_value = self.game.grid.get_cell_value(nx, ny, iscellpos=True)
        if cell_value != self.game.st.EMPTY:
            if center.distance_to(self.target_pos) <= (self.rect.width / 2 + 15):
                self.is_obstacle = True

        # Logique de Pathfinding
        if self.arrived and not self.is_obstacle:
            self.arrived = False

    def _think(self) -> None:

        if self.is_obstacle:
            self.state = "ATTACK"
            # Si on attaque, retourner l'entite visee
            if self.rect.colliderect(self.game.player.rect): return self.game.player
            if self.rect.colliderect(self.game.kernel.rect): return self.game.kernel
            return self.game.grid.get_entity_at(*self.target_pos.xy)

        else:
            self.state = "MOVE"

    def move(self, dt, output) -> None:
        # On utilise le centre actuel pour la direction
        center = pygame.Vector2(self.rect.center)
        self.director_vector = self.target_pos - center
        length = self.director_vector.length()

        if length > 0:
            self.director_vector.normalize_ip()

        if length > 2:
            velocity_vec = self.director_vector * self.velocity * dt
            
            # Mouvement X avec glissement
            self.pos.x += velocity_vec.x
            self.sync_rect()
            if self.check_static_collision():
                self.pos.x -= velocity_vec.x
                self.sync_rect()

            # Mouvement Y avec glissement
            self.pos.y += velocity_vec.y
            self.sync_rect()
            if self.check_static_collision():
                self.pos.y -= velocity_vec.y
                self.sync_rect()
        else:
            self.arrived = True

    def sync_rect(self):
        """ Synchronise le Rect avec self.pos (topleft) """
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def check_static_collision(self) -> bool:
        """ Vérifie les collisions avec la grille et le kernel """
        # Check les coins du rect pour la grille
        for pt in [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]:
            if self.game.grid.get_cell_isOccupied(*pt):
                return True

        # Check collision avec le Kernel
        if self.rect.colliderect(self.game.kernel.rect):
            return True

        return False

    def attack(self, dt, entity) -> None:

        if entity and self.delay(1, dt):
            self.kick(entity, self.damage)

    def idle(self, dt, **kwargs) -> None:
        pass
