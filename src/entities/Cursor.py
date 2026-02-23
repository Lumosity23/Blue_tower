import pygame
from entities.Entity import Entity
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class Cursor(Entity):
    def __init__(self, game: "App"):
        # On l'initialise avec la taille d'une cellule par défaut
        super().__init__(0, 0, game.st.CELL_SIZE, game.st.CELL_SIZE, tag="CURSOR", uid="CURSOR")
        self.game = game
        
        # États du curseur
        self.current_build_data = None  # Stockera les infos du batiment choisi
        self.range_circle_surface = None # Surface pour le cercle de portée
        self.is_occupied = False
        
        # Surface par défaut (le carré blanc)
        self.default_image = pygame.Surface((self.game.st.CELL_SIZE, self.game.st.CELL_SIZE), pygame.SRCALPHA)
        self.default_image.fill((255, 255, 255, 100))
        self.image = self.default_image

        # On s'abonne à l'événement de sélection
        self.game.eventManager.subscribe("SELECT_BUILD", self.on_build_selected)
        self.game.eventManager.subscribe("CANCEL_BUILD", self.on_build_canceled)

    def on_build_selected(self, build_key: str):
        """ 
        On reçoit juste la clé (ex: 'TURRET_L1') 
        et on va piocher dans les settings.
        """
        # On récupère le dictionnaire complet depuis les settings
        data = self.game.st.BUILDINGS_DATA.get(build_key)
        if not data: return

        self.current_build_data = data

        # On prépare le visuel (Ghost Sprite)
        sprite = self.game.spriteManager.get_custom_sprite(data['sprite_id'], data['size'])
        self.image = sprite.copy()
        self.image.set_alpha(150)

        # On ajuste la taille du rect de collision selon le bâtiment
        self.rect.size = data['size']

        # On prépare le cercle de portée
        if data['range'] > 0:
            r = data['range']
            self.range_circle_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(self.range_circle_surface, (200, 200, 200, 80), (r, r), r, 2)
        else:
            self.range_circle_surface = None

    def on_build_canceled(self):
        self.current_build_data = None
        self.image = self.default_image
        self.range_circle_surface = None

    def update(self, dt):
        # 1. Conversion Screen -> World (Prise en compte de la caméra)
        mx, my = pygame.mouse.get_pos()
        cam_x, cam_y = self.game.sceneManager.camera.pos.x, self.game.sceneManager.camera.pos.y
        
        world_mx = mx - cam_x
        world_my = my - cam_y

        # 2. Snapping à la grille
        px = (world_mx // self.game.st.CELL_SIZE) * self.game.st.CELL_SIZE
        py = (world_my // self.game.st.CELL_SIZE) * self.game.st.CELL_SIZE
        self.pos.update(px, py)
        self.rect.topleft = self.pos

        # 3. Vérification de collision / Occupation
        self.check_validity(world_mx, world_my)

    def check_validity(self, mx, my):
        # Vérification sur la grille
        cell_val = self.game.grid.get_cell_value(mx, my)
        
        # Vérification collision avec entités (Ennemis/Joueur) via EntityManager
        collision_entity = any(e.rect.colliderect(self.rect) for e in self.game.entityManager.entities if e.active)

        if cell_val != self.game.st.EMPTY or collision_entity:
            self.is_occupied = True
        else:
            self.is_occupied = False

    def draw(self, surface: pygame.Surface):
        if not self.visible: return
        
        # On récupère la position écran pour le rendu
        screen_rect = self.get_screen_rect()
        
        # 1. Dessiner le cercle de portée en premier (dessous)
        if self.current_build_data and self.range_circle_surface:
            r = self.current_build_data['range']
            # On centre le cercle sur le bâtiment
            range_pos = (screen_rect.centerx - r, screen_rect.centery - r)
            surface.blit(self.range_circle_surface, range_pos)

        # 2. Dessiner le Ghost Sprite
        # On applique une teinte rouge si c'est occupé
        temp_image = self.image.copy()
        if self.is_occupied:
            temp_image.fill((255, 50, 50, 100), special_flags=pygame.BLEND_RGBA_MULT)
        
        surface.blit(temp_image, screen_rect)