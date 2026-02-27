from entities.Camera import Camera
from entities.Cursor import Cursor
from entities.Entity import Entity
from manager.BuildManager import BuildManager
from manager.EntityManager import EntityManager
from manager.WaveManager import WaveManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    

class SceneManager:
    def __init__(self, game: "App"):
        self.game = game
        
        # 1. Le système de vue
        self.main_camera = Camera(game.st.SCREEN_WIDTH, game.st.SCREEN_HEIGHT)

        # 2. Les Managers de contenu (Leurs racines seront enfants de la caméra)
        self.buildManager = BuildManager(game)
        self.entityManager = EntityManager(game)
        self.waveManager = WaveManager(game)

        # 3. Le Curseur de jeu (Pont entre UI et Monde)
        self.cursor = Cursor(game)


    def update(self, dt):

        # On update les different managers
        self.entityManager.update(dt)
        self.buildManager.update(dt)
        self.waveManager.update()
        self.cursor.update(dt)

        # Update la camera pour l'offset
        self.main_camera.update(dt)


    def draw(self, screen):
        """ 
        C'est ici qu'on gère le rendu global du monde physique.
        """
        # La camera dessine tout les entites active
        self.main_camera.draw(screen)

        # On dessine le curseur en dernier (toujours par dessus le monde)
        self.cursor.draw(screen)


    def handle_event(self, event):
        # 1. On donne d'abord l'event au Curseur (pour la pose de bâtiments)
        if self.cursor.handle_event(event):
            return True
            
        # 2. Puis au BuildManager (pour la sélection de bâtiments existants)
        if self.buildManager.handle_event(event):
            return True
        
        if self.game.player.handle_event(event):
            return True
        
        return False