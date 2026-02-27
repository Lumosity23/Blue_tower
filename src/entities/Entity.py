import pygame


class Entity:

    def __init__(self, x: int, y: int, w: int, h: int, tag: str, uid: str | None) -> None:
        # ID de l'element
        self.uid = uid
        self.tag = tag

        # Position dans l'espace du niveau
        self.rect = pygame.Rect(x, y, w, h)
        self.pos = pygame.math.Vector2(x, y)

        # Surface de l'entite
        self.image = pygame.Surface((w, h))
        # self.flip_x = False

        # System de logic/rendu
        self.debug = False
        self.visible = True
        self.active = True
        self.alive = True

        # Composite Paterne
        self.parent: "Entity" = None
        self.children = []


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
        self.set_child("active", True)
        self.set_child("visible", True)


    def kill(self):
        ''' Détruit l'entité et ses enfants en se retirant de l'ecran '''
        self.visible = False
        self.active = False

        # On propage aussi la mort au enfants
        child: "Entity"
        for child in self.children:
            child.kill()
    

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

        # Propagation aux enfants
        for child in reversed(self.children):
            child: "Entity"
            if child.handle_event(event):
                return True
                
        return False # Personne n'a réagi
    

    def set_child(self, argument: str, state: bool=True) -> None:
        '''
            Passe un attribut de UIElement et permet de la set a tout le monde et a soi (ex : Debug)\n
            le state de l'attribut changer pour aller dans son oposse donc a utiliser avec prudence !\n
            ex : True -> False et inversement\n
            \n
            argument: attribut de UIElement bool en STR !\n
           state: l'etat dans le quel on veux aller
        '''
        # Verification que UIElement a bien cet attribut
        if hasattr(self, argument):
            # Verifier que l'attribut est un bien un bool
            if isinstance(getattr(self, argument), bool):    
                setattr(self, argument, state)
                # Recursion sur ses enfants
                child: "Entity"
                for child in self.children:
                    child.set_child(argument)


    def update(self, dt):
        if not self.visible: return

        # Syncronisation de la pos logic avec le rendu
        self.rect.topleft = round(self.pos.x), round(self.pos.y)

        # Logique de mouvement, IA, etc.
        child: "Entity"
        for child in self.children:
            child.update(dt)


################################################ DEBUG ########################################################
""" if self.debug:
    # Dessine un cadre vert neon autour de l'element lors du debug_mode
    pygame.draw.rect(surface, (57, 255, 20), screen_rect, 2) """
