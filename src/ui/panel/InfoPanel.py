from ui.UIPanel import UIPanel
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class InfoPanel( UIPanel ):

    def __init__( self, game: "App" ):
        
        self.game = game
        w, h = 400, game.st.SCREEN_HEIGHT
        self.size = w, h

        super().__init__( game.st.SCREEN_WIDTH, 0, w, h, uid="InfoPanel" )

        self.set_label("INFO", 200)
        self.set_animation( (self.game.st.SCREEN_WIDTH - self.size[0], 0), (self.game.st.SCREEN_WIDTH, 0), 1000 )
        self.visible = False

        # Souscription
        self.game.eventManager.subscribe( "ELEMENT_SELECTED", self.show_element )
        self.game.eventManager.subscribe( "ELEMENT_UNSELECTED", self.kill )     
    

    def show_element( self, data: dict ) -> None:

        # print(len(data))

        super().show()