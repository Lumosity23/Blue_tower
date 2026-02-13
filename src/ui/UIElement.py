import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

class UIElement:

    def __init__(self, x: int, y: int, w: int, h: int, game: "App", uid: str=None):
        '''
            un element de UI requiert toute ses dimentsion : (x, y) et W and H\n
            et ensuie l'instance du jeu : game et si il est un enfant (children)\n
            alors il dois donner l'instance de son parent
        '''
        self.uid = uid
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.absolute_rect = None
        self.pos = pygame.math.Vector2(x, y)
        self.start_pos = self.pos.copy()
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 100, 100))

        # Par defaut l'image est invisible
        self.image.set_alpha(0)

        self.visible: bool = True
        self.parent: "UIElement" = None
        self.children = []
        
        # Pour l'animation
        self.target: tuple = None
        self.speed: int = 300 # Pixel par secondes (rapide)

    
    def home_position(self) -> None:
        '''
            Met a jour sa position init si self est un enfant
        '''
        self.absolute_rect = self.get_absolute_rect()


    def add_child(self, new_child: "UIElement") -> None:
        '''
            Ajout d'un enfant a la liste du parent
        '''
        self.children.append(new_child)
        new_child.parent = self # Definition du lien de parente
        new_child.home_position()

    
    def get_absolute_rect(self) -> pygame.Rect:
        '''
            permet de connaitre sa position absolue sur l'ecran
        '''
        abs_x = self.rect.x
        abs_y = self.rect.y

        current = self.parent
        while current is not None:
            abs_x += current.rect.x
            abs_y += current.rect.y
            current = current.parent

        return pygame.Rect(abs_x, abs_y, self.rect.width, self.rect.height)

    
    def update(self, dt) -> None:
        '''
            Pour pouvoir faire de l'animation (deplacement, disparition)
        '''
        if not self.visible: return

        if self.target:
            # Deplacement si pas encore arriver a destination
            tx, ty = self.target
            vec = pygame.math.Vector2(tx - self.rect.x, ty - self.rect.y)
            dist = vec.length()

            if dist > self.speed / 100:
                vec.normalize_ip()
                # On se deplace
                self.rect.x += vec.x * self.speed * dt
                self.rect.y += vec.y * self.speed * dt

            else:
                # On est arriver
                self.rect.x = tx
                self.rect.y = ty
                self.target = None
                
        # Propagation aux enfants
        child: "UIElement"
        for child in self.children:
            child.update(dt)
    

    def handle_event(self, event):
        """
        Renvoie True si l'événement a été traité par cet élément ou un enfant.
        """
        if not self.visible:
            return False

        # 1. On demande d'abord aux enfants (car ils sont dessines PAR DESSUS le parent)
        # On inverse la liste pour commencer par le dernier dessiné (celui tout en haut)
        child: UIElement
        for child in reversed(self.children):
            if child.handle_event(event):
                return True # L'événement a été mangé par un enfant
        
        return False # Personne n'a réagi
    

    def draw(self, surface: pygame.Surface):
        '''
            se dessiner sur la surface demander\n
            et dessine ses enfants juste apres si il y en a !
        ''' 
        # Verifier que l'element dois etre afficher
        if not self.visible:
            return
        
        abs_rect = self.get_absolute_rect()

        surface.blit(self.image, abs_rect)

        if self.children:
            child: "UIElement"
            for child in self.children:
                child.draw(surface)
    

    def reset_position(self) -> None:
        '''
            Remet a la position initial notre element
        '''
        #self.pos = self.start_pos.copy()
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.target = None


    def show(self) -> None:
        """
            Permet d'affcher l'ement sur l'ecran
        """
        self.visible = True
        self.reset_position()
        
        child: "UIElement"
        if self.children:
            for child in self.children:
                child.reset_position()


    def hide(self) -> None:
        '''
            Masque l'element de l'ecran et reinitialise sa position de depart
        '''
        self.visible = False