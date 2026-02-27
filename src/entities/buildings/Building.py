import pygame
from entities.Entity import Entity
from ui.UIProgressBar import UIProgressBar
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
        
        # État
        self.state = "IDLE" # IDLE, HOVER, SELECTED
        
        # Visuel
        self.source_image = self.game.spriteManager.get_custom_sprite(
            data.get("sprite_id"), (w, h)
        )
        self.image = self.source_image.copy()

        # Stats issues du dictionnaire
        self.max_hp = data.get("hp", 100)
        self.current_hp = self.max_hp
        self.cost = data.get("cost", 0)
        self.range = data.get("range", 0)

        # --- ENFANT : Barre de Vie ---
        # On la crée mais on la cache par défaut (elle ne s'affiche qu'au survol/clic)
        self.hp_bar = UIProgressBar(x=5, y=-12, w=self.rect.w - 10, h=6, uid=f"{uid}_hp" if uid else None)
        self.hp_bar.visible = False
        self.add_child(self.hp_bar)

    def handle_event(self, event) -> bool:
        if not self.visible or not self.active: return False

        # On utilise get_screen_rect pour gérer le décalage caméra !
        screen_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = screen_rect.collidepoint(mouse_pos)

        # 1. Gestion du Survol (Hover)
        if event.type == pygame.MOUSEMOTION:
            if self.state != "SELECTED":
                new_state = "HOVER" if is_hovered else "IDLE"
                if new_state != self.state:
                    self.state = new_state
                    self.on_state_change()

        # 2. Gestion du Clic (Sélection)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_hovered:
                self.select()
                return True
            else:
                self.deselect()

        return super().handle_event(event) # Propagation aux enfants si besoin

    def select(self) -> None:
        self.state = "SELECTED"
        self.game.eventManager.publish("BUILDING_SELECTED", self)
        self.on_state_change()

    def deselect(self) -> None:
        if self.state == "SELECTED":
            self.state = "IDLE"
            self.on_state_change()

    def on_state_change(self):
        """ Gère les effets visuels selon l'état """
        # Visibilité de la barre de vie
        self.hp_bar.visible = (self.state in ["HOVER", "SELECTED"])
        
        # On recrée l'image avec un feedback (ex: contour blanc si sélectionné)
        self.image = self.source_image.copy()
        if self.state == "SELECTED":
            pygame.draw.rect(self.image, (255, 255, 255), (0, 0, self.rect.w, self.rect.h), 2)
        elif self.state == "HOVER":
            # Petit effet de brillance/teinte légère
            self.image.fill((30, 30, 30), special_flags=pygame.BLEND_RGB_ADD)

    def take_damage(self, amount):
        self.current_hp -= amount
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        if self.current_hp <= 0:
            self.die()

    def die(self):
        self.active = False
        self.visible = False
        # Logique de destruction (libérer la grille)
        self.game.eventManager.publish("BUILDING_DESTROYED", self)

    def update(self, dt):
        # Les bâtiments n'ont souvent pas de mouvement, mais ils peuvent 
        # avoir des enfants qui s'animent (tourelles qui tournent)
        super().update(dt)