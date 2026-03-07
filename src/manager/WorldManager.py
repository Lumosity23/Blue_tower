import pygame
from grid import Grid
from TileMap import TileMap
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class WorldManager:

    def __init__(self, game: "App"):
        
        self.game = game
        self.grid = Grid(game)
        self.TileMap = TileMap(game)
        
        # Ecoute l'event de NEW_GAME
        self.game.eventManager.subscribe( "NEW_GAME", self.generate_new_world )


    def generate_new_world( self ) -> None:

        # On reinitialise notre grid
        self.grid.restart()
