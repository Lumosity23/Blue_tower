import pygame


class Entity:

    def __init__(self, x: int, y: int, w: int, h: int, tag: str, uid: str | None) -> None:
        # ID de l'element
        self.uid = uid
        self.tag = None

        # Position dans l'espace du niveau
        self.rect = pygame.Rect(x, y, w, h)
        self.pos = pygame.math.Vector2(x, y)

        # Surface de l'entite
        self.image = pygame.Surface((w, h))
        self.flip_x = False

        # System de logic/rendu
        self.debug = False
        self.visible = True
        self.active = True

        # Composite Paterne
        self.parent: "Entity" = None
        self.children = []

        # Pour le Z-sorting (camera)
        self.z_index = 0


    def add_child(self, new_child: "Entity") -> None:
        if new_child not in self.children:
            self.children.append(new_child)
            new_child.parent = self
    

    def remove_child(self, child: "Entity") -> None:
        if child in self.children:
            self.children.remove(child)
            child.parent = None
        
    
    def spawn(self, x, y, uid=None):
        ''' Réactive l'entité et la place à une nouvelle position '''
        self.pos.update(x, y)
        self.rect.topleft = (x, y)
        self.uid = uid
        self.set_child("active", own=True)
        self.set_child("visible", own=True)


    def kill(self):
        ''' Détruit l'entité en se retirant de l'ecran '''
        self.visible = False
        self.active = False
    

    def increment_kills(self):
        self.kills += 1
        

    def get_screen_rect(self) -> pygame.Rect:
        """ 
        C'est l'équivalent de ton get_absolute_rect.
        Il transforme les coordonnées MONDE en coordonnées ÉCRAN.
        """
        abs_x, abs_y = self.rect.x, self.rect.y
        curr = self.parent
        while curr:
            abs_x += curr.rect.x
            abs_y += curr.rect.y
            curr = curr.parent
        return pygame.Rect(abs_x, abs_y, self.rect.w, self.rect.h)


    def handle_event(self, event) -> bool:
        if not self.visible: return False

        # Propagation aux enfants (ex: barre de vie cliquable ?)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Exemple d'interaction basique : détection du clic sur l'entité
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_screen_rect().collidepoint(event.pos):
                print(f"Entité cliquée : {self.uid}")
                return True
                
        return False # Personne n'a réagi
    

    def set_child(self, argument: str, own: bool=True) -> None:
        '''
            Passe un attribut de UIElement et permet de la set a tout le monde et a soi (ex : Debug)\n
            le state de l'attribut changer pour aller dans son oposse donc a utiliser avec prudence !\n
            ex : True -> False et inversement\n
            \n
            argument: attribut de UIElement bool en STR !\n
            own: si on veux que soit-meme soit aussi affecter
        '''
        # Verification que UIElement a bien cet attribut
        if hasattr(self, argument):
            # Verifier que l'attribut est un bien un bool
            if isinstance(getattr(self, argument), bool):
                if own:
                    setattr(self, argument, not getattr(self, argument))
                # Recursion sur ses enfants
                child: "Entity"
                for child in self.children:
                    child.set_child(argument)


    def update(self, dt):
        if not self.visible: return

        # Syncronisation de la pos logic avec le rendu
        self.rect.topleft = self.pos

        # Logique de mouvement, IA, etc.
        child: "Entity"
        for child in self.children:
            child.update(dt)


    def draw(self, surface: pygame.Surface):
        '''
            se dessiner sur la surface demander\n
            et dessine ses enfants juste apres si il y en a !
        ''' 
        # Verifier que l'element dois etre afficher
        if not self.visible: return
        
        screen_rect = self.get_screen_rect()

        if self.flip_x:
            # Gestion du Flip (regard gauche/droite)
            img = pygame.transform.flip(self.image, self.flip_x, False)
        else:
            img = self.image

        # Rendu sur l'ecran
        surface.blit(img, screen_rect)
    
        if self.debug:
            # Dessine un cadre rose autour de l'element lors de l'edit_mode
            pygame.draw.rect(surface, (57, 255, 20), screen_rect, 2)

        if self.children:
            child: "Entity"
            for child in self.children:
                child.draw(surface)