import pygame
from entities.Entity import Entity
from ui.UIProgressBar import UIProgressBar
from ui.UIRange import UIRange
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class Building(Entity):
    # Registre automatique des types de bâtiments
    BUILDING_TYPES = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.BUILDING_TYPES[cls.__name__.upper()] = cls


    def __init__(self, x, y, data: dict, game: "App", tag, uid: str = None):
        # 1. Init Entity (Position Monde)
        w, h = data.get("size", (game.st.CELL_SIZE, game.st.CELL_SIZE))
        super().__init__(x, y, w, h, tag=tag, uid=uid)
        
        self.game = game
        self.data = data # On garde le dictionnaire de config
        self.grid_pos = (0, 0)

        # État
        self.meta_state = "IDLE" # IDLE, HOVER, SELECTED
        self.type = "BUILDING"

        # Visuel
        self.source_image = self.game.spriteManager.get_custom_sprite(
            data.get("sprite_id"), (w, h)
        )
        self.image = self.source_image.copy()
        self.current_image = self.source_image.copy()

        # Stats issues du dictionnaire
        self.max_hp = data.get("hp", 100)
        self.current_hp = self.max_hp
        self.cost = data.get("cost", 0)
        self.range = data.get("range", 0)
        self.damage = data.get("damage", 0)
        self.cooldown = data.get("cooldown", 0)

        # --- ENFANT : Barre de Vie ---
        # On la crée mais on la cache par défaut (elle ne s'affiche qu'au survol/clic)
        self.hp_bar = UIProgressBar(x=5, y=self.rect.height - 12, uid=f"{uid}_hp" if uid else None)
        self.hp_bar.setup(w=self.rect.w - 10, h=6, show_text=False)
        self.hp_bar.visible = False
        self.add_child(self.hp_bar)

        if self.data["range"] > 0:
            self.range_circle = UIRange((0 - self.range) + (self.data["size"][0] / 2), (0 - self.range) + (self.data["size"][1] / 2), self.data['range'], self, f"{uid}_range")
            self.range_circle.visible = False
            self.add_child(self.range_circle)
        else:
            self.range_circle = None
            

    def handle_event(self, event) -> bool:
        if not self.visible or not self.active: return False

        # On utilise get_screen_rect pour gérer le décalage caméra !
        mouse_pos = pygame.mouse.get_pos()
        cam_offset = self.game.sceneManager.main_camera.offset
        world_mouse_pos = (mouse_pos[0] + cam_offset.x, mouse_pos[1] + cam_offset.y)

        # 3. Maintenant les deux sont dans le World Space, on peut tester !
        is_hovered = self.get_screen_rect().collidepoint(world_mouse_pos)

        # 1. Gestion du Survol (Hover)
        if event.type == pygame.MOUSEMOTION:
            if self.meta_state != "SELECTED":
                new_meta_state = "HOVER" if is_hovered else "IDLE"
                if new_meta_state != self.meta_state:
                    self.meta_state = new_meta_state
                    self.on_meta_state_change()

        # 2. Gestion du Clic (Sélection)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_hovered:
                self.select()
                return True
            else:
                self.deselect()

        return super().handle_event(event) # Propagation aux enfants si besoin


    def select(self) -> None:
        self.meta_state = "SELECTED"
        self.game.eventManager.publish("BUILDING_SELECTED", self)
        self.on_meta_state_change()


    def deselect(self) -> None:
        if self.meta_state == "SELECTED":
            self.meta_state = "IDLE"
            self.on_meta_state_change()


    def on_meta_state_change(self):
        """ Gère les effets visuels selon l'état """
        # Visibilité de la barre de vie
        self.hp_bar.visible = (self.meta_state in ["HOVER", "SELECTED"])
        if self.range_circle:
            self.range_circle.visible = (self.meta_state in ["HOVER", "SELECTED"])
        
        # On recrée l'image avec un feedback (ex: contour blanc si sélectionné)
        self.image = self.current_image.copy()

        if self.meta_state == "SELECTED":
            pygame.draw.rect(self.image, (255, 255, 255), (0, 0, self.rect.w, self.rect.h), 2)
        elif self.meta_state == "HOVER":
            # Petit effet de brillance/teinte légère
            self.image.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_ADD)


    def take_damage(self, amount):
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        super().take_damage(amount)


    def kill(self):
        # Logique de destruction (libérer la grille)
        self.game.eventManager.publish("BUILDING_DESTROYED", self)
        super().kill()


    def spawn(self, x, y, uid=None, **kwargs):
        
        self.current_hp = self.max_hp
        self.kills = 0
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        self.hp_bar.visible = False
        self.alive = True
        super().spawn(x, y, uid, **kwargs)