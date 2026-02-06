import pygame
from settings import Settings


# cache simple pour ne pas recharger les images du disque à chaque fois 
_texture_cache = {}

def get_custom_sprite(path: str, size: tuple, shape: str='square'): 
    """   
        Charge une image, la redimensionne et applique une forme.\n
        
        path: chemin vers le sprite en png\n
        size: tuple de taille (x,y)\n
        shape: 'square' ou 'circle'
    """
    # 1. Gestion du cache (clé unique basée sur path et size)
    cache_key = (path, size, shape)
    if cache_key in _texture_cache:
        return _texture_cache[cache_key].copy()
    
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
    _texture_cache[cache_key] = image
    return image

