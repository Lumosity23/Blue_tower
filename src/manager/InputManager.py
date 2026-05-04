import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import App

class InputManager:
    """
    Gère le mapping des touches du jeu avec persistance.
    Permet de faire le lien entre une action (ex: 'up') et une touche pygame.
    """
    def __init__(self, game: "App"):
        self.game = game
        self.controls = self.game.save_manager.get_setting("controls")
        self.key_map = self._update_key_map()
        
    def _update_key_map(self) -> dict[str, int]:
        """Convertit les strings du JSON en constantes pygame.K_..."""
        mapping = {}
        for action, key_str in self.controls.items():
            # Conversion string -> constante pygame (ex: "z" -> pygame.K_z)
            key_const = getattr(pygame, f"K_{key_str.lower()}", None)
            if key_const is not None:
                mapping[action] = key_const
        return mapping

    def is_pressed(self, action: str) -> bool:
        """Vérifie si la touche associée à une action est actuellement pressée."""
        keys = pygame.key.get_pressed()
        key_const = self.key_map.get(action)
        if key_const is not None:
            return keys[key_const]
        return False

    def set_key(self, action: str, key_str: str) -> None:
        """Modifie la touche associée à une action et sauvegarde."""
        self.controls[action] = key_str.lower()
        self.game.save_manager.set_setting("controls", self.controls)
        self.key_map = self._update_key_map()
        print(f"Contrôle mis à jour : {action} -> {key_str}")

    def get_key_name(self, action: str) -> str:
        """Retourne le nom de la touche actuelle pour l'affichage (ex: 'Z')."""
        return self.controls.get(action, "?").upper()
