import pygame

from .UIElement import UIElement
from .UIText import UIText


class UITourniquet(UIElement):
    """
    Un carrousel horizontal d'éléments (sprites).
    Les éléments au centre sont plus grands et plus lumineux.
    """

    def __init__(
        self, x: int, y: int, w: int, h: int, sprite_ids: list[str], uid: str = None
    ):
        # On élargit de 10px (5 de chaque côté) pour que les items ne touchent pas les bords
        w += 10
        super().__init__(x, y, w, h, uid)
        self.type = "tourniquet"
        self.sprite_ids = sprite_ids
        self.current_index = 0.0
        self.target_index = 0
        self.lerp_speed = 5.0
        self.spacing = 200  # Espace entre les éléments
        self.base_size = 100  # Taille de base d'un élément

        # Variables pour le drag & drop et l'inertie
        self.is_dragging = False
        self.velocity_x = 0.0

        # On garde en mémoire la hauteur de la zone de contenu (zone des sprites)
        self.content_h = h

        # Création du fond initial via SpriteManager
        self.image = self._SPRITE.get_ui_panel(
            self.rect.w, self.rect.h, color=(50, 50, 60)
        )
        self.title = None

    def set_title(self, text: str, size: int = 50) -> None:
        """Ajoute ou met à jour le titre. Le fond s'agrandit pour l'englober."""
        if not self.title:
            # Espace nécessaire pour le titre (taille + marge)
            title_space = size - 40

            # On agrandit le rect vers le haut
            self.rect.y -= title_space
            # self.rect.h += title_space

            # On régénère le fond avec la nouvelle taille
            self.image = self._SPRITE.get_ui_panel(
                self.rect.w, self.rect.h, color=(50, 50, 60)
            )

            # On place le titre en haut à l'intérieur du nouveau rect
            self.title = UIText(
                self.rect.w // 2,
                20,
                text,
                size_text=size,
                align="midtop",
                uid=f"{self.uid}_title",
            )
            self.add_child(self.title)
        else:
            self.title.set_text(text, size=size)

    def get_selected_item(self) -> str:
        """Retourne l'ID de l'élément actuellement sélectionné (au centre)."""
        if not self.sprite_ids:
            return None
        # On arrondit l'index cible car il peut être un float pendant l'inertie
        return self.sprite_ids[int(round(self.target_index))]

    def handle_event(self, event: pygame.event.EventType) -> bool:
        if not self.visible:
            return False

        # On laisse d'abord les enfants gérer
        if super().handle_event(event):
            return True

        abs_rect = self.get_screen_rect()
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEWHEEL:
            if abs_rect.collidepoint(mouse_pos):
                # On change de cible au scroll avec blocage aux extrémités
                self.target_index -= event.y
                self.target_index = max(
                    0, min(self.target_index, len(self.sprite_ids) - 1)
                )
                self.velocity_x = 0.0  # Stop inertie
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                self.velocity_x = 0.0
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                dx = event.rel[0]
                self.target_index -= dx / self.spacing
                self.target_index = max(
                    0, min(self.target_index, len(self.sprite_ids) - 1)
                )
                # Calcul de l'inertie
                self.velocity_x = self.velocity_x * 0.5 - (dx / self.spacing) * 30.0
                return True

        return False

    def update(self, dt: float) -> None:
        super().update(dt)

        # Application de l'inertie
        if not self.is_dragging and abs(self.velocity_x) > 0.01:
            self.target_index += self.velocity_x * dt
            self.target_index = max(0, min(self.target_index, len(self.sprite_ids) - 1))
            self.velocity_x -= self.velocity_x * 5.0 * dt

            # Arrondi à l'item le plus proche à faible vitesse
            if abs(self.velocity_x) < 0.2:
                self.target_index = round(self.target_index)
                self.velocity_x = 0.0

        # Animation fluide vers l'index cible
        diff = self.target_index - self.current_index
        if abs(diff) > 0.001:
            self.current_index += diff * self.lerp_speed * dt
        else:
            self.current_index = self.target_index

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        abs_rect = self.get_screen_rect()

        # 1. Dessiner le fond (englobe tout, titre inclus)
        surface.blit(self.image, abs_rect)

        # 2. Calculer la zone de contenu (uniquement là où les sprites défilent)
        # On ajoute un padding horizontal (ex: 20px) pour que les items soient coupés avant le bord
        padding_x = 20
        content_rect = pygame.Rect(
            abs_rect.x + padding_x,
            abs_rect.bottom - self.content_h,
            abs_rect.w - (padding_x * 2),
            self.content_h,
        )

        center_x = content_rect.centerx
        center_y = content_rect.centery

        # --- CLIPPING (limité à la zone de contenu avec padding) ---
        old_clip = surface.get_clip()
        new_clip = content_rect.clip(old_clip) if old_clip else content_rect
        surface.set_clip(new_clip)

        # On trie pour dessiner les éléments du fond en premier
        indices = list(range(len(self.sprite_ids)))
        indices.sort(key=lambda i: abs(i - self.current_index), reverse=True)

        for i in indices:
            sprite_id = self.sprite_ids[i]
            dist = i - self.current_index
            x = center_x + dist * self.spacing

            factor = 1.0 / (1.0 + abs(dist) * 0.8)
            size = int(self.base_size * (1.0 + factor * 1.5))

            try:
                sprite = self._SPRITE.get_sprite_resize(sprite_id, (size, size))
                alpha = int(100 + 155 * factor)
                sprite.set_alpha(alpha)

                if factor < 0.8:
                    dark = pygame.Surface((size, size), pygame.SRCALPHA)
                    dark_val = int(150 * (1.0 - factor))
                    dark.fill((0, 0, 0, dark_val))
                    sprite.blit(dark, (0, 0))

                sprite_rect = sprite.get_rect(center=(x, center_y))
                surface.blit(sprite, sprite_rect)

            except Exception as e:
                print(f"Erreur tourniquet sur {sprite_id}: {e}")

        # Restauration du clip
        surface.set_clip(old_clip)

        # 3. Dessiner les enfants (dont le titre) par dessus
        if self.children:
            for child in self.children:
                child.draw(surface)

        if self.debug:
            pygame.draw.rect(surface, (255, 0, 255), abs_rect, 2)
            pygame.draw.rect(surface, (0, 255, 0), content_rect, 1)
