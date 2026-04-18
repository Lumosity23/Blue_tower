from .Building import Building
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class Wall(Building):
    
    _SIDES = {}

    @classmethod
    def get_sides_sprite(cls, game: "App") -> None:
        side = game.spriteManager.get_animation("anim_wall_sides", (32, 32), scaling=2)
        sides = game.st.DIRECTIONS_ALGO
        cls._SIDES = { sides[i]: side for i, side in side.items()}


    def __init__(self, x: int, y: int, data: dict, game: "App", uid):
    
        # Appel de la classe parent
        super().__init__(x, y, data, game, uid)
        self.tag = "WALL"
        
        self.config = { side : False for side in self._SIDES.keys()}


    def update_look(self):
        
        # On reset la surface de notre mur
        self.image = self.source_image.copy()

        # On ajoute les cote nessesaire au mur
        for s, val in self.config.items():
            if val :
                side = self._SIDES[s]
                self.image.blit(side, (0,0))


Wall.ui_config(
    ("ICON", "WALL", "image"),
    ("BAR", "Vie", "current_hp", "max_hp"),
    ("STAT", "CHUNK", "chunk")
)