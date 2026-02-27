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
        self.stats = self.game.st.ENEMIE_STATS
        self.size = self.stats["size"]

        # Setup visuel
        self.image = self.game.spriteManager.get_custom_sprite(self.game.st.ENEMIE, size, 'circle')
        
        # Logique de mouvement
        self.velocity = 150
        self.director_vector = pygame.math.Vector2(0, 0)
        self.target_pos = pygame.math.Vector2(x, y)
        self.arrived = True
        
        # Stats
        self.max_hp = self.stats['hp']
        self.current_hp = self.max_hp
        
        # --- ENFANT : Barre de vie ---
        # Elle est attachée à l'ennemi et suit ses mouvements automatiquement
        self.hp_bar = UIProgressBar(x=0, y=-10, w=self.rect.w, h=5, uid=f"{uid}_hp" if uid else None, show_text=False)
        self.hp_bar.dynamic_color = True
        self.add_child(self.hp_bar)


    def spawn(self, x, y, size, game, uid=None):
        """ Surcharge de spawn pour réinitialiser la logique de l'ennemi """
        super().spawn(x, y, uid)
        self.size = size
        self.current_hp = self.max_hp
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        self.arrived = True
        # On s'assure que les enfants sont bien réactivés
        self.set_child("active", True)
        self.set_child("visible", True)


    def update(self, dt):
        if not self.active: return
        
        # 1. Logique de Pathfinding (Flow Field / Grid)
        if self.arrived:
            nx, ny = self.next_target()
            
            # Calcul de la position cible au centre de la cellule
            dx = ((nx * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2) - self.size[0] / 2
            dy = ((ny * self.game.st.CELL_SIZE) + self.game.st.CELL_SIZE / 2) - self.size[1] / 2

            self.target_pos.update(dx, dy)
            self.arrived = False
              
        # 2. Calcul du vecteur de direction
        self.director_vector = self.target_pos - self.pos
        length = self.director_vector.length()

        if length > 0:
            self.director_vector.normalize_ip()

        if length > 2: # Seuil de proximité (un peu plus que 1 pour éviter les micro-saccades)
            # Déplacement fluide sur self.pos (float)
            self.pos += self.director_vector * self.velocity * dt
            # Mise à jour du Rect pour les collisions et get_screen_rect
            self.rect.center = self.pos
        else:
            self.arrived = True

        # 3. Update des enfants (Barre de vie)
        super().update(dt)


    def next_target(self) -> tuple[int, int]:
        cx, cy = self.game.grid.get_cell_pos(self.pos.x, self.pos.y)
        neighbors = self.game.grid.getNeighborsAndCost(cx, cy)
        
        next_cell = (cx, cy)
        cheapest_cell = float('inf')
        
        for n, cost in neighbors.items():
            if cost < cheapest_cell:
                cheapest_cell = cost
                next_cell = n

        return next_cell


    def take_damage(self, amount):
        if not self.active: return
        
        self.current_hp -= amount
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        
        if self.current_hp <= 0:
            self.kill()


    def kill(self):
        """ Mort de l'ennemi : on désactive au lieu de supprimer (Pooling) """
        # On prévient le reste du jeu
        reward = self.type * 20
        self.game.eventManager.publish("ENEMY_KILLED", reward)
        super().kill()