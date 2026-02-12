import pygame
from pygame.locals import *
from settings import Settings
from entities.player import Player
from entities.bullet import Bullet
from manager.WaveManager import WaveManager
from manager.UIManager import UIManager
from manager.CollideManager import CollideManager
from entities.Cursor import Cursor
from grid import Grid
from entities.kernel import Kernel
from manager.WalletManager import WalletManager
from manager.EventManager import EventManager
from manager.BuildManager import BuildManager
from ui.UIElement import UIElement


class App:

    # initialise les variable important pour pygame
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.clock = pygame.time.Clock()
        self.st = Settings()
        self.size = self.width, self.height  = self.st.SCREEN_WIDTH, self.st.SCREEN_HEIGHT
    

    # on initialise pygame et tout les object utile pour le jeu
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.eventManager = EventManager()
        self.wave_manager = WaveManager(self)
        self.ui_manager = UIManager(self)
        self.collider = CollideManager(self)
        self.buildManager = BuildManager(self)
        self.kernel = Kernel(self)
        self.grid = Grid(self)
        self.cursor = Cursor(self)
        self.mode = "EASY"
        self.walletManager = WalletManager(self)
        self.all_sprites = pygame.sprite.Group()
        self.builds = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player, self.kernel)
        self._running = True
        self.game_over = False
        self.edit = False
        self.debug = False
        self.last_time_shoot = - self.st.BULLET_COOLDOWN
        
        # Test
        self.root_panel = UIElement(self.st.ROOT_PANEL_POS[0], self.st.ROOT_PANEL_POS[1], self.st.ROOT_PANEL_SIZE[0], self.st.ROOT_PANEL_SIZE[1])
        self.root_panel.image.fill((50, 50, 50)) # Gris foncé

        # 2. Création de l'ENFANT (Bouton Rouge)
        # Position 10, 10 DANS LE PARENT (donc 110, 110 sur l'écran)
        self.red_button = UIElement(10, 10, 50, 50)
        self.red_button.image.fill((255, 0, 0)) # Rouge
    
        # 3. LIAISON
        self.root_panel.add_child(self.red_button)
        self.root_panel.visible = False
        self.root_panel.speed = 1500

    # Boucle qui va recupree les event
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        # Tir d'un projectile    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            m1, m2, m3 = pygame.mouse.get_pressed()
            if m1:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_time_shoot > self.st.BULLET_COOLDOWN:
                    # Creation d'un projectile si clic de souris
                    bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, target_pos=pygame.mouse.get_pos())
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                    self.last_time_shoot = current_time
            # Systeme de build        
            if self.edit:
                # Creation d'un mur
                if m3 and self.cursor.cell_isOccupied == False:
                    self.buildManager.attemp_build(pygame.mouse.get_pos(), self.st.WALL)
        # Restart
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                if self.game_over:
                    self.game_over = False
                    self.start_game()
                    print("restart")
            if event.key == pygame.K_e:
                self.edit = not self.edit
                if not self.edit:
                    self.all_sprites.remove(self.cursor)
                    self.debug = False
            if event.key == pygame.K_p and self.edit:
                self.debug = not self.debug

            if self.edit:
                # Creation de la tourelle
                if event.key == pygame.K_t and self.cursor.cell_isOccupied == False:
                    self.buildManager.attemp_build(pygame.mouse.get_pos(), self.st.TURRET)

            if event.key == pygame.K_g:
                if self.root_panel.visible:
                    self.root_panel.hide()
                else:
                    self.root_panel.show()

    # la logic et tout le reste se trouve ici dans la boucle
    def on_loop(self, dt):
        
        # GAME OVER
        if self.game_over:
            pass
        
        else:
            # Met a jour les point de vie des elements sur le terrain
            # Balles -> Ennemis
            self.collider.check_collisions(self.bullets, self.enemies, False, False)

            # Joueur -> Ennemis
            self.collider.check_collisions(self.player, self.enemies, False, False)

            # Kernel -> Ennemis
            self.collider.check_collisions(self.kernel, self.enemies, False, False)

            # On appel la methode update de tout les object dans "all_sprites"
            self.all_sprites.update(dt) 
            self.wave_manager.update()
            self.root_panel.update(dt)

            # Verifier si le joueur est toujours en vie
            if not self.player.alive or not self.kernel.alive:
                self.game_over = True


    # Affichage et autre rendu visuel
    def on_render(self):
        
        # ECRAN NOIRE
        self._display_surf.fill((0,0,0)) 
        
        # GAME OVER
        if self.game_over:
            # ICI meca de fin de game
            self.ui_manager.draw_text(self._display_surf, "GAME OVER", self.st.SCREEN_WIDTH / 2, self.st.SCREEN_HEIGHT / 2, (255, 0, 0), 'center')
            self.ui_manager.draw_text(self._display_surf, "clic SPACE or R for restart", self.st.SCREEN_WIDTH / 2, self.st.SCREEN_HEIGHT / 2 + 50, (255,255,255), 'center')

        else:
            # Affichage de la grille lors d'edit
            if self.edit:
                self.grid.draw(self._display_surf)
                self.all_sprites.add(self.cursor)
                
                if self.debug:
                    for cell_pos, cell_val in self.grid.flow_field.items():
                        length = len(str(cell_val)) * 26
                        decalage = (self.st.CELL_SIZE - length) // 2
                        cx = cell_pos[0] * self.st.CELL_SIZE + decalage
                        cy = cell_pos[1] * self.st.CELL_SIZE + 7
                        self.ui_manager.draw_text(self._display_surf, str(cell_val), cx, cy)

            self.all_sprites.draw(self._display_surf) # DRAW sprite.image (self.image)
            # Dessiner la bar de vie de ennemis
            for enemy in self.enemies:
                self.ui_manager.draw_health_bar(enemy, self._display_surf)
            self.ui_manager.draw_health_bar(self.player, self._display_surf)
            self.ui_manager.draw_health_bar(self.kernel, self._display_surf, self.st.SCREEN_WIDTH / 2, self.st.SCREEN_HEIGHT - self.st.CELL_SIZE, (600, 32))

            # Affichage du text
            # Nombre de vague
            self.ui_manager.draw_text(self._display_surf, f"Wave {self.wave_manager.wave_number}", Settings.SCREEN_WIDTH / 2, 50, (255,255,255), 'center')
            # Nombre d'ennemis qui restent
            self.ui_manager.draw_text(self._display_surf, str(len(self.enemies)), self.st.SCREEN_WIDTH - 50, 60, (255,255,255), 'topright')
            # Nombre de FPS
            self.ui_manager.draw_text(self._display_surf, str(int(self.clock.get_fps())), 10, 0, (255,255,255))
            # Wallet
            money = str(self.walletManager.get_wallet_val())
            if self.walletManager.creatif:
                money = "CREATIF"
            self.ui_manager.draw_text(self._display_surf, money, self.st.SCREEN_WIDTH - 50, 20, (255,255,255), 'topright')
            # self.ui_manager.draw_text(self._display_surf, str(len(self.ui_manager.cache_text)), self.st.SCREEN_WIDTH - 100, self.st.SCREEN_HEIGHT - 100, (255,255,255), 'topright')

            # Test de UIElement
            self.root_panel.draw(self._display_surf)

        pygame.display.flip() # METRE AJOUR L'ECRAN PHYSIQUE


    def start_game(self):
        # Reinitialiser le manager et les entite unique via l'event "RESTART_GAME"
        self.eventManager.publish("RESTART_GAME",data=None)

        # Test UIElement
        self.root_panel.rect.x = self.st.ROOT_PANEL_POS[0]
        self.root_panel.rect.y = self.st.ROOT_PANEL_POS[1]

        # Vider les groupes de logic et rendu
        self.enemies.empty()
        self.bullets.empty()
        self.all_sprites.empty()
        self.builds.empty()

        # Rajout du player dans le rendu
        self.all_sprites.add(self.player, self.kernel)

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
 