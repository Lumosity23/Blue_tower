import json
from ui.UIPanel import UIPanel
from ui import UIProgressBar, UIDot, UIStat, UIIcon
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    from entities.Entity import Entity
    from UIElement import UIElement


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
        self.ui_pool = {}
        self.amount_ui_elements: dict[str, list[int, "UIElement"]] = {
            "icon" : [1, UIIcon.UIIcon],
            "bar"  : [5, UIProgressBar.UIProgressBar],
            "dot"  : [3, UIDot.UIDot],
            "stat" : [4, UIStat.UIStat]
        }
        self.init_pool_child()

        # Souscription
        self.game.eventManager.subscribe( "ELEMENT_SELECTED", self.show_element )
        self.game.eventManager.subscribe( "ELEMENT_UNSELECTED", self.kill )     
    

    def init_pool_child( self ) -> None:
        for uielement, numAndClass in self.amount_ui_elements.items():
            num, cls = numAndClass
            self.ui_pool[uielement] = []
            for _ in range(num):
                element: "UIElement" = cls( 0, 0 )
                element.active = False
                self.ui_pool[uielement].append(element)
        

    def show_element( self, entity: "Entity" ) -> None:

        self.game.eventManager.publish( "CLOSE_SHOP" )
        # self.make_data(entity)
        
        super().show()
    
    
    def reset_data_child( self ) -> None:

        for child in self.children:
            child.active = False
            self.remove_child(child)


    def make_data(self, entity: "Entity") -> None:
        
        # Setup de notre nouvelle entite
        self.reset_data_child()
        self.current_entity = entity

        if entity.tag in self.schemas:
            entity_schema = self.schemas.get(entity.tag)
        else: return

        for item in entity_schema:
            # Recupere un element correspondant encore non utiliser
            for e in self.ui_pool[item["type"]]:
                if not e.active:
                    element = e
                    element.active = True
                    self.add_child(element)
            





        

        