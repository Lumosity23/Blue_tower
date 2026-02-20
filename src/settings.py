import pygame
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

@dataclass
class Settings:
    
    #### PLAYER ####
    PLAYER = "PLAYER"
    PLAYER_WIDTH: int = 22 * 2
    PLAYER_HEIGHT: int = 38 * 2
    PLAYER_HEALTH: int = 30
    PLAYER_SPRITE_PATH: str = 'assets/player.png'

    #### ENEMIE ####
    ENEMIE: str = "ENEMIE"
    ENEMIE_SIZE: Tuple[int, int] = (30,30)
    ENEMIE_HEALTH: int = 5 * 3
    ENEMIE_SPRITE_PATH: str = 'assets/enemie.png'
    
    #### KERNEL ####
    KERNEL = "KERNEL"
    KERNEL_SPRITE_PATH: str = 'assets/kernel.png'
    KERNEL_SIZE: int = 64 * 2
    KERNEL_HP: int = 40
    KERNEL_COOLDOWN: int = 1500

    #### WALL ####
    WALL_SPRITE_PATH: str = 'assets/wall_gab.png'
    WALL: str = "WALL"
    WALL_HP: int = 50
 
    #### TURRET ####
    TURRET_SPRITE_PATH: str = 'assets/turret.png'
    TURRET: str = "TURRET"
    TURRET_HP: int = WALL_HP // 2
    TURRET_COOLDOWN: int = 1000 # en millisecondes

    #### BANK ####
    BANK: str = "BANK"
    
    #### WAVE ####
    DIFFICULTY: dict[int, int] = field(default_factory=lambda: {
        1: 10, # EASY
        3: 20, # NORMAL
        10: 30, # HARD
        50: 45, # HARDER
        100: 70 # INSANE
    })
    SECURITY_ZONE: int = 200

    #### BULLET #### 
    BULLET_SIZE: int = 12
    BULLET_VELOCITY:int = 500
    BULLET_COOLDOWN: int = 10

    #### PHYSIQUE ####
    GRAVITY: float = 9.81

    #### FONT ####
    FONTS: Dict[int , pygame.font.Font] = field(init=False)

    #### GRID ####
    DIRECTIONS_ALGO: List[Tuple[int, int]] = field(default_factory=lambda: [(1, 0), (0, -1), (-1, 0), (0, 1)])
    DIRECTIONS_ENEMIS: List[Tuple[int, int]] = field(default_factory=lambda: [(1, 0), (0, -1), (-1, 0), (0, 1)]) #[(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
    CELL_SIZE: int = 64

    #### SCREEN ####
    SCREEN_WIDTH: int = 25 * CELL_SIZE # AXE X de l'ecran
    SCREEN_HEIGHT: int = 19 * CELL_SIZE # AXE Y de l'ecran (vers le bas c'est positif)
    OFFSET: int = 5

    #### BUILDINGS TYPE ####
    EMPTY: str = "EMPTY"
    WALL: str = "WALL"
    TURRET: str = "TURRET"
    BANK: str = "BANK"

    #### CELL_COST #####
    cell_cost: Dict[str, int] = field(default_factory=lambda: {
        "EMPTY": 1,
        "WALL": 50,
        "TURRET": 20
    })

    TYPE_COST: Dict[str, int] = field(default_factory=lambda: {
        "EMPTY": 1,
        "WALL": 50,
        "TURRET": 0,
        "BANK": 300,
        "PLAYER": 0
    })

    MODE: Dict[str, int] = field(default_factory=lambda: {
        "EASY": 1000,
        "NORMAL": 500,
        "HARD": 250,
        "CREATIF": False 
    })

    #### UI ####
    UI_LAYOUT_PATH = 'src/ui/layout.json'
    UI_TREE_PATH = 'src/ui/tree.json'

    ### COLOR ####
    VISION_HUMAIN = 128
    DEFAULT: str = "DEFAULT"


    def __post_init__(self):
        
        #### GRID ####
        self.COLS = self.SCREEN_WIDTH // self.CELL_SIZE
        self.ROWS = self.SCREEN_HEIGHT // self.CELL_SIZE

        #### FONT ####
        PATH_FONT: str = 'assets/font/boldpixels/BoldPixels.ttf'
        FONT_100: pygame.font.Font = pygame.font.Font(PATH_FONT, 100)
        FONT_75: pygame.font.Font = pygame.font.Font(PATH_FONT, 75)
        FONT_50: pygame.font.Font = pygame.font.Font(PATH_FONT, 50)
        FONT_25: pygame.font.Font = pygame.font.Font(PATH_FONT, 25)
        FONT_10: pygame.font.Font = pygame.font.Font(PATH_FONT, 10)

        self.FONTS = {
            100 : FONT_100,
            75 : FONT_75,
            50 : FONT_50,
            25 : FONT_25,
            10 : FONT_10
        }

        WALL_SPRITE: pygame.Surface = pygame.image.load(self.WALL_SPRITE_PATH)
        TURRET_SPRITE: pygame.Surface = pygame.image.load(self.TURRET_SPRITE_PATH)
        PLAYER_SPRITE: pygame.Surface = pygame.image.load(self.PLAYER_SPRITE_PATH)
        KERNEL_SPRITE: pygame.Surface = pygame.image.load(self.KERNEL_SPRITE_PATH)
        ENEMIE_SPRITE: pygame.Surface = pygame.image.load(self.ENEMIE_SPRITE_PATH)
        DEFAULT_SPRITE: pygame.Surface = pygame.surface.Surface((64, 64), masks=(255, 0, 0))

        self.SPRITE = {
            self.WALL : WALL_SPRITE,
            self.TURRET : TURRET_SPRITE,
            self.PLAYER : PLAYER_SPRITE,
            self.KERNEL : KERNEL_SPRITE,
            self.ENEMIE : ENEMIE_SPRITE,
            self.DEFAULT : DEFAULT_SPRITE
        }
    

    def get_font(self, size: int) -> pygame.font.Font:
        '''Recupere une font avec un taille specifier'''
        return self.FONTS.get(size, self.FONTS[50])
    
    def get_sprite(self, type: str) -> pygame.Surface:
        ''' Renvoie le sprite associer au type STR donner '''
        return self.SPRITE.get(type, self.SPRITE["DEFAULT"])