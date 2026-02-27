import pygame
from .UIElement import UIElement
from .UIText import UIText


class   UIProgressBar(UIElement):
    def __init__(self, x, y, w, h, current_val=100, max_val=100, 
                 fill_color=(0, 255, 0), back_color=(60, 60, 60), 
                 border_color=None, show_text=True, font_size=25, font_color=(255,255,255),
                 uid=None):
        super().__init__(x, y, w, h, uid)
        
        # 1. Données de progression
        self.current_val = current_val
        self.max_val = max_val
        self.target_ratio = self.current_val / self.max_val if self.max_val > 0 else 0
        self.display_ratio = self.target_ratio  # Pour l'animation fluide
        
        # 2. Design et Couleurs
        self.fill_color = fill_color
        self.back_color = back_color
        self.border_color = border_color
        self.dynamic_color = False  # Si True, passe du vert au rouge selon la vie
        
        # 3. Texte optionnel (utilise ta classe UIText)
        self.show_text = show_text
        if self.show_text:
            # On passe une fonction lambda pour que UIText se mette à jour tout seul
            self.text_element = UIText(0, 0, self._get_text_string, size_text=font_size, 
                                      text_update=True, color=font_color, uid=f"{uid}_text" if uid else None)
            self.add_child(self.text_element)
            # Centrage du texte au milieu de la barre
            self.text_element.rect.center = (w // 2, h // 2)

    def _get_text_string(self) -> str:
        ''' Fonction interne pour mettre à jour le texte automatiquement '''
        percentage = int(self.display_ratio * 100)
        return f"{percentage}%"

    def update_values(self, current, max_val=None):
        ''' Met à jour les valeurs et recalcule la cible de l'animation '''
        if max_val is not None:
            self.max_val = max_val
        self.current_val = max(0, min(current, self.max_val))
        
        if self.max_val > 0:
            self.target_ratio = self.current_val / self.max_val
        else:
            self.target_ratio = 0

    def update(self, dt):
        super().update(dt)
        # --- Animation "Lerp" (Lissage) ---
        # La barre rejoint la cible à une vitesse de 5.0 (ajustable)
        lerp_speed = 5.0 * dt
        diff = self.target_ratio - self.display_ratio
        
        if abs(diff) > 0.001:
            self.display_ratio += diff * lerp_speed
        else:
            self.display_ratio = self.target_ratio


    def _render_bar(self, surface: pygame.Surface, draw_rect: pygame.Rect):
        """ Dessine la barre exactement là où on lui dit (draw_rect) """
        # 1. Dessiner le Fond
        pygame.draw.rect(surface, self.back_color, draw_rect, border_radius=self.rect.h//2)
        
        # 2. Déterminer la couleur
        color = self.fill_color
        if self.dynamic_color:
            if self.display_ratio < 0.2: color = (255, 50, 50)     # Rouge
            elif self.display_ratio < 0.5: color = (255, 200, 50)  # Orange
            else: color = (50, 255, 50)                            # Vert

        # 3. Dessiner le Remplissage
        if self.display_ratio > 0:
            fill_w = draw_rect.w * self.display_ratio
            fill_rect = pygame.Rect(draw_rect.x, draw_rect.y, fill_w, draw_rect.h)
            pygame.draw.rect(surface, color, fill_rect, border_radius=self.rect.h//2)

        # 4. Bordure optionnelle
        if self.border_color:
            pygame.draw.rect(surface, self.border_color, draw_rect, 2, border_radius=self.rect.h//2)


    def draw(self, surface: pygame.Surface):
        """ Appelé par ton HUD ou ton UI Manager (AUCUN OFFSET) """
        if not self.visible: return
        
        # On utilise la position absolue sur l'écran telle quelle
        self._render_bar(surface, self.get_screen_rect())
        
        # Comme on est dans l'UI (Scene Graph), on doit dessiner les enfants (ex: Texte)
        super().draw(surface)


    def custom_draw(self, surface: pygame.Surface, cam_offset: pygame.math.Vector2):
        """ Appelé UNIQUEMENT par la Caméra (OFFSET APPLIQUÉ) """
        if not self.visible: return

        # On calcule la position par rapport à la caméra
        world_rect = self.get_screen_rect()
        screen_x = world_rect.x - cam_offset.x
        screen_y = world_rect.y - cam_offset.y
        
        draw_rect = pygame.Rect(screen_x, screen_y, world_rect.w, world_rect.h)
        
        # On dessine à la position calculée
        self._render_bar(surface, draw_rect)