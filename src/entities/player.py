import pygame
from ui.UIProgressBar import UIProgressBar
from entities.Entity import Entity  # Import de ta nouvelle base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class Player(Entity):
    def __init__(self, game: "App"):
        # On appelle le constructeur d'Entity
        # Position initiale au centre du monde
        self.game = game

        spawn_x = game.st.SCREEN_WIDTH / 2
        spawn_y = game.st.SCREEN_HEIGHT / 2
        
        self.stats = self.game.st.PLAYER_STATS
        w, h = self.stats['size']

        super().__init__(spawn_x, spawn_y, w, h, tag="PLAYER", uid="PLAYER")
        
        # Setup de l'image
        self.image = self.game.spriteManager.get_custom_sprite(self.game.st.PLAYER, (w, h))
        
        # Stats
        self.velocity = 500
        self.max_hp = self.stats['hp']
        self.current_hp = self.max_hp
        self.kills = 0
        self.alive = True 
        
        # Logique de grille
        # self.current_cell: tuple[int, int] = self.game.grid.get_cell_pos(self.pos.x, self.pos.y)

        # --- GESTION DES ENFANTS ---
        # Plus besoin de gérer la position de la barre manuellement dans update !
        self.hp_bar = UIProgressBar(x=0, y=-15, w=self.rect.w, h=8, uid="PLAYER_HP")
        self.hp_bar.dynamic_color = True
        self.add_child(self.hp_bar)

        # Souscription aux events
        self.game.eventManager.subscribe("NEW_GAME", self.reset)
        

    def update(self, dt):
        if not self.active: return

        keys = pygame.key.get_pressed()

        # ---------------------------------------------------------
        # AXE X : Mouvement et Collisions
        # ---------------------------------------------------------
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pos.x -= self.velocity * dt
            
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pos.x += self.velocity * dt
            
        
        # Synchronisation immédiate du rect pour le test de collision X
        self.rect.x = self.pos.x

        # Check collisions bâtiments sur X
        hits = [b for b in self.game.sceneManager.buildManager.entities if b.active and self.rect.colliderect(b.rect)]
        if hits:
            hit = hits[0]
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                self.rect.left = hit.rect.right
            elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.rect.right = hit.rect.left
            self.pos.x = self.rect.x # On recale le float sur le rect

        # ---------------------------------------------------------
        # AXE Y : Mouvement et Collisions
        # ---------------------------------------------------------
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pos.y -= self.velocity * dt
            
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pos.y += self.velocity * dt
            
        # Synchronisation immédiate du rect pour le test de collision Y
        self.rect.y = self.pos.y

        # Check collisions bâtiments sur Y
        hits = [b for b in self.game.sceneManager.buildManager.entities if b.active and self.rect.colliderect(b.rect)]
        if hits:
            hit = hits[0]
            if (keys[pygame.K_UP] or keys[pygame.K_w]):
                self.rect.top = hit.rect.bottom
            elif (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                self.rect.bottom = hit.rect.top
            self.pos.y = self.rect.y # On recale le float sur le rect

        # ---------------------------------------------------------
        # Finalisation (Contraintes, Grille, Enfants)
        # ---------------------------------------------------------
        self.constraints_world()
        #self.update_grid_logic()
        
        # Appel de l'update d'Entity pour propager aux enfants (barre de vie)
        super().update(dt)
    

    def update_grid_logic(self):
        new_cell = self.game.grid.get_cell_pos(self.rect.x, self.rect.y)
        if new_cell != self.current_cell:
            nx, ny = new_cell
            oldx, oldy = self.current_cell
            self.game.grid.set_cell_value(oldx, oldy, self.game.st.EMPTY, True)
            self.game.grid.set_cell_value(nx, ny, self.type, True)
            self.game.grid.update_flow_field(self.game.kernel.pos)
            self.current_cell = new_cell


    def constraints_world(self):
        # On limite aux bordures de la map (Settings)
        self.pos.x = max(0, min(self.pos.x, self.game.st.WORLD_WIDTH - self.rect.w))
        self.pos.y = max(0, min(self.pos.y, self.game.st.WORLD_HEIGHT - self.rect.h))
        self.rect.topleft = self.pos


    def take_damage(self, amount):
        self.current_hp -= amount
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        if self.current_hp <= 0:
            self.alive = False
            self.kill() # On utilise la méthode de Entity pour le pooling


    def reset(self):
        self.spawn(self.game.st.SCREEN_WIDTH / 2, self.game.st.SCREEN_HEIGHT / 2, "PLAYER")
        self.current_hp = self.max_hp
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        self.kills = 0
        self.alive = True