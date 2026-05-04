import pygame
from entities.buildings.Building import Building
from entities.buildings.wall import Wall
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class BuildManager:


    def __init__(self, game: "App"):
        self.game = game
        
        # Liste pour la logique et le pooling
        self.entities: list[Building] = []
        
        # État
        self.selected_build: Building | None = None

        Wall.get_sides_sprite(game)

        # Souscriptions
        self.game.eventManager.subscribe("PLACE_BUILDING", self.attempt_build_from_event)
        self.game.eventManager.subscribe("NEW_GAME", self.new_game)
        self.game.eventManager.subscribe("BUILDING_DESTROYED", self.clean_chunk)


    def update(self, dt):
        """ Update uniquement les entités actives """
        # Update tout le entites active
        for entity in self.entities:
            if entity.active:
                entity.update(dt)


    def clean_chunk(self, building: Building) -> None:
        self.check_buildings(building, True)
        self.game.sceneManager.main_camera.remove_entity(building)
        self.game.grid.remove_entity_chunk(building)
        self.game.grid.remove_build_at(*building.grid_pos, True)
        self.game.grid.update_flow_field(self.game.kernel.pos)
        # print(f"la cell a bien ete changer : {self.game.grid.get_cell_value(*building.rect.center)}")
    

    def attempt_build_from_event(self, event_data: dict):
        """ Reçoit les infos du Cursor : {'pos': Vector2, 'data': dict} """
        pos = event_data['pos']
        data = event_data['data']
        self.attempt_build(pos, data)


    def attempt_build(self, world_pos: pygame.math.Vector2, build_data: dict) -> None:
        """ Vérifie les conditions et lance la construction """
        cost = build_data.get("cost", 0)
        type_name = build_data.get("sprite_id").upper() # On utilise l'ID comme type

        # 2. Vérification Grille (L'occupation a déjà été checkée par le Cursor, mais on re-vérifie ici)
        if self.game.grid.get_cell_isOccupied(world_pos.x, world_pos.y):
            self.game.eventManager.publish("ERROR_SOUND")
            return

        # 1. Vérification Argent
        if not self.game.walletManager.buy(cost):
            self.game.eventManager.publish("ERROR_PAYMENT")
            return

        # 3. Création / Recyclage
        self.make_building(build_data, world_pos)
        self.game.eventManager.publish("BUILD_SUCCESS", type_name)


    def make_building(self, data: dict, pos: pygame.math.Vector2):
        type_name = data.get("sprite_id").upper()
        
        # On cherche la classe correspondante (Turret, Wall, etc.)
        # Si le type spécifique n'existe pas, on prend la classe Building de base
        build_class = Building.BUILDING_TYPES.get(type_name, Building)
        gx, gy = self.game.grid.get_cell_pos(pos.x, pos.y)
        wx = gx * self.game.st.CELL_SIZE
        wy = gy * self.game.st.CELL_SIZE

        # --- LOGIQUE DE POOLING ---
        recycled_build = None
        for b in self.entities:
            if not b.active and isinstance(b, build_class):
                recycled_build = b
                break

        if recycled_build:
            recycled_build.spawn(wx, wy, uid=f"{type_name}_{id(recycled_build)}")
            # On pourrait avoir besoin de rafraîchir les stats si le bâtiment a été amélioré entre-temps
            recycled_build.data = data 
            build = recycled_build

        else:
            # Nouveau bâtiment
            build = build_class(wx, wy, data, self.game, uid=f"{type_name}_{len(self.entities)}")
            self.entities.append(build)

        # Ajout dans la camera pour le rendu
        self.game.sceneManager.main_camera.add_entity(build)

        # Mise à jour du monde
        build.grid_pos = self.game.grid.add_building(pos.x, pos.y, build)
        self.game.grid.set_entity_chunk(build)
        # print(self.game.grid.get_cell_pos(pos.x, pos.y))

        # On met à jour le chemin des ennemis vers le Kernel
        self.game.grid.update_flow_field(self.game.kernel.pos)

        # Mise a jour des building autour (ex: mur)
        self.check_buildings(build)


    def handle_event(self, event) -> bool:
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and not self.game.edit_mode:
                self.game.eventManager.publish("BUILD_MODE", True)
                return True
            
            if event.key == pygame.K_e and self.game.edit_mode:
                self.game.eventManager.publish("BUILD_MODE", False)
                return True

        # On inverse l'ordre pour la sélection (le dernier bâti est "au dessus")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # IMPORTANT : Les bâtiments utilisent get_screen_rect() dans leur handle_event
            # On délègue la vérification de collision aux entités elles-mêmes
            for build in reversed(self.entities):
                if build.active and build.handle_event(event):
                    # Si un bâtiment a été sélectionné, on déselectionne le précédent
                    if self.selected_build and self.selected_build != build:
                        self.selected_build.deselect()
                    self.selected_build = build
                    self.game.eventManager.publish( "ELEMENT_SELECTED", build )
                    return True

            # Si on clique ailleurs, on déselectionne tout
            if self.selected_build:
                self.selected_build.deselect()
                self.selected_build = None
                self.game.eventManager.publish( "ELEMENT_UNSELECTED" )


        return False
    

    def check_buildings(self, build: Building, destroyed: bool=False) -> None:
        buildings_around = self.game.grid.get_neighbors_buildings(build)

        for side, building in buildings_around.items():
            if building.tag == "WALL":
                # Le côté pour le voisin est l'opposé du côté pour nous
                opposite_side = (-side[0], -side[1])

                # Si on détruit, on met False. Sinon True.
                building.config[opposite_side] = not destroyed
                building.update_look()

            # Si nous sommes un mur, on met à jour notre propre config
            if not destroyed and build.tag == "WALL":
                build.config[side] = True

        if build.tag == "WALL": 
            build.update_look()


    def clear_all(self):
        """ Désactive tous les bâtiments (pour le reset de partie) """
        for b in self.entities:
            b.kill() # Met active/visible à False
            # On la retire de la camera
            self.game.sceneManager.main_camera.remove_entity(b)

    
    def new_game(self):
        # cache tout les element et remetre le kernel sur l'ecran
        self.clear_all()
        self.game.sceneManager.main_camera.add_entity(self.game.kernel)
        self.game.kernel.reset()
