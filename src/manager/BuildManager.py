import pygame
from entities.buildings.Building import Building
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class BuildManager():

    def __init__(self, game: "App"):
        self.game = game
        self.selected_build: Building | None = None
        self.build_maker = {}

    def attemp_build(self, MousPos, type: str) -> None:
        '''
            permet de construir un batiment a la position donnee
        '''
        cost = self.game.st.TYPE_COST[type]
        mx, my = MousPos
        if self.game.grid.get_cell_isOccupied(mx, my):
            '''
                renvoier une erreur
            '''
            self.game.eventManager.publish("ERROR_SOUND")
            return
        
        if not self.game.walletManager.buy(cost):
            '''
                veirfie que on a asser d'argent
            '''
            self.game.eventManager.publish("ERROR_PAYMENT")
            return
        
        self.make_building(type, MousPos)
        self.game.eventManager.publish("BUILD_ITEM", type)
        

    def make_building(self, type_name, mp):

        if type_name in Building.BUILDING_TYPES:

            build_class = Building.BUILDING_TYPES[type_name] 
            
            # MousPos
            mx, my = mp

            # CellPos
            x, y  = self.game.grid.get_cell_pos(mx, my)

            px = x * self.game.st.CELL_SIZE
            py = y * self.game.st.CELL_SIZE

            # Making the building with the classe approriate
            build = build_class(px, py, self.game)

            self.game.builds.add(build)
            self.game.all_sprites.add(build)
            self.game.grid.set_cell_value(mx, my, type_name)
            self.game.grid.update_flow_field(self.game.kernel.rect.center)
        
        else:
            print(f"ce type de batiment n'exite pas dans mon repertoire : {type_name}")
    
    
    def handle_event(self, event) -> bool:
        # Voir si un batiment a manger l'event
        
        if self.game.edit:
            button = 1
        else: button = 3

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == button:
            # On check si on a cliquer sur un batiments
            build: "Building"
            clicked_build = None
            for build in self.game.builds:
                if build.rect.collidepoint(event.pos):
                    clicked_build = build
                    break
            
            # Si batiment a intersepter le clic
            if clicked_build:
                if self.selected_build:
                    self.selected_build.deselect()
                # On selectionne le nouveau batiment
                self.selected_build = clicked_build
                self.selected_build.select()
                return True

            # Si clique dans le vide -> deselection du seleted_build
            else:
                if self.selected_build:
                    self.selected_build.deselect()
                    self.selected_build = None
            
        for build in self.game.builds:
            build.handle_event(event)
        
        return False