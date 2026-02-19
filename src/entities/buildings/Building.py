import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class Building(pygame.sprite.Sprite):

    BUILDING_TYPES = {}

    def __init_subclass__(cls, **kargs):
        super().__init_subclass__(**kargs)
        
        # Nom de la classe enfants en maj
        # Enregistrement de la classe dans le dico
        cls.BUILDING_TYPES[cls.__name__.upper()] = cls


    def __init__(self, x, y, game: "App"):
        super().__init__()
        self.game = game
        self.pos = x, y
        self.is_selected = False
        self.state = "IDLE"

        # Valeur par defaut pour le building
        self.image = pygame.Surface((self.game.st.CELL_SIZE, self.game.st.CELL_SIZE))
        self.image.fill((255, 0, 255))
        self.source_image = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.cost = 25
    

    def handle_event(self, event) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        # Gestion du Survol
        if event.type == pygame.MOUSEMOTION:
            # On ne perd pas l'état SELECTED si on bouge la souris
            if self.state != "SELECTED":
                new_state = "HOVER" if is_hovered else "IDLE"
                # Si changement d'etat
                if new_state != self.state:
                    self.state = new_state
                    self.update_appearance()

    
    def select(self) -> None:
        ''' Appele par le Buildmanager '''
        self.state = "SELECTED"
        self.game.eventManager.publish("BUILDING_SELECTED", self)
        self.update_appearance()

    
    def deselect(self) -> None:
        ''' Appeler par le Buildmanager '''
        self.state = "IDLE"
        self.update_appearance()


    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.die()
    

    def die(self):
        self.kill()

    
    def update_appearance(self):
        """ Recrée l'image à partir de la source et ajoute les effets """
        # 1. Reset l'image
        self.image = self.source_image.copy()

        # 2. Si cliqué : Contour blanc
        if self.state == "SELECTED":
            # On dessine un rectangle blanc sur tout le tour
            pygame.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 2)

        # 3. Si survolé ou clique : Barre de vie
        if self.state == "HOVER" or self.state == "SELECTED":
            self.game.spriteManager.draw_health_bar(self, self.image, self.rect.w / 2, self.rect.h / 2, (self.rect.w - 20, 10))