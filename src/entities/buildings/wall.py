from .Building import Building
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App



class Wall(Building):
    
    def __init__(self, x: int, y: int, data: dict, game: "App", uid):
        
        # Appel de la classe parent
        super().__init__(x, y, data, game, uid)
