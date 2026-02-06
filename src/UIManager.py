import pygame
from settings import Settings


class UIManager():
    
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.Font(Settings.PATH_FONT, 50)
        # On sauvgarde le text deja "Render" pour eviter de le refaire (OPTIMISATION)
        self.cache_text = {}
    
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