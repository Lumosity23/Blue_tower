import pygame
from entities.buildings.Building import Building
from entities.Entity import Entity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class BuildManager:


    def __init__(self, game: "App"):
        self.game = game
        
        # 1. Racine pour le rendu (Sera attachée à la Camera)
        self.root = Entity(0, 0, 0, 0, "ROOT", uid="BUILD_ROOT")
        
        # 2. Liste pour la logique et le pooling
        self.entities: list[Building] = []
        
        # État
        self.selected_build: Building | None = None

        # Souscriptions
        self.game.eventManager.subscribe("PLACE_BUILDING", self.attempt_build_from_event)
        self.game.eventManager.subscribe("NEW_GAME", self.clear_all)


    def attempt_build_from_event(self, event_data: dict):
        """ Reçoit les infos du Cursor : {'pos': Vector2, 'data': dict} """
        pos = event_data['pos']
        data = event_data['data']
        self.attempt_build(pos, data)


    def attempt_build(self, world_pos: pygame.math.Vector2, build_data: dict) -> None:
        """ Vérifie les conditions et lance la construction """
        cost = build_data.get("cost", 0)
        type_name = build_data.get("sprite_id").upper() # On utilise l'ID comme type

        # 1. Vérification Argent
        if not self.game.walletManager.buy(cost):
            self.game.eventManager.publish("ERROR_PAYMENT")
            return

        # 2. Vérification Grille (L'occupation a déjà été checkée par le Cursor, mais on re-vérifie ici)
        if self.game.grid.get_cell_isOccupied(world_pos.x, world_pos.y):
            self.game.eventManager.publish("ERROR_SOUND")
            return

        # 3. Création / Recyclage
        self.make_building(build_data, world_pos)
        self.game.eventManager.publish("BUILD_SUCCESS", type_name)


    def make_building(self, data: dict, pos: pygame.math.Vector2):
        type_name = data.get("sprite_id").upper()
        
        # On cherche la classe correspondante (Turret, Wall, etc.)
        # Si le type spécifique n'existe pas, on prend la classe Building de base
        build_class = Building.BUILDING_TYPES.get(type_name, Building)

        # --- LOGIQUE DE POOLING ---
        recycled_build = None
        for b in self.entities:
            if not b.active and isinstance(b, build_class):
                recycled_build = b
                break

        if recycled_build:
            recycled_build.spawn(pos.x, pos.y, uid=f"{type_name}_{id(recycled_build)}")
            # On pourrait avoir besoin de rafraîchir les stats si le bâtiment a été amélioré entre-temps
            recycled_build.data = data 
            build = recycled_build
        else:
            # Nouveau bâtiment
            build = build_class(pos.x, pos.y, data, self.game, uid=f"{type_name}_{len(self.entities)}")
            self.entities.append(build)
            self.root.add_child(build)

        # 4. Mise à jour du monde
        self.game.grid.set_cell_value(pos.x, pos.y, type_name)
        # On met à jour le chemin des ennemis vers le Kernel
        self.game.grid.update_flow_field(self.game.kernel.pos)


    def handle_event(self, event) -> bool:
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.game.eventManager.publish("BUILD_MODE")
                return True

        # On inverse l'ordre pour la sélection (le dernier bâti est "au dessus")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_build = None
            # IMPORTANT : Les bâtiments utilisent get_screen_rect() dans leur handle_event
            # On délègue la vérification de collision aux entités elles-mêmes
            for build in reversed(self.entities):
                if build.active and build.handle_event(event):
                    # Si un bâtiment a été sélectionné, on déselectionne le précédent
                    if self.selected_build and self.selected_build != build:
                        self.selected_build.deselect()
                    self.selected_build = build
                    return True

            # Si on clique ailleurs, on déselectionne tout
            if self.selected_build:
                self.selected_build.deselect()
                self.selected_build = None

        return False
    

    def clear_all(self):
        """ Désactive tous les bâtiments (pour le reset de partie) """
        for b in self.entities:
            b.kill() # Met active/visible à False