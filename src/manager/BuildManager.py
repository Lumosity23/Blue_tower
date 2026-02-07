from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class BuildManager():

    def __init__(self, game: "App"):
        self.game = game
        self.build_maker = {}

    def attemp_build(self, MousPos, type: int) -> None:
        '''
            permet de construir un batiement a la position donnee
        '''
        cost = self.game.st.TYPE_COST[type]

        if self.game.grid.get_cell_isOccupied():
            '''
                renvoier une erreur
            '''
            self.game.eventManager.publish("ERROR_SOUND")
            return
        
        if not self.game.wallet.buy(cost):
            '''
                veirfie que on a asser d'argent
            '''
            self.game.eventManager.publish("ERROR_PAYMENT")
            return
        
        self.make_building(self, type, MousPos)
        self.game.eventManager.publish("BUILD_ITEM", type)
        

    def make_building(self, type, mp):

        if type not in self.build_maker:
            self.build_maker[type] = self.game.st.CONSTRUCTOR 
