import pygame
from ui.UIProgressBar import UIProgressBar
from entities.Entity import Entity  # Ta nouvelle base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class Enemie(Entity):


    def __init__(self, x: int, y: int, size: tuple, game: "App", type: int = 1, uid: str = None):
        # 1. Init de la base Entity
        super().__init__(x, y, size[0], size[1], "ENEMY", uid)
        
        self.game = game
        self.type = type
        self.stats = self.game.st.ENEMIES_DATA[type]
        self.size = self.stats["size"]

        # Setup visuel
        self.image = self.game.spriteManager.get_custom_sprite(self.stats["sprite_id"], size, 'circle')
        
        # Logique de mouvement
        self.velocity = 150
        self.director_vector = pygame.math.Vector2(0, 0)
        self.target_pos = pygame.math.Vector2(x, y)
        self.arrived = True
        self.is_prio_target = False
        self.is_obstacle = False

        # Stats
        self.max_hp = self.stats['hp']
        self.current_hp = self.max_hp
        self.damage = self.stats['damage']
        
        # --- ENFANT : Barre de vie ---
        # Elle est attachée à l'ennemi et suit ses mouvements automatiquement
        self.hp_bar = UIProgressBar(x=0, y=-10 , uid=f"{uid}_hp" if uid else None)
        self.hp_bar.setup( w=self.rect.w, h=5, show_text=False )
        self.hp_bar.dynamic_color = True
        self.add_child(self.hp_bar)

        # Pipeline de vie
        self.state = "MOVE"
        self.action = {
            "IDLE" : self.idle,
            "MOVE" : self.move,
            "ATTACK" : self.attack
        }


    def spawn(self, x, y, size, uid=None, **kwargs):
        """ Surcharge de spawn pour réinitialiser la logique de l'ennemi """
        super().spawn(x, y, uid)
        self.size = size
        self.current_hp = self.max_hp
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        self.arrived = True
    

    def update(self, dt):
        if not self.active: return
        
        # Debut du Pipline
        self._view()
        self._think()

        # Effectuer l'action de son statment
        self.action[self.state](dt)

        self.check_chunk()
        # Update des enfants (Barre de vie)
        super().update(dt)


    def next_target(self, cell_pos=False) -> tuple[int, int]:
        cx, cy = self.game.grid.get_cell_pos(self.pos.x, self.pos.y)
        neighbors = self.game.grid.getNeighborsAndCost(cx, cy)
        
        cheapest_cell = float('inf')
        
        for n, cost in neighbors.items():
            if cost < cheapest_cell:
                cheapest_cell = cost
                nx, ny = n

        if cell_pos:
            return nx, ny
        
        dx = ((nx * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2) - self.size[0] / 2
        dy = ((ny * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2) - self.size[1] / 2

        return dx, dy


    def check_chunk(self) -> None:
        # Verifier si on a changer de chunk
        new_chunk = self.game.grid.get_chunk_cell(self.rect.center)
        if new_chunk != self.old_chunk:
            self.chunk_changed = True


    def take_damage(self, amount):
        if not self.active: return
        
        self.current_hp -= amount
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        
        if self.current_hp <= 0:
            self.kill()


    def kill( self ):
        """ Mort de l'ennemi : on désactive au lieu de supprimer (Pooling) """
        # On prévient le reste du jeu
        reward = self.type * 20
        self.game.eventManager.publish("ENEMY_KILLED", reward)
        super().kill()
    
    def _view(self) -> None:

        # Regarder si target_prio in range
        """ if self.game.player in self.game.grid.get_entities_around(self.pos, radius=1):
            self.is_prio_target = True
            self.prio_target_pos = self.game.player.pos
        self.is_prio_target = False """
        
        self.target_pos.update(self.next_target())

        # Regarder si un mur devant
        if self.game.grid.get_cell_value(*self.target_pos.xy) != self.game.st.EMPTY and self.pos.distance_to(self.target_pos) <= (self.rect.width + 10):
            self.is_obstacle = True
        else : self.is_obstacle = False

        # 1. Logique de Pathfinding (Flow Field / Grid)
        if self.arrived and not self.is_obstacle:
            self.arrived = False

    
    def _think(self) -> None:

        if self.is_obstacle:
            self.state = "ATTACK"

        else : self.state = "MOVE"
    

    def move(self, dt) -> None:
      
        # Calcul du vecteur de direction
        self.director_vector = self.target_pos - self.pos
        length = self.director_vector.length()

        if length > 0:
            self.director_vector.normalize_ip()

        if length > 2: # Seuil de proximité (un peu plus que 1 pour éviter les micro-saccades)
            # Déplacement fluide sur self.pos (float)
            self.pos += self.director_vector * self.velocity * dt
            # Mise à jour du Rect pour les collisions et get_screen_rect
        
        else:
            self.arrived = True


    def attack(self, dt) -> None:
        entity: "Entity"  = self.game.grid.get_entity_at(*self.target_pos)
        if entity :
            self.kick(entity, self.damage)


    def idle(self, dt) -> None:
        pass