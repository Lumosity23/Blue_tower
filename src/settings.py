import pygame
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

@dataclass
class Settings:
    """
    Paramètres globaux du jeu. 
    Note : Les sprites sont gérés par le SpriteManager, 
    Settings ne stocke que les chemins et les métadonnées.
    """

    # ==========================================
    # 1. CONSTANTES DE CLÉS (Pour éviter les typos)
    # ==========================================
    # Ces strings servent de clés dans nos dictionnaires
    HP = "hp"
    COST = "cost"
    RANGE = "range"
    COOLDOWN = "cooldown"
    DAMAGE = "damage"
    VELOCITY = "velocity"
    SIZE = "size"
    SPRITE_ID = "sprite_id"

    # ==========================================
    # 2. DIMENSIONS DU MONDE ET ÉCRAN
    # ==========================================
    CELL_SIZE: int = 64
    
    # Taille de la fenêtre (Ce que le joueur voit)
    SCREEN_WIDTH: int = 1920 
    SCREEN_HEIGHT: int = 1080
    
    # Taille du monde réel (La carte totale où la caméra voyage)
    # Ici, une carte de 50x50 cellules
    WORLD_COLS: int = 50
    WORLD_ROWS: int = 50
    WORLD_WIDTH: int = WORLD_COLS * CELL_SIZE
    WORLD_HEIGHT: int = WORLD_ROWS * CELL_SIZE
    
    # Utilisé pour le culling (ne pas dessiner hors champ)
    @property
    def WORLD_RECT(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.WORLD_WIDTH, self.WORLD_HEIGHT)

    # ==========================================
    # 3. ÉCONOMIE ET ÉQUILIBRAGE (Types)
    # ==========================================
    EMPTY = "EMPTY"
    WALL = "WALL"
    TURRET = "TURRET"
    BANK = "BANK"
    PLAYER = "PLAYER"
    KERNEL = "KERNEL"
    ENEMIE = "ENEMIE"

    # Coût de passage pour le Pathfinding (Flow Field)
    # Plus c'est haut, plus l'ennemi évite la zone. 0 = Infranchissable.
    TYPE_COST: Dict[str, int] = field(default_factory=lambda: {
        "EMPTY": 1,
        "WALL": 0,    # 0 car infranchissable, l'ennemi doit contourner
        "TURRET": 0,
        "PLAYER": 1
    })

    # ==========================================
    # 4. DATA MASTER DICTIONARY : BÂTIMENTS
    # ==========================================
    # C'est ici que le BuildManager et le Cursor piochent TOUT.
    BUILDINGS_DATA: Dict[str, dict] = field(default_factory=lambda: {
        "WALL": {
            "hp": 100,
            "cost": 25,
            "range": 0,
            "sprite_id": "wall", # ID utilisé par le SpriteManager
            "size": (64, 64)
        },
        "TURRET": {
            "hp": 50,
            "cost": 150,
            "range": 300,
            "cooldown": 1000,
            "damage": 10,
            "sprite_id": "turret",
            "size": (64, 64)
        },
        "BANK": {
            "hp": 80,
            "cost": 300,
            "range": 0,
            "sprite_id": "bank",
            "size": (64, 64)
        }
    })

    # ==========================================
    # 5. UNITÉS (PLAYER & ENEMIES)
    # ==========================================
    PLAYER_STATS: dict = field(default_factory=lambda: {
        "hp": 100,
        "velocity": 500,
        "size": (44, 76) # 22x38 * 2
    })

    ENEMIE_STATS: dict = field(default_factory=lambda: {
        "hp": 15,
        "velocity": 150,
        "damage": 5,
        "size": (30, 30)
    })

    KERNEL_STATS: dict = field(default_factory=lambda: {
        "hp": 1000,
        "cooldown": 1500,
        "size": (128, 128)
    })

    # ==========================================
    # 6. PROJECTILES
    # ==========================================
    BULLET_SIZE: int = 12
    BULLET_VELOCITY: int = 800
    BULLET_COOLDOWN: int = 150 # ms entre chaque tir du joueur

    # ==========================================
    # 7. PATHS ET ASSETS
    # ==========================================
    UI_LAYOUT_PATH = 'src/ui/layout.json'
    UI_TREE_PATH = 'src/ui/tree.json'
    
    # Dictionnaire des chemins pour le SpriteManager
    ASSET_PATHS: Dict[str, str] = field(default_factory=lambda: {
        "PLAYER": 'assets/player.png',
        "ENEMIE": 'assets/enemie.png',
        "KERNEL": 'assets/kernel.png',
        "wall": 'assets/wall_gab.png',
        "turret": 'assets/turret.png',
        "bullet": 'assets/bullet.png'
    })

    # ==========================================
    # 8. SYSTÈMES (DIFFICULTÉ, GRILLE)
    # ==========================================
    DIRECTIONS_ALGO: List[Tuple[int, int]] = field(default_factory=lambda: [(1, 0), (0, -1), (-1, 0), (0, 1)])
    
    DIFFICULTY = {
        "spawn_wave" : 30, # formule math pour augment plus que juste ( multiplier )
        "mini_boss" : 1, # formule math pour augment plus que juste ( multiplier )
        "hp_enemy" : 10, # formule math pour augment plus que juste ( multiplier )
        "money_earn" : 20, # formule math pour augment plus que juste ( multiplier )
        "boss" : 0.5, # formule math pour augment plus que juste ( multiplier )
        "wave_number" : 5 # formule math pour augment plus que juste ( multiplier )
    }

    DIFFICULTY_MTP: dict = field(default_factory=lambda: {
        "EASY" : 0.7,
        "NORMAL" : 1,
        "HARD" : 1.5,
        "INSANE" : 2.4,
        "DEMON" : 4
    })

    def __post_init__(self):
        """ Calculs automatiques après l'initialisation """
        # On s'assure que ROWS/COLS correspondent bien au WORLD et non au SCREEN
        self.COLS = self.WORLD_WIDTH // self.CELL_SIZE
        self.ROWS = self.WORLD_HEIGHT // self.CELL_SIZE

    # On pourrait ajouter une méthode pour récupérer proprement les données
    def get_build_data(self, key: str) -> dict:
        return self.BUILDINGS_DATA.get(key, {})