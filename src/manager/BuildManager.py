from entities.buildings.Building import Building
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class BuildManager():

    def __init__(self, game: "App"):
        self.game = game
        self.build_maker = {}

    def attemp_build(self, MousPos, type: int) -> None:
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