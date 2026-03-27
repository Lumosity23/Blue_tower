import os
import sys

def resource_path(relative_path):
    """ Gestion des chemins pour le mode script et le mode .exe """
    try:
        # Dossier temporaire de PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # On remonte de 'src/utils' vers la racine du projet
        # __file__ est le chemin de paths.py, donc on remonte 2 fois
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)