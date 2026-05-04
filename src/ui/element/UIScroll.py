import pygame

from .UIElement import UIElement


class UIScroll(UIElement):
    """
    Un conteneur d'UI scrollable.
    Permet d'ajouter des UIElement et de les faire défiler à la molette.
    """

    def __init__(
        self, x: int, y: int, w: int, h: int, color=(30, 30, 30), uid: str = None
    ):
        super().__init__(x, y, w, h, uid)
        self.type = "scroll"
        self.scroll_speed = 60  # Augmenté légèrement pour la sensation de fluidité
        self.lerp_speed = 12  # Vitesse de l'interpolation

        # Fond du scroll
        self.image = self._SPRITE.get_ui_panel(w, h, color=color)

        # Limites de scroll
        self.max_scroll_y = 0
        self.max_scroll_x = 0

        # Cible pour l'interpolation du scroll
        self.target_scroll_offset = self.scroll_offset.copy()

        # Variables pour le Glisser-Déposer (Drag) et Inertie
        self.is_dragging = False
        self.velocity_y = 0.0

    def add_child(self, new_child: UIElement) -> None:
        super().add_child(new_child)
        self.update_content_size()

    def update_content_size(self) -> None:
        """Calcule la zone totale occupée par les enfants pour définir les limites du scroll."""
        if not self.children:
            self.max_scroll_y = 0
            self.max_scroll_x = 0
            return

        max_y = 0
        max_x = 0
        for child in self.children:
            # On prend le point le plus bas/droite de chaque enfant
            max_y = max(max_y, child.rect.bottom)
            max_x = max(max_x, child.rect.right)

        # On ajoute un petit paddin pour que les element ne touche pas le bord
        self.max_scroll_y = max(0, max_y - self.rect.h) + 20
        self.max_scroll_x = max(0, max_x - self.rect.w) + 20

        # On contraint la cible si les limites ont changé
        self.target_scroll_offset.y = max(
            0, min(self.target_scroll_offset.y, self.max_scroll_y)
        )
        self.target_scroll_offset.x = max(
            0, min(self.target_scroll_offset.x, self.max_scroll_x)
        )

    def update(self, dt: float) -> None:
        """Met à jour l'interpolation du scroll."""
        super().update(dt)
        if not self.visible:
            return

        # Application de l'inertie si on ne drague plus
        if not self.is_dragging and abs(self.velocity_y) > 10.0:
            self.target_scroll_offset.y += self.velocity_y * dt
            self.target_scroll_offset.y = max(
                0, min(self.target_scroll_offset.y, self.max_scroll_y)
            )
            # Décélération (Friction)
            self.velocity_y -= self.velocity_y * 5.0 * dt

        # Interpolation (Lerp) du scroll_offset vers target_scroll_offset
        if self.scroll_offset.distance_to(self.target_scroll_offset) > 0.5:
            # Formule de lerp indépendante du framerate
            # current += (target - current) * speed * dt
            self.scroll_offset += (
                (self.target_scroll_offset - self.scroll_offset) * self.lerp_speed * dt
            )
        else:
            # On colle à la cible quand on est très proche pour éviter les micros-mouvements infinis
            self.scroll_offset = self.target_scroll_offset.copy()

    def handle_event(self, event: pygame.event.EventType) -> bool:
        if not self.visible:
            return False

        # 1. On laisse les enfants gérer l'événement en priorité (ex: Tourniquet, Boutons)
        if super().handle_event(event):
            return True

        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()

        # 2. Gestion du scroll à la molette
        if event.type == pygame.MOUSEWHEEL:
            if abs_rect.collidepoint(mouse_pos):
                # Scroll vertical (event.y est positif vers le haut, on soustrait pour descendre)
                self.target_scroll_offset.y -= event.y * self.scroll_speed
                self.target_scroll_offset.y = max(
                    0, min(self.target_scroll_offset.y, self.max_scroll_y)
                )

                # Scroll horizontal (optionnel)
                self.target_scroll_offset.x += event.x * self.scroll_speed
                self.target_scroll_offset.x = max(
                    0, min(self.target_scroll_offset.x, self.max_scroll_x)
                )
                self.velocity_y = 0.0  # Stop inertie
                return True

        # 3. Gestion du glisser-déposer (Drag)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                self.velocity_y = 0.0
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                dy = event.rel[1]
                self.target_scroll_offset.y -= dy
                self.target_scroll_offset.y = max(
                    0, min(self.target_scroll_offset.y, self.max_scroll_y)
                )
                # Calcul de la vélocité pour l'inertie
                self.velocity_y = self.velocity_y * 0.5 - dy * 30.0
                return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        abs_rect = self.get_screen_rect()
        # On dessine le fond (image)
        surface.blit(self.image, abs_rect)

        if self.children:
            # Zone de clipping pour ne pas dessiner en dehors du scroll
            old_clip = surface.get_clip()
            new_clip = abs_rect.clip(old_clip) if old_clip else abs_rect
            surface.set_clip(new_clip)

            for child in self.children:
                child.draw(surface)

            # Restauration du clip
            surface.set_clip(old_clip)

        if self.debug:
            pygame.draw.rect(surface, (255, 0, 255), abs_rect, 2)
