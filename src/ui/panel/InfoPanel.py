import json
from ui.UIPanel import UIPanel
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    from entities.Entity import Entity


class InfoPanel( UIPanel ):

    def __init__( self, game: "App" ):

        self.game = game
        w, h = 400, game.st.SCREEN_HEIGHT
        self.size = w, h

        # Dans ton UIManager ou InfoPanel
        with open( self.game.st.UI_SCHEMA_PATH, 'r') as f:
            self.schemas: dict[dict] = json.load(f)

        super().__init__( game.st.SCREEN_WIDTH, 0, w, h, uid="InfoPanel" )

        self.set_label("INFO", 200)
        self.set_animation( (self.game.st.SCREEN_WIDTH - self.size[0], 0), (self.game.st.SCREEN_WIDTH, 0), 1000 )
        self.visible = False

        # Entity INFO
        self.current_entity: Entity = None
        self.amount_ui_elements = {
            "icon" : 1,
            "bar"  : 5,
            "dot" : 3,
            "stat" : 4,
        }

        # Souscription
        self.game.eventManager.subscribe( "ELEMENT_SELECTED", self.show_element )
        self.game.eventManager.subscribe( "ELEMENT_UNSELECTED", self.kill )     
    

    def init_pool_child( self ) -> None:

        pass


    def show_element( self, entity: "Entity" ) -> None:

        self.game.eventManager.publish( "CLOSE_SHOP" )
        # self.make_data(entity)

        super().show()
    
    
    def reset_data_child( self ) -> None:

        for child in self.data_children:
            self.remove_child(child)


    def make_data(self, entity: "Entity") -> None:
        
        # Setup de notre nouvelle entite
        self.reset_data_child()
        self.current_entity = entity

        if entity.tag in self.schemas:
            entity_schema = self.schemas.get(entity.tag)
        else: return

        for item in entity_schema:
            # 1. Trouver la classe correspondante dans le registre
            ui_class = item["ui_class"]






        

        