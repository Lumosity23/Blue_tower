import json
import os
from typing import TYPE_CHECKING

from utils.path import resource_path as rp

if TYPE_CHECKING:
    from app import App


class SaveManager:
    """
    Gère la persistance des données du jeu (sauvegardes).
    Permet de stocker les paramètres (volume, etc.), le high score,
    et un historique des 3 dernières parties.
    """

    def __init__(self, game: "App"):
        self.game = game
        # Le chemin vers le fichier de sauvegarde (dans les assets ou à la racine)
        self.save_file = rp("src/save.json")

        # Structure de données par défaut si aucune sauvegarde n'existe
        self.default_data = {
            "settings": {
                "master_volume": 1.0,
                "music_volume": 1.0,
                "sfx_volume": 1.0,
                "mute": False,
                "show_fps": True,
                "controls": {"up": "z", "down": "s", "left": "q", "right": "d"},
            },
            "high_score": 0,
            "last_games": [],  # Liste des 3 dernières parties (ex: {"wave": 15, "score": 1500, "date": "2026-05-02"})
        }

        self.data = self.load_data()

        # On peut brancher des événements pour sauvegarder automatiquement
        self.game.eventManager.subscribe("SAVE_GAME", self.save_data)
        self.game.eventManager.subscribe("SAVE_SETTINGS", self.save_data)

    def load_data(self) -> dict:
        """Charge les données depuis le fichier JSON ou retourne les valeurs par défaut."""
        if not os.path.exists(self.save_file):
            print("Aucune sauvegarde trouvée. Création des données par défaut.")
            return self.default_data.copy()

        try:
            with open(self.save_file, "r") as f:
                data = json.load(f)
                # Fusionner avec les données par défaut pour éviter les clés manquantes si le format évolue
                merged_data = self.default_data.copy()
                merged_data.update(data)
                print("Sauvegarde chargée avec succès !")
                return merged_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erreur lors du chargement de la sauvegarde : {e}")
            return self.default_data.copy()

    def save_data(self) -> None:
        """Sauvegarde les données actuelles dans le fichier JSON."""
        try:
            with open(self.save_file, "w") as f:
                json.dump(self.data, f, indent=4)
            print("Données sauvegardées avec succès !")
        except IOError as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    # ==========================================
    # MÉTHODES POUR LES PARAMÈTRES (SETTINGS)
    # ==========================================
    def get_setting(self, key: str):
        return self.data["settings"].get(key, self.default_data["settings"].get(key))

    def set_setting(self, key: str, value) -> None:
        self.data["settings"][key] = value
        # self.save_data()  # On sauvegarde automatiquement à chaque changement (ou on peut le faire quand on quitte le menu)

    # ==========================================
    # MÉTHODES POUR LES STATS ET HISTORIQUE
    # ==========================================
    def update_high_score(self, score: int) -> bool:
        """Met à jour le high score si le nouveau score est meilleur. Retourne True si record battu."""
        if score > self.data["high_score"]:
            self.data["high_score"] = score
            self.save_data()
            return True
        return False

    def add_game_to_history(self, wave: int, score: int, date: str) -> None:
        """Ajoute une partie à l'historique et ne garde que les 3 dernières."""
        game_stats = {"wave": wave, "score": score, "date": date}

        # Ajoute au début de la liste (la plus récente en premier)
        self.data["last_games"].insert(0, game_stats)

        # Garde seulement les 3 dernières parties
        if len(self.data["last_games"]) > 3:
            self.data["last_games"] = self.data["last_games"][:3]

        self.save_data()
