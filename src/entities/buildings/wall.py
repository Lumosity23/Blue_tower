from .Building import Building
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App



class Wall(Building):
    
    def __init__(self, x: int, y: int, game: "App"):
        
        # Appel de la classe parent
        super().__init__(x, y, game)

        self.type = self.game.st.WALL
        self.image = self.game.spriteManager.get_custom_sprite(self.game.st.WALL, (self.game.st.CELL_SIZE, self.game.st.CELL_SIZE))
        self.source_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_hp = self.game.st.WALL_HP
        self.current_hp = self.max_hp
        self.cost = self.game.st.TYPE_COST[self.type]