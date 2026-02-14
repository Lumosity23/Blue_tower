import pygame
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

@dataclass
class Settings:
    
    #### PLAYER ####
    PLAYER_WIDTH: int = 22 * 2
    PLAYER_HEIGHT: int = 38 * 2
    PLAYER_HEALTH: int = 30
    PLAYER_SPRITE: str = 'assets/player.png'

    #### ENEMIE ####
    ENEMIE_SIZE: Tuple[int, int] = (30,30)
    ENEMIE_HEALTH: int = 5
    ENEMIE_SPRITE: str = 'assets/enemie.png'
    
    #### KERNEL ####
    KERNEL_SPRITE: str = 'assets/kernel.png'
    KERNEL_SIZE: str = 64 * 2
    KERNEL_HP: str = 40
    KERNEL_COOLDOWN: int = 1500

    #### WALL ####
    WALL_SPRITE: str = 'assets/wall_gab.png'
    WALL: str = "WALL"
    WALL_HP: int = 50
 
    #### TURRET ####
    TURRET_SPRITE: str = 'assets/turret.png'
    TURRET: str = "TURRET"
    TURRET_HP: int = WALL_HP // 2
    TURRET_COOLDOWN: int = 1000 # en millisecondes

    #### BANK ####
    BANK: str = "BANK"
    
    #### WAVE ####
    DIFFICULTY: dict[int, int] = field(default_factory=lambda: {
        1: 3, # EASY
        3: 5, # NORMAL
        10: 10, # HARD
        50: 25, # HARDER
        100: 50 # INSANE
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
        "TURRET": 200,
        "BANK": 300,
    })

    MODE: Dict[str, int] = field(default_factory=lambda: {
        "EASY": 1000,
        "NORMAL": 500,
        "HARD": 250,
        "CREATIF": False 
    })

    #### UI ####
    UI_LAYOUT_PATH = 'src/ui/layout.json'

    ### COLOR ####
    VISION_HUMAIN = 128


    def __post_init__(self):
        
        #### GRID ####
        self.COLS = self.SCREEN_WIDTH // self.CELL_SIZE
        self.ROWS = self.SCREEN_HEIGHT // self.CELL_SIZE

        #### FONT ####
        PATH_FONT: str = 'assets/font/boldpixels/BoldPixels.ttf'
        FONT_100: pygame.font = pygame.font.Font(PATH_FONT, 100)
        FONT_75: pygame.font = pygame.font.Font(PATH_FONT, 75)
        FONT_50: pygame.font = pygame.font.Font(PATH_FONT, 50)
        FONT_25: pygame.font = pygame.font.Font(PATH_FONT, 25)
        FONT_10: pygame.font = pygame.font.Font(PATH_FONT, 10)

        self.FONTS = {
            100 : FONT_100,
            75 : FONT_75,
            50 : FONT_50,
            25 : FONT_25,
            10 : FONT_10
        }
    

    def get_font(self, size: int) -> pygame.font.Font:
        '''Recupere une font avec un taille specifier'''
        return self.FONTS.get(size, self.FONTS.get(50))