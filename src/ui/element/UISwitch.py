import pygame
from .UIElement import UIElement
from .UIText import UIText

class UISwitch(UIElement):
    """
    ===========================================================================
    FICHE D'UTILISATION : UISwitch
    ===========================================================================
    Description : 
    Composant d'interface agissant comme un interrupteur (On/Off) avec une 
    animation fluide, similaire à un slider dans les paramètres d'un téléphone.
    Il intègre automatiquement un texte descriptif sur la même ligne.

    Arguments :
    - x, y : Position du coin supérieur gauche.
    - text (str) : Le texte descriptif de l'action.
    - on_toggle_callback (function) : Fonction appelée sans argument lors 
      du changement d'état. L'état peut être lu via self.state.
    - start_state (bool) : L'état initial du switch (True=ON, False=OFF).
    - size_text (int) : Taille du texte.
    - text_color (tuple) : Couleur du texte.
    - color_on (tuple) : Couleur du fond quand activé.
    - color_off (tuple) : Couleur du fond quand désactivé.
    - uid (str) : Identifiant unique pour le layout.

    Méthodes utiles :
    - set_state(state: bool) : Force l'état du switch (sans appeler le callback).
    
    Fonctionnement interne :
    - Hérite de UIElement.
    - Met à jour son "image" (pygame.Surface) à chaque frame dans update() pour
      animer la transition du curseur (le rond) grâce à une interpolation (lerp).
    - Capture l'événement MOUSEBUTTONDOWN pour basculer son état (self.state)
      et déclencher le callback passé en paramètre.
    ===========================================================================
    """

    def __init__(self, x, y, text, on_toggle_callback, start_state=False, size_text=50, text_color=(255, 255, 255), color_on=(50, 150, 50), color_off=(150, 50, 50), uid=None):
        
        uid_text = f"{uid}_text" if uid else None
        self.text_element = UIText(0, 0, text, size_text, text_color, uid=uid_text)
        
        # Dimensions de la partie "switch" (cloison deux fois plus longue que haute)
        self.switch_w = 100
        self.switch_h = 50
        self.padding = 30
        
        # Dimensions totales
        w = self.text_element.rect.w + self.padding + self.switch_w
        h = max(self.text_element.rect.h, self.switch_h)
        
        super().__init__(x, y, w, h, uid)
        
        self.add_child(self.text_element)
        
        # Positionnement vertical centré pour le texte
        self.text_element.rect.midleft = (0, self.rect.h // 2)
        
        self.type = "switch"
        self.callback = on_toggle_callback
        self.sound = "click_default"
        
        # Couleurs
        self.color_on = color_on
        self.color_off = color_off
        
        # Etat
        self.state = start_state
        self.is_hovered = False
        
        # Animation du curseur (0.0 = OFF, 1.0 = ON)
        self.cursor_ratio = 1.0 if start_state else 0.0
        self.lerp_speed = 15.0 # Vitesse d'animation du slider
        
        # Dessin initial
        self.render_switch()


    def render_switch(self):
        # On nettoie l'image (transparente)
        self.image.fill((0, 0, 0, 0))
        
        # Calcul de la couleur de fond par interpolation
        r = int(self.color_off[0] + (self.color_on[0] - self.color_off[0]) * self.cursor_ratio)
        g = int(self.color_off[1] + (self.color_on[1] - self.color_off[1]) * self.cursor_ratio)
        b = int(self.color_off[2] + (self.color_on[2] - self.color_off[2]) * self.cursor_ratio)
        bg_color = (r, g, b)
        
        # Si survolé, on éclaircit légèrement
        if self.is_hovered:
            bg_color = (min(255, bg_color[0] + 20), min(255, bg_color[1] + 20), min(255, bg_color[2] + 20))
            
        switch_x = self.rect.w - self.switch_w
        switch_y = (self.rect.h - self.switch_h) // 2
        
        # Dessin de la "cloison" (fond du switch) avec le SpriteManager
        bg_panel = self._SPRITE.get_ui_panel(self.switch_w, self.switch_h, color=bg_color)
        self.image.blit(bg_panel, (switch_x, switch_y))
        
        # Dessin du curseur (un carré)
        cursor_size = self.switch_h - 8
        cursor_panel = self._SPRITE.get_ui_panel(cursor_size, cursor_size, color=(255, 255, 255))
        
        # Position X du curseur : varie de la gauche vers la droite de la cloison
        min_x = switch_x + 4
        max_x = switch_x + self.switch_w - cursor_size - 4
        
        cursor_x = min_x + (max_x - min_x) * self.cursor_ratio
        cursor_y = switch_y + 4
        
        self.image.blit(cursor_panel, (int(cursor_x), int(cursor_y)))


    def update(self, dt):
        super().update(dt)
        
        # Animation fluide du curseur vers l'état actuel
        target_ratio = 1.0 if self.state else 0.0
        diff = target_ratio - self.cursor_ratio
        
        if abs(diff) > 0.01:
            self.cursor_ratio += diff * self.lerp_speed * dt
            self.render_switch()
        elif self.cursor_ratio != target_ratio:
            self.cursor_ratio = target_ratio
            self.render_switch()

            
    def set_state(self, state: bool):
        """ Force l'état du switch sans déclencher le callback """
        self.state = state
        # Le rendu se mettra à jour à la prochaine frame via update()


    def handle_event(self, event: pygame.event.EventType) -> bool:
        if not self.visible:
            return False

        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = abs_rect.collidepoint(mouse_pos)

        if self.is_hovered != was_hovered:
            self.render_switch() # Met à jour la couleur au survol
        
        # Clic sur le composant (texte ou switch)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.state = not self.state
                
                # Appel du callback
                if self.callback:
                    if self._EVENTBUS:
                        self._EVENTBUS.publish("CLICK_BUTTON", self.sound)
                    self.callback()
                
                return True
                
        # On passe aussi l'event aux enfants (comme le texte) si nécessaire
        return super().handle_event(event)
