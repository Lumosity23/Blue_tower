import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class UIManager():
    
    def __init__(self, game: "App"):
        pygame.font.init()
        self.game = game
        self.font = pygame.font.Font(self.game.st.PATH_FONT, 50)
        # On sauvgarde le text deja "Render" pour eviter de le refaire (OPTIMISATION)
        self.cache_text = {}
        self.sprite_cache = {}
    
    def draw_text(self, surface: pygame.Surface, text: str, x: int, y: int, color: tuple=(255,255,255), align: str='topleft'):
        '''
            surface : la surface sur la quelle tu veux dessiner\n
            text : le text que tu veux afficher\n
            x, y : la position que tu veux lui donner en x et y\n
            color : si tu veux une autre couleur que le noir (0,0,0) -> noire\n
            align : permet de dire par ou alligner la text ('topleft', 'center',....)
        '''
        # ---- 1. RENDU (partie lourde) ---- #
        img = None
        # On va stocker les "rendu" par text et positon sur l'ecran
        key = (text, color)

        # Si deja "rendu" alors on affiche simplement la copy
        if key in self.cache_text:
            img = self.cache_text[key].copy()
        else:
            img = self.font.render(text, True, color)
            # Sécurité : Si le cache est trop gros (>100 images), on le vide pour éviter le crash mémoire
            if len(self.cache_text) > 100:
                self.cache_text.clear()
            
            # Stocke le "rendu" pour la prochaine fois
            self.cache_text[key] = img
        
        # ---- 2. POSITIONEMENT ---- #
        rect = img.get_rect()
        
        if align == "center":
            rect.center = (x, y)
        elif align == "topright":
            rect.topright = (x, y)
        else:
            rect.topleft = (x, y)
        

        # ---- 3. AFFICHAGE ---- # 
        surface.blit(img, rect)
        # debug (log)
        # print(len(self.cache_text))

    def draw_health_bar(self, entity, surface: pygame.Surface, x: int=None, y: int=None, size: tuple=None) -> None:
        # 1. Calcul du ratio de vie (entre 0.0 et 1.0)
        # On évite la division par zéro par sécurité
        if entity.max_hp <= 0: return
        ratio = entity.current_hp / entity.max_hp
        
        if not x and not y and not size: 
            # 2. Définir la position et la taille de la BARRE
            # On veut qu'elle soit au-dessus de l'objet
            bar_width = entity.rect.width # Même largeur que l'objet
            bar_height = 5

            # Position X : La même que l'objet
            # Position Y : Un peu au-dessus (ex: -10 pixels)
            x = entity.rect.x
            y = entity.rect.y - 10
        
        # si custom bar
        else:
            bar_width, bar_height = size
            x -= bar_width / 2
            y -= bar_height / 2
        # 3. Dessiner le FOND (Rouge ou Noir) -> La barre vide
        # Rect(x, y, width, height)
        back_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), back_rect) # Gris foncé/Noir
        
        # 4. Dessiner la VIE (Vert) -> La barre pleine
        # Sa largeur dépend du ratio !
        fill_width = bar_width * ratio
        fill_rect = pygame.Rect(x, y, fill_width, bar_height)
        
        # Petit détail esthétique : Couleur change selon la vie
        color = (0, 255, 0) # Vert
        if ratio < 0.3: color = (255, 0, 0) # Rouge si critique
        
        pygame.draw.rect(surface, color, fill_rect)


    def get_custom_sprite(self, path: str, size: tuple, shape: str='square'): 
        """   
            Charge une image, la redimensionne et applique une forme.\n
        
            path: chemin vers le sprite en png\n
            size: tuple de taille (x, y)\n
            shape: 'square' ou 'circle'
        """
        # 1. Gestion du cache (clé unique basée sur path et size)
        cache_key = (path, size, shape)
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key].copy()
        
        # 2. Chargement et redimensionnement
        try:
            image = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            print(f"Erreur: Image non trouvée {path}")
            return pygame.Surface(size, (0,255,0)) # Retourne une surface vide ou rose par défaut
        
        image = pygame.transform.scale(image, size)
        
        # 3. Application de la forme
        if shape == 'circle':
            # Créer une surface vide transparente
            final_surf = pygame.Surface(size, pygame.SRCALPHA)
            # Dessiner le masque (cercle blanc)
            radius = min(size[0], size[1]) // 2
            pygame.draw.circle(final_surf, (255, 255, 255), (radius, radius), radius)
            # Appliquer l'image sur le masque
            final_surf.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            image = final_surf
    
        # (Si 'square', on garde l'image redimensionnée telle quelle)
        
          # 4. Sauvegarder dans le cache et retourner
        self.sprite_cache[cache_key] = image
        return image