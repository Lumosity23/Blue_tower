import pygame
import os
from typing import TYPE_CHECKING
from utils.path import resource_path as rp

if TYPE_CHECKING:
    from main import App


class SpriteManager:


    def __init__(self, game: "App"):
        self.game = game
        self.st = self.game.st
        
        # 1. CACHE : On stocke les images originales pour éviter de relire le disque
        # { "player": <pygame.Surface>, "wall": <pygame.Surface>, ... }
        self.image_cache = {}
        
        # 2. FONTS : Génération dynamique des tailles
        self.fonts = {}
        self.init_fonts(25, 200, 5)


    def init_fonts(self, start: int, end: int, step: int):
        """ Génère des polices de caractères de façon dynamique """
        pygame.font.init()
        # On récupère le chemin depuis les settings ou un défaut
        font_path = rp('assets/font/boldpixels/BoldPixels.ttf')
        
        if not os.path.exists(font_path):
            print(f"Attention: Police introuvable à {font_path}. Utilisation de la police système.")
            font_path = None # Utilise la police par défaut de Pygame

        for size in range(start, end + step, step):
            self.fonts[size] = pygame.font.Font(font_path, size)

        print(f"SpriteManager: {len(self.fonts)} tailles de polices chargées.")

        from ui.UIText import UIText # Import local pour éviter les imports circulaires
        UIText.set_font_provider(self.fonts)
        

    # ==========================================
    # GESTION DES IMAGES
    # ==========================================
    def get_base_image(self, sprite_id: str) -> pygame.Surface:
        """ Récupère l'image originale (chargement 'paresseux') """
        if sprite_id not in self.image_cache:
            # On cherche le chemin dans Settings.ASSET_PATHS
            path = rp(self.st.ASSET_PATHS.get(sprite_id))
            if not path or not os.path.exists(path):
                # Image de secours (Carré rose de debug)
                surf = pygame.Surface((64, 64))
                surf.fill((255, 0, 255))
                self.image_cache[sprite_id] = surf
                print(f"SpriteManager Error: ID '{sprite_id}' non trouvé.")
            else:
                self.image_cache[sprite_id] = pygame.image.load(path).convert_alpha()
        
        return self.image_cache[sprite_id]


    def get_sprite_resize(self, sprite_id: str, size: tuple[int, int]) -> pygame.Surface:
        """ 
        Méthode demandée : Récupère un sprite et le redimensionne direct.
        Très utile pour les balles ou les effets temporaires.
        """
        base_img = self.get_base_image(sprite_id)
        return pygame.transform.scale(base_img, size)


    def get_custom_sprite(self, sprite_id: str, size: tuple[int, int] = (64, 64), shape: str = 'square') -> pygame.Surface: 
        """ Charge, redimensionne et applique une forme (Cercle ou Carré) """
        image = self.get_sprite_resize(sprite_id, size)
        
        if shape == 'circle':
            final_surf = pygame.Surface(size, pygame.SRCALPHA)
            radius = min(size[0], size[1]) // 2
            pygame.draw.circle(final_surf, (255, 255, 255), (radius, radius), radius)
            final_surf.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            return final_surf
    
        return image
    

    def slice_sprite(self, sprite_id: str, slicing: tuple[int, int], margin: int=0, spacing: int=0 ) -> dict[tuple[int, int], pygame.Surface]:
        ''' Permet de couper un grand sprite en plus petit Rect '''

        bigSprite = self.get_base_image(sprite_id)
        wBT, hBT = bigSprite.get_size()
        w, h = slicing
        tiles = {}

        # On soustrait les marges pour calculer le bon nombre de colonnes/lignes
        cols = (wBT - 2 * margin + spacing) // (w + spacing)
        rows = (hBT - 2 * margin + spacing) // (h + spacing)

        for col in range( cols ):
            for row in range( rows ):
                x = margin + col * (w + spacing)
                y = margin + row * (h + spacing)
                tiles[col, row] = bigSprite.subsurface(pygame.Rect(x, y, w, h))
            
        return tiles
    
    
    def get_animation(self, sprite_id: str, sclicing: tuple[int, int], margin: int=0, spacing: int=0, scaling: int=1) -> dict[int, pygame.Surface]:
        """ Permet de decouper un spritesheet en ligne droite (specialement pour les animation) """
        
        spritesheet = self.get_base_image(sprite_id)
        lenght, _ = spritesheet.get_size()
        w, h = (dim * scaling for dim in sclicing)
        num_frames = int(lenght) // int(sclicing[0])
        
        spritesheet = self.get_sprite_resize(sprite_id, (num_frames * w, h))
        tiles = {}
        
        for col in range(num_frames):
            x = margin + col * (w + spacing)
            tiles[col] = spritesheet.subsurface(pygame.Rect(x, 0, w, h))
        # print(f"animation de : {num_frames} frames")

        return tiles