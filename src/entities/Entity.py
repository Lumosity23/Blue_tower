import pygame
from manager.EventManager import EventManager
from manager.SpriteManager import SpriteManager


class Entity:

    @classmethod
    def get_eventBus(cls, eventBus: "EventManager"):
        cls._EVENTBUS = eventBus
    
    @classmethod
    def get_spriteManager(cls, spriteManager: "SpriteManager"):
        cls._SPRITE = spriteManager


    def __init__(self, x: int, y: int, w: int, h: int, tag: str, uid: str | None) -> None:
        # ID de l'element
        self.uid: str = uid
        self.tag: str = tag
        self.type = "ENTITY"

        # Position dans l'espace du niveau
        self.rect = pygame.Rect(x, y, w, h)
        self.pos = pygame.math.Vector2(x, y)
        self.chunk = None
        self.old_chunk = None

        # Surface de l'entite
        self.image = pygame.Surface((w, h)) # <------ A ne PLUS UTILISER
        self.animations: dict[str, dict[tuple[int], pygame.Surface]] = {}
        self.current_state = "None"
        self.state = "None"
        self.anim_timer = 0.0
        self.anim_size = 0
        self.anim_duration = 0.0
        self.frame_duration = 0.0
        self.frame_index = 0
        # self.flip_x = False

        # System de logic/rendu
        self.debug = False
        self.visible = True
        self.active = True
        self.alive = True
        self.selected = False
        self.chunk_changed = False
        self.kills = 0

        # Composite Paterne
        self.parent: "Entity" = None
        self.children = []

        # States de bases
        self.max_hp = 1
        self.current_hp = self.max_hp

        # Systeme de delay
        self.timers = {}

    @property
    def img(self):
        return self.current_anim["ANIMATION"][self.frame_index]
    

    def set_anim(self, anim_name: str, rect_size: tuple[int, int], duration: float, scaling: int=1) -> None:
        """ Configure une animation depuis une spritesheet """
        name = f'anim_{self.__class__.__name__}_{anim_name}'
        animation = self._SPRITE.get_animation(name.lower(), rect_size, scaling=scaling)
        self.animations[anim_name] = {
            "ANIMATION" : animation,
            "DURATION"  : duration
            }
        print(f"Animation {anim_name} de {self.__class__.__name__} a bien ete charger")
        #print(self.animations)


    def update_animation(self, dt, new_anim) -> None:

        if new_anim != self.current_state:
                self.anim_timer = 0.0
                self.frame_index = 0
                self.current_state = new_anim
                self.current_anim = self.animations[new_anim]
                self.rect = self.img.get_rect()
                self.rect.topleft = self.pos.xy
                self.anim_duration = self.current_anim["DURATION"]
                self.anim_size = len(self.current_anim["ANIMATION"])
                self.frame_duration = self.anim_duration / self.anim_size
        
        self.anim_timer += dt
        self.anim_timer %= self.anim_duration
        
        # On recupere la current frame et securise si on out of range
        self.frame_index = min(self.anim_size , int(self.anim_timer / self.frame_duration))
        

    def add_child(self, new_child: "Entity") -> None:
        if new_child not in self.children:
            self.children.append(new_child)
            new_child.parent = self
    

    def remove_child(self, child: "Entity") -> None:
        if child in self.children:
            self.children.remove(child)
            child.parent = None
        
    
    def spawn(self, x, y, uid=None, **kwargs):
        ''' Réactive l'entité et la place à une nouvelle position '''
        self.pos.update(x, y)
        self.rect.topleft = (x, y)
        self.uid = uid
        self.set_child("active", True)
        self.set_child("visible", True)
        self.set_child("alive", True)
        if hasattr(self, "hp_bar"):
            self.hp_bar.visible = False
            

    def kill(self):
        ''' Détruit l'entité et ses enfants en se retirant de l'ecran '''
        self.visible = False
        self.active = False
        # self.alive = False

        # On propage aussi la mort au enfants
        child: "Entity"
        for child in self.children:
            child.kill()
    

    def increment_kills(self):
        self.kills += 1
    

    def take_damage(self, amount: int) -> None:
        
        mapping = {
            "xy" : self.rect.center,
            "text" : amount
        }

        self._EVENTBUS.publish("SHOW_FT", mapping)

        self.current_hp -= amount

        if self.current_hp <= 0:
            self.alive = False
            self.kill()
            return True
    

    def kick(self, entity: "Entity", amount: int) -> None:

        if entity.take_damage(amount):
            self.increment_kills()
    

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
        # Verification que Entity a bien cet attribut
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
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        # Logique de mouvement, IA, etc.
        child: "Entity"
        for child in self.children:
            child.update(dt)


    def delay(self, time_s, dt) -> bool:
        ''' Renvoie si le temps voulu est passe '''
        if time_s in self.timers:
            self.timers[time_s] += dt
            if self.timers[time_s] >= time_s:
                self.timers[time_s] = 0
                return True
            return False
        
        else :
            self.timers[time_s] = dt
            return False
        

    @classmethod
    def ui_config(cls, *elements):
        """
        Example :\n
        Entity.ui_config(
            ("Element", "label", "mapping*"),\n
            (...),\n
            ("lastElement", "label", "mapping*")\n
        )\n

        MAPPING ->\n
            "BAR"  : ["current", "max"]\n
            "STAT" : ["string"]\n
            "BOOL" : ["state"]\n
            "ICON" : ["icon_id"]\n


        La passerelle : elle prend des tuples (Type, Label, Map1, Map2...)
        et les envoie au configurateur.\n
        elements: (Type, Lable, Map1, Map2...)
        """
        from utils.ui_config import save_entity_schema # Import local pour éviter les cercles
        
        # On passe juste le nom de la classe et les données brutes
        save_entity_schema(name=cls.__name__.upper(), raw_data=elements)


    @classmethod
    def upgrade_config(cls, *element):
        """ 
        label = str(NAME of the UPGRADE)\n
        mapping = "CURRENT", "MAX", "PRICE", "RATE"\n

        use --> upgrade_config(label, *mapping)
        """

        from utils.upgrade_config import save_entity_upgrade

        save_entity_upgrade(name=cls.__name__.upper(), raw_data=element)


    @property
    def __name__():
        ''' Permet de retourner le nom de la classe de notre entity'''
        return __class__.__name__()


################################################ DEBUG ########################################################
""" if self.debug:
    # Dessine un cadre vert neon autour de l'element lors du debug_mode
    pygame.draw.rect(surface, (57, 255, 20), screen_rect, 2) """
