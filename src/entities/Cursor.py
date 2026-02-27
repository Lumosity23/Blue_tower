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

        # De base pas visible mais quand en mode EDIT
        self.visible = False
        self.active = False

        # On s'abonne à l'événement de sélection
        self.game.eventManager.subscribe("BUILD_MODE", self.show)
        self.game.eventManager.subscribe("SELECT_BUILD", self.on_build_selected)


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
        mx, my = pygame.mouse.get_pos()
        cam_offset = self.game.sceneManager.main_camera.offset
        
        # Screen -> World (Pour placer le curseur dans le monde)
        world_mx = mx + cam_offset.x
        world_my = my + cam_offset.y

        # Snapping à la grille
        px = (world_mx // self.game.st.CELL_SIZE) * self.game.st.CELL_SIZE
        py = (world_my // self.game.st.CELL_SIZE) * self.game.st.CELL_SIZE
        self.pos.update(px, py)
        self.rect.topleft = self.pos

        self.check_validity(world_mx, world_my)


    def check_validity(self, mx, my):
        # Vérification sur la grille
        cell_val = self.game.grid.get_cell_value(mx, my)
        
        # Vérification collision avec entités (Ennemis/Joueur) via EntityManager
        collision_entity = any(e.rect.colliderect(self.rect) for e in self.game.sceneManager.entityManager.entities if e.active)

        if cell_val != self.game.st.EMPTY or collision_entity:
            self.is_occupied = True
        else:
            self.is_occupied = False


    def draw(self, surface: pygame.Surface):
        if not self.visible: return
        
        # ATTENTION : get_screen_rect() de Entity renvoie la pos absolue du MONDE ! 
        # (Le nom de la méthode est un peu trompeur, on devrait l'appeler get_world_rect)
        world_rect = self.get_screen_rect()
        cam_offset = self.game.sceneManager.main_camera.offset
        
        # World -> Screen (On SOUSTRAIT l'offset pour dessiner manuellement)
        screen_x = world_rect.x - cam_offset.x
        screen_y = world_rect.y - cam_offset.y

        # 1. Dessiner le cercle (centré sur le screen_x/y)
        if self.current_build_data and self.range_circle_surface:
            r = self.current_build_data['range']
            range_pos = (screen_x + (self.rect.w//2) - r, screen_y + (self.rect.h//2) - r)
            surface.blit(self.range_circle_surface, range_pos)

        # 2. Dessiner le Ghost Sprite
        temp_image = self.image.copy()
        if self.is_occupied:
            temp_image.fill((255, 50, 50, 100), special_flags=pygame.BLEND_RGBA_MULT)
        
        # On dessine aux coordonnées calculées !
        surface.blit(temp_image, (screen_x, screen_y))
    

    def show(self) -> None:
        self.visible = not self.visible
        self.active = not self.active


    def get_pos_world(self) -> tuple[int, int]:
        mx, my = pygame.mouse.get_pos()
        cam_offset = self.game.sceneManager.main_camera.offset
        
        return mx + cam_offset.x, my + cam_offset.y
    
    
    def handle_event(self, event):
        
        if not self.game.edit_mode: return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.on_build_canceled()
                return True

            if event.button == 1 and self.current_build_data != None:
                data = {
                    "pos" : pygame.math.Vector2(self.get_pos_world()),
                    "data" : self.current_build_data
                }
                self.game.eventManager.publish("PLACE_BUILDING", data)
                return True
            
        super().handle_event(event)