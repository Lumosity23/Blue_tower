from entities.Camera import Camera
from entities.Cursor import Cursor
from manager.BuildManager import BuildManager
from manager.EntityManager import EntityManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    

class SceneManager:
    def __init__(self, game: "App"):
        self.game = game
        
        # 1. Le système de vue
        self.camera = Camera(game.st.SCREEN_WIDTH, game.st.SCREEN_HEIGHT)

        # 2. Les Managers de contenu (Leurs racines seront enfants de la caméra)
        self.buildManager = BuildManager(game)
        self.entityManager = EntityManager(game)
        
        # 3. Le Curseur de jeu (Pont entre UI et Monde)
        self.cursor = Cursor(game)
        
        # Montage de l'arbre nodal
        self.camera.add_child(self.buildManager.root)
        self.camera.add_child(self.entityManager.root)
        self.camera.add_child(self.cursor) # Le curseur suit aussi la caméra

    def update(self, dt):
        # On update la racine (Camera), ce qui update TOUT le monde récursivement
        self.camera.update(dt)

    def draw(self, screen):
        """ 
        C'est ici qu'on gère le rendu global du monde physique.
        """
        """ # On récupère toutes les entités actives des deux managers
        # pour faire un Z-Sorting global (un ennemi peut passer derrière une tour)
        render_list = self.entityManager.get_active_entities() + self.buildManager.entities
        
        # Tri par le bas (Perspective 2D)
        for entity in sorted(render_list, key=lambda e: e.rect.bottom):
            entity.draw(screen)
            
        # On dessine le curseur en dernier (toujours par dessus le monde)
        self.cursor.draw(screen) """
        self.camera.draw(screen)


    def handle_event(self, event):
        # 1. On donne d'abord l'event au Curseur (pour la pose de bâtiments)
        if self.cursor.handle_event(event):
            return True
            
        # 2. Puis au BuildManager (pour la sélection de bâtiments existants)
        if self.buildManager.handle_event(event):
            return True
            
        # 3. Puis aux entités si besoin (clic sur ennemi, etc.)
        if self.camera.handle_event(event):
            return True
            
        return False