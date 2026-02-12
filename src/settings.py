from dataclasses import dataclass


@dataclass
class Settings:
    
    #### PLAYER ####
    PLAYER_WIDTH = 22 * 2
    PLAYER_HEIGHT = 38 * 2
    PLAYER_HEALTH = 30
    PLAYER_SPRITE = 'assets/player.png'

    #### ENEMIE ####
    ENEMIE_SIZE = (30,30)
    ENEMIE_HEALTH = 5
    ENEMIE_SPRITE = 'assets/enemie.png'
    
    #### KERNEL ####
    KERNEL_SPRITE = 'assets/kernel.png'
    KERNEL_SIZE = 64 * 2
    KERNEL_HP = 40
    KERNEL_COOLDOWN = 1500

    #### WALL ####
    WALL_SPRITE = 'assets/wall_gab.png'
    WALL = "WALL"
    WALL_HP = 50
 
    #### TURRET ####
    TURRET_SPRITE = 'assets/turret.png'
    TURRET = "TURRET"
    TURRET_HP = WALL_HP // 2
    TURRET_COOLDOWN = 1000 # en millisecondes

    #### BANK ####
    BANK = 3
    
    #### WAVE ####
    DIFFICULTY = {
        1: 3, # EASY
        3: 5, # NORMAL
        10: 10, # HARD
        50: 25, # HARDER
        100: 50 # INSANE
    }
    SECURITY_ZONE = 200

    #### BULLET #### 
    BULLET_SIZE = 12
    BULLET_VELOCITY = 500
    BULLET_COOLDOWN = 10

    #### PHYSIQUE ####
    GRAVITY = 9.81

    #### GRID ####
    CELL_SIZE = 64 #* 2

    #### SCREEN ####
    SCREEN_WIDTH = 25 * CELL_SIZE # AXE X de l'ecran
    SCREEN_HEIGHT = 19 * CELL_SIZE # AXE Y de l'ecran (vers le bas c'est positif)
    OFFSET = 5

    #### GRID ####
    COLS = SCREEN_WIDTH // CELL_SIZE
    ROWS = SCREEN_HEIGHT // CELL_SIZE
    DIRECTIONS_ALGO = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    DIRECTIONS_ENEMIS = [(1, 0), (0, -1), (-1, 0), (0, 1)] #[(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
    
    #### FONT ####
    PATH_FONT = 'assets/font/boldpixels/BoldPixels.ttf'

    #### BUILDINGS TYPE ####
    EMPTY = "EMPTY"
    WALL = "WALL"
    TURRET = "TURRET"
    BANK = "BANK"

    #### CELL_COST #####
    cell_cost = {
        EMPTY: 1,
        WALL: 50
    }

    TYPE_COST = {
        EMPTY: 1,
        WALL: 50,
        TURRET: 200,
        BANK: 300,
    }

    MODE = {
        "EASY": 1000,
        "NORMAL": 500,
        "HARD": 250,
        "CREATIF": False 
    }

    #### UI ####
    ROOT_PANEL_POS = 100, 100
    ROOT_PANEL_SIZE = 300, 200