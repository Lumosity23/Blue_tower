import os
from typing import TYPE_CHECKING

import pygame

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
        self.font_path = None
        self.fonts = {}
        self.init_fonts(25, 200, 5)

    def init_fonts(self, start: int, end: int, step: int):
        """Génère des polices de caractères de façon dynamique"""
        pygame.font.init()
        # On récupère le chemin depuis les settings ou un défaut
        self.font_path = rp("assets/font/boldpixels/BoldPixels.ttf")

        if not os.path.exists(self.font_path):
            print(
                f"Attention: Police introuvable à {self.font_path}. Utilisation de la police système."
            )
            self.font_path = None  # Utilise la police par défaut de Pygame

        for size in range(start, end + step, step):
            self.fonts[size] = pygame.font.Font(self.font_path, size)

        print(f"SpriteManager: {len(self.fonts)} tailles de polices chargées.")

        from ui.element.UIText import (
            UIText,  # Import local pour éviter les imports circulaires
        )

        UIText.set_font_provider(self.fonts)

    def get_font(self, font_size: int):
        """Utilise que dans des cas extreme pour du Hot debug"""
        return pygame.font.Font(self.font_path, font_size)

    # ==========================================
    # GESTION DES IMAGES
    # ==========================================
    def get_base_image(self, sprite_id: str) -> pygame.Surface:
        """Récupère l'image originale (chargement 'paresseux')"""
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

    def get_sprite_resize(
        self, sprite_id: str, size: tuple[int, int]
    ) -> pygame.Surface:
        """
        Méthode demandée : Récupère un sprite et le redimensionne direct.
        Très utile pour les balles ou les effets temporaires.
        """
        base_img = self.get_base_image(sprite_id)
        return pygame.transform.scale(base_img, size)

    def get_custom_sprite(
        self, sprite_id: str, size: tuple[int, int] = (64, 64), shape: str = "square"
    ) -> pygame.Surface:
        """Charge, redimensionne et applique une forme (Cercle ou Carré)"""
        image = self.get_sprite_resize(sprite_id, size)

        if shape == "circle":
            final_surf = pygame.Surface(size, pygame.SRCALPHA)
            radius = min(size[0], size[1]) // 2
            pygame.draw.circle(final_surf, (255, 255, 255), (radius, radius), radius)
            final_surf.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            return final_surf

        return image

    def slice_sprite(
        self,
        sprite_id: str,
        slicing: tuple[int, int],
        margin: int = 0,
        spacing: int = 0,
    ) -> dict[tuple[int, int], pygame.Surface]:
        """Permet de couper un grand sprite en plus petit Rect"""

        bigSprite = self.get_base_image(sprite_id)
        wBT, hBT = bigSprite.get_size()
        w, h = slicing
        tiles = {}

        # On soustrait les marges pour calculer le bon nombre de colonnes/lignes
        cols = (wBT - 2 * margin + spacing) // (w + spacing)
        rows = (hBT - 2 * margin + spacing) // (h + spacing)

        for col in range(cols):
            for row in range(rows):
                x = margin + col * (w + spacing)
                y = margin + row * (h + spacing)
                tiles[col, row] = bigSprite.subsurface(pygame.Rect(x, y, w, h))

        return tiles

    def get_animation(
        self,
        sprite_id: str,
        sclicing: tuple[int, int],
        margin: int = 0,
        spacing: int = 0,
        scaling: int = 1,
    ) -> dict[int, pygame.Surface]:
        """Permet de decouper un spritesheet en ligne droite (specialement pour les animation)"""

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

    def get_ui_panel(
        self,
        target_width,
        target_height,
        color: pygame.Color = (91, 110, 225),
        sprite_id="sample_ui",
        slice_size=16,
    ):

        # Sécurité minimale pour éviter les crashs si la taille demandée est plus petite que les 4 coins
        target_width = max(target_width, slice_size * 2)
        target_height = max(target_height, slice_size * 2)

        panel = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
        tiles = self.slice_sprite(sprite_id, (slice_size, slice_size))

        top_left, top_mid, top_right = tiles[(0, 0)], tiles[(1, 0)], tiles[(2, 0)]
        mid_left, center, mid_right = tiles[(0, 1)], tiles[(1, 1)], tiles[(2, 1)]
        bot_left, bot_mid, bot_right = tiles[(0, 2)], tiles[(1, 2)], tiles[(2, 2)]

        # 1. Dessiner les 4 coins (Pas de changement)
        panel.blit(top_left, (0, 0))
        panel.blit(top_right, (target_width - slice_size, 0))
        panel.blit(bot_left, (0, target_height - slice_size))
        panel.blit(bot_right, (target_width - slice_size, target_height - slice_size))

        # --- NOUVELLE METHODE SANS OVERLAP ---

        # Limites où on doit s'arrêter de dessiner le centre et les bords
        end_x = target_width - slice_size
        end_y = target_height - slice_size

        # 2. Bords horizontaux (Haut et Bas)
        current_x = slice_size
        while current_x < end_x:
            # On calcule la largeur restante à remplir.
            # Si c'est plus grand que la tuile, on prend la taille de la tuile. Sinon, on prend juste le reste.
            draw_width = min(slice_size, end_x - current_x)

            # On coupe la tuile si nécessaire
            cropped_top = top_mid.subsurface((0, 0, draw_width, slice_size))
            cropped_bot = bot_mid.subsurface((0, 0, draw_width, slice_size))

            panel.blit(cropped_top, (current_x, 0))
            panel.blit(cropped_bot, (current_x, target_height - slice_size))
            current_x += draw_width

        # 3. Bords verticaux (Gauche et Droite)
        current_y = slice_size
        while current_y < end_y:
            draw_height = min(slice_size, end_y - current_y)

            cropped_left = mid_left.subsurface((0, 0, slice_size, draw_height))
            cropped_right = mid_right.subsurface((0, 0, slice_size, draw_height))

            panel.blit(cropped_left, (0, current_y))
            panel.blit(cropped_right, (target_width - slice_size, current_y))
            current_y += draw_height

        # 4. Remplir le centre (Double boucle adaptative)
        current_x = slice_size
        while current_x < end_x:
            draw_width = min(slice_size, end_x - current_x)

            current_y = slice_size
            while current_y < end_y:
                draw_height = min(slice_size, end_y - current_y)

                # On coupe le centre selon X ET selon Y !
                cropped_center = center.subsurface((0, 0, draw_width, draw_height))
                panel.blit(cropped_center, (current_x, current_y))

                current_y += draw_height
            current_x += draw_width

        # --- COLORISATION ---
        panel_color = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
        panel_color.fill(color)

        # Astuce : Utilise BLEND_RGBA_MULT ou BLEND_RGB_MULT
        # BLEND_MULT basique peut parfois modifier l'alpha de tes coins transparents et faire des carrés bizarres.
        panel.blit(panel_color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return panel
