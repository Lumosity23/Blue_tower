import pygame
from .UIElement import UIElement
from .UIText import UIText

class UIProgressBar(UIElement):
    def __init__(self, x, y, w, h, current_val=100, max_val=100, 
                 fill_color=(0, 255, 0), back_color=(60, 60, 60), 
                 border_color=None, show_text=True, font_size=25, uid=None):
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
                                      text_update=True, uid=f"{uid}_text" if uid else None)
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

    def draw(self, surface):
        if not self.visible: return
        
        abs_rect = self.get_absolute_rect()
        
        # 1. Dessiner le Fond (Background)
        # On utilise le border_radius pour faire une barre arrondie (style pill)
        pygame.draw.rect(surface, self.back_color, abs_rect, border_radius=self.rect.h//2)
        
        # 2. Déterminer la couleur de remplissage
        color = self.fill_color
        if self.dynamic_color:
            if self.display_ratio < 0.2: color = (255, 50, 50)     # Rouge
            elif self.display_ratio < 0.5: color = (255, 200, 50)  # Orange
            else: color = (50, 255, 50)                            # Vert

        # 3. Dessiner le Remplissage (Fill)
        if self.display_ratio > 0:
            fill_w = abs_rect.w * self.display_ratio
            # On s'assure que le rectangle de remplissage respecte l'arrondi
            fill_rect = pygame.Rect(abs_rect.x, abs_rect.y, fill_w, abs_rect.h)
            pygame.draw.rect(surface, color, fill_rect, border_radius=self.rect.h//2)

        # 4. Bordure optionnelle
        if self.border_color:
            pygame.draw.rect(surface, self.border_color, abs_rect, 2, border_radius=self.rect.h//2)
            
        # 5. Dessiner les enfants (donc le texte UIText s'il existe)
        super().draw(surface)