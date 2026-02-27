import pygame
#from pygame.locals import *
from settings import Settings
from entities.player import Player
from manager.UIManager import UIManager
from grid import Grid
from entities.kernel import Kernel
from manager.WalletManager import WalletManager
from manager.EventManager import EventManager
from manager.SpriteManager import SpriteManager
from manager.SceneManager import SceneManager


class App:

    # initialise les variable important pour pygame
    def __init__(self):
        pygame.init()
        self._running = True
        self._display_surf = None
        self.clock = pygame.time.Clock()
        self.st = Settings()
        self.size = self.width, self.height  = self.st.SCREEN_WIDTH, self.st.SCREEN_HEIGHT
    

    # on initialise pygame et tout les object utile pour le jeu
    def on_init(self):

        # Init des composante de base de pygame
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('Blue Tower')

        # Variable d'etats
        self.mode = "EASY" # NORMAL, HARD, INSANE, DEMON
        self.state = "MENU" # PAUSE, GAME_OVER, PLAYING
        self.edit_mode = False

        # Init des differents composante du jeu
        self.eventManager = EventManager()
        self.spriteManager = SpriteManager(self)
        self.sceneManager = SceneManager(self)
        self.ui_manager = UIManager(self)
        self.walletManager = WalletManager(self)
        
        # Declaration des variables de base
        self.player = None
        self.kernel = None
        self.grid = Grid(self)

        # Init de HUD
        self.ui_manager.OSD.post_init()

        # Declaration des ecoute sur les event
        self.eventManager.subscribe("NEW_GAME", self.start_game)
        self.eventManager.subscribe("QUIT", self.quit)
        self.eventManager.subscribe("PAUSE", self.freeze)
        self.eventManager.subscribe("UNPAUSE", self.unfreeze)
        self.eventManager.subscribe("BUILD_MODE", self.edit)

        # Annonce le lancemeent du jeu avec le Menu
        self.eventManager.publish("MENU")

        return True
        

    # Boucle qui va recupree les event
    def on_event(self, event):
        # --- CHAÎNE DE PRIORITÉ DES INPUTS ---
        
        # 1. L'UI a la priorité absolue (ex: clic sur bouton pause)
        if self.ui_manager.handle_event(event):
            return

        # 2. Le monde de jeu (SceneManager gère le Cursor, le Build et le Player)
        if self.state == "PLAYING":
            if self.sceneManager.handle_event(event):
                return

        # 3. Événements système globaux
        if event.type == pygame.QUIT:
            self._running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.state == "PAUSE":
                self.eventManager.publish("UNPAUSE")
                return True
            
            if event.key == pygame.K_ESCAPE and self.state == "PLAYING":
                self.eventManager.publish("PAUSE")
                return True
            

    # la logic et tout le reste se trouve ici dans la boucle
    def on_loop(self, dt):
        
        if self.state == "PLAYING":
            # Le SceneManager s'occupe du tri Z-Sort et du dessin via la caméra
            self.sceneManager.update(dt)
        
            # Verifier si le joueur est toujours en vie
            if not self.player.alive or not self.kernel.alive:
                self.game_over = True
                self.eventManager.publish("GAME_OVER")
        
        self.ui_manager.root.update(dt)


    # Affichage et autre rendu visuel
    def on_render(self):
        self._display_surf.fill((10, 10, 10)) # Fond neutre
        
        if self.state == "PLAYING" or self.state == "PAUSE":
            if self.edit_mode:
                self.grid.draw(self._display_surf)
            # Le SceneManager s'occupe du tri Z-Sort et du dessin via la caméra
            self.sceneManager.draw(self._display_surf)

        # L'UI se dessine par-dessus tout
        self.ui_manager.root.draw(self._display_surf)
        
        pygame.display.flip()


    def start_game(self):
        # Reinitialiser le manager et les entite unique via l'event "RESTART_GAME"
        self.state = "PLAYING"
        self.game_over = False


    def quit(self) -> None:
        self._running = False


    def freeze(self) -> None:
        self.state = "PAUSE"

    def unfreeze(self) -> None:
        self.state = "PLAYING"

    def edit(self) -> None:
        self.edit_mode = not self.edit_mode


    def on_cleanup(self):
        # fermeture propre de pygame
        pygame.quit()
    

    # Boucle principal du jeu
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            # deltaTime (temps par frame)
            dt = self.clock.tick(60) / 1000
            self.on_loop(dt)

            self.on_render()
        self.on_cleanup()
 