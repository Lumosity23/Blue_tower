import os
import sys


def resource_path(relative_path):
    """ Gestion des chemins pour le mode script et le mode .exe """
    # 1. On cherche d'abord le chemin de PyInstaller
    base_path = getattr(sys, '_MEIPASS', None)

    # 2. Si on n'est pas en mode .exe, on calcule le chemin manuellement
    if base_path is None:
        # On part du dossier où se trouve path.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # On remonte de 2 niveaux (utils -> src -> racine)
        base_path = os.path.join(current_dir, "..", "..")

    # 3. Sécurité ultime : on s'assure que base_path n'est pas None
    if base_path is None:
        base_path = os.path.abspath(".")

    # Nettoyage du chemin final
    if base_path is None or relative_path is None:
        raise TypeError(f"ERREUR : base_path est {base_path} et relative_path est {relative_path}")
    
    full_path = os.path.join(base_path, relative_path)
    return os.path.normpath(full_path)