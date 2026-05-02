from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from manager.EventManager import EventManager
    from manager.SaveManager import SaveManager
    from manager.SpriteManager import SpriteManager


class UIElement:
    # 1. LA VARIABLE PARTAGÉE (Dictionnaire vide au début)
    # Elle appartient à la classe, pas aux objets individuels.
    _LAYOUT_CACHE = {}
    _EVENTBUS = None

    # 2. MÉTHODE POUR REMPLIR LE CACHE (Appelée par le Manager)
    @classmethod
    def load_layout_cache(cls, data: dict):
        cls._LAYOUT_CACHE = data
        if data:
            print("💾 UIElement : Configuration Layout chargée !")
        else:
            print(" Erreur lors du chargement du fichier de configuration !")

    @classmethod
    def get_eventBus(cls, eventBus: "EventManager"):
        cls._EVENTBUS = eventBus

    @classmethod
    def get_spriteManager(cls, SpriteManager: "SpriteManager"):
        cls._SPRITE = SpriteManager

    @classmethod
    def get_save(cls, SaveManager: "SaveManager"):
        cls._SAVE = SaveManager

    def __init__(self, x: int, y: int, w: int, h: int, uid: str | None = None):
        """
        un element de UI requiert toute ses dimentsion : (x, y) et W and H\n
        et ensuie l'instance du jeu : game et si il est un enfant (children)\n
        alors il dois donner l'instance de son parent
        """
        self.uid = uid
        self.scroll_offset = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, w, h)
        self.cfg_loaded = False
        # 3. AUTO-CONFIGURATION SANS 'GAME'
        # On regarde directement dans la variable de classe
        if self.uid and self.uid in UIElement._LAYOUT_CACHE:
            cfg: dict = UIElement._LAYOUT_CACHE[self.uid]

            # On applique la config JSON (qui écrase les valeurs par défaut x,y,w,h)
            self.rect.x = cfg.get("x", x)
            self.rect.y = cfg.get("y", y)
            self.rect.width = cfg.get("w", w)
            self.rect.height = cfg.get("h", h)
            self.cfg_loaded = True
            # print(f'| LOG LAYOUT | : Layout applique a : {self.uid}')
        # else: print(f"Erruer lors du load ! : {self.__class__.__name__} | {self.uid if self.uid else None}")

        self.absolute_rect = None
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.start_pos = self.pos.copy()

        # Par defaut l'image est invisible
        self.image = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)

        self.debug = False
        self.visible: bool = True
        self.active: bool = True
        self.type: str = "element"
        self.parent: "UIElement" = None
        self.children: list["UIElement"] = []

        # Pour l'animation
        self.target: tuple = None
        self.speed: int = 300  # Pixel par secondes (rapide)
        self.bouncing: bool = False
        self.start_pos = x, y
        self.end_pos = None

    def home_position(self) -> None:
        """
        Met a jour sa position init si self est un enfant
        """
        self.absolute_rect = self.get_screen_rect()

    def add_child(self, new_child: "UIElement") -> None:
        """
        Ajout d'un enfant a la liste du parent
        """
        self.children.append(new_child)
        new_child.parent = self  # Definition du lien de parente
        new_child.home_position()

    def remove_child(self, child: "UIElement") -> None:
        """Retire l'enfant voulue de la list de ces derniers"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def remove_all_child(self) -> None:
        """Permet de retirer tout les enfants actifs de soit"""
        for child in self.children:
            self.remove_child(child)

    def get_screen_rect(self) -> pygame.Rect:
        """permet de connaitre sa position absolue sur l'ecran"""
        abs_x = self.rect.x
        abs_y = self.rect.y

        current = self.parent
        while current is not None:
            abs_x += current.rect.x - current.scroll_offset.x
            abs_y += current.rect.y - current.scroll_offset.y
            current = current.parent

        return pygame.Rect(abs_x, abs_y, self.rect.width, self.rect.height)

    def get_size(self) -> pygame.Rect:
        # On commence par la position absolue de l'élément actuel
        total_rect = self.get_screen_rect()

        for child in self.children:
            # On fusionne avec le rectangle total (écran) de chaque enfant
            total_rect.union_ip(child.get_size())

        return total_rect

    def update(self, dt) -> None:
        """
        Pour pouvoir faire de l'animation (deplacement, disparition)
        """
        if not self.visible:
            return

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

    def handle_event(self, event) -> bool:
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
                return True  # L'événement a été mangé par un enfant

        return False  # Personne n'a réagi

    def set_child(self, argument: str, own: bool = True) -> None:
        """
        Passe un attribut de UIElement et permet de la set a tout le monde et a soi (ex : Debug)\n
        le state de l'attribut changer pour aller dans son oposse donc a utiliser avec prudence !\n
        ex : True -> False et inversement\n
        \n
        argument: attribut de UIElement bool en STR !\n
        own: si on veux que soit-meme soit aussi affecter
        """
        # Verification que UIElement a bien cet attribut
        if hasattr(self, argument):
            # Verifier que l'attribut est un bien un bool
            if type(getattr(self, argument)) == bool:
                if own:
                    current_val = getattr(self, argument)
                    setattr(self, argument, not current_val)
                # Recursion sur ses enfants
                if self.children:
                    child: "UIElement"
                    for child in self.children:
                        child.set_child(argument)

    def draw(self, surface: pygame.Surface):
        """
        se dessiner sur la surface demander\n
        et dessine ses enfants juste apres si il y en a !
        """
        # Verifier que l'element dois etre afficher
        if not self.visible:
            return

        abs_rect = self.get_screen_rect()
        surface.blit(self.image, abs_rect)

        if self.debug:
            # Dessine un cadre rose autour de l'element lors de l'edit_mode
            pygame.draw.rect(surface, (255, 0, 255), abs_rect, 2)

        if self.children:
            child: "UIElement"
            for child in self.children:
                child.draw(surface)

    def reset_position(self) -> None:
        """
        Remet a la position initial notre element
        """
        # self.pos = self.start_pos.copy()
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.target = None

    def show(self) -> None:
        """
        Permet d'affcher l'ement sur l'ecran
        """
        self.visible = True
        if self.start_pos and self.end_pos:
            self.target = self.start_pos

        """ self.reset_position()

        child: "UIElement"
        if self.children:
            for child in self.children:
                child.reset_position() """

    def kill(self) -> None:
        """
        Masque l'element de l'ecran et reinitialise sa position de depart
        """
        if not self.end_pos:
            self.visible = False

        else:
            self.target = self.end_pos

    def set_animation(
        self,
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        speed: int = 300,
        bouncing: bool = False,
    ) -> None:

        self.bouncing = True
        self.speed = speed

        self.start_pos = start_pos
        self.end_pos = end_pos
