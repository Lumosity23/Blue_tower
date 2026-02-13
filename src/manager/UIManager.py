import pygame
import os
import json
from ui.UIElement import UIElement
from ui.panel.ShopPanel import ShopPanel
from ui.panel.OSD import OSD
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class UIManager():
    
    def __init__(self, game: "App"):
        pygame.font.init()
        self.game = game
        self.st = self.game.st
        self.edit_mode = False
        self.layout_path = self.st.UI_LAYOUT_PATH
        # Init de notre bloc logic pour le UI
        self.root = UIElement(0, 0, self.st.SCREEN_WIDTH, self.st.SCREEN_HEIGHT, game)
        self.root.image.set_alpha(0)
        
        # pour le debug pour l'instant
        self.selected_element = None
        
        # Init de element UI visuel
        self.shop_panel = ShopPanel(self.game)
        self.OSD = OSD(0, 0, 0, 0, game)

        # Ajout des enfants
        self.root.add_child(self.shop_panel)
        self.root.add_child(self.OSD)

        # Declaration des event sur ecoute
        # self.game.eventManager.subscribe("OPEN_UPGRADE_PANEL", self.upgrade_panel.show)

        self.layout = self.load_layout()

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        print(f" UI Edit Mode: {'ON' if self.edit_mode else 'OFF'}")


    def load_layout(self) -> dict:

        if not os.path.exists(self.layout_path):
            return {}
        
        try:
            with open(self.layout_path, "r") as f:
                return json.load(f)
            
        except json.JSONDecodeError:
            print(" Erreur de lecture du JSON, retour à vide.")
            return {}
    

    def save_layout(self):
        """Parcourt l'arbre UI et sauvegarde les positions."""
        print(" Sauvegarde du layout en cours...")
        
        # On va remplir ce dictionnaire
        data_to_save = {}
        
        # Fonction récursive interne pour visiter tout l'arbre
        def collect_data(element: "UIElement"):
            # Si l'élément a un ID, on sauvegarde ses infos
            if element.uid:
                data_to_save[element.uid] = {
                    "x": element.rect.x,
                    "y": element.rect.y,
                    "w": element.rect.width,
                    "h": element.rect.height
                }
            
            # On visite les enfants
            
            for child in element.children:
                collect_data(child)

        # On lance la collecte depuis la racine
        collect_data(self.root)

        # On écrit dans le fichier
        with open(self.layout_path, 'w') as f:
            json.dump(data_to_save, f, indent=4) # indent=4 pour que ce soit joli à lire
            
        print(f"Layout sauvegardé dans {self.layout_path} !")
    

    def handle_event(self, event):
        # 1. Activation du mode avec F1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.toggle_edit_mode()
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            if not self.shop_panel.visible:
                self.shop_panel.show()
            else : self.shop_panel.hide()

        # SI ON EST EN MODE ÉDITION : ON DÉPLACE 
        if self.edit_mode:
            return self.handle_editor_event(event)
        
        # Sinon, comportement normal (clic boutons...)
        return self.root.handle_event(event)
    

    def handle_editor_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        # Sauvgarde de l'OSD via CTRL + S
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.save_layout()
                return True
            
        # A. Clic Gauche : On attrape un élément
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # On cherche l'élément le plus profond sous la souris
            found = self.find_element_under_mouse(self.root, mouse_pos)
            if found and found != self.root: # On ne bouge pas la racine !
                self.selected_element = found
                # On calcule le décalage pour que l'objet ne saute pas au coin de la souris
                self.offset_x = mouse_pos[0] - found.rect.x
                self.offset_y = mouse_pos[1] - found.rect.y
                print(f"Saisi : {type(found).__name__}")
                return True

        # B. Mouvement Souris : On déplace
        elif event.type == pygame.MOUSEMOTION:
            if self.selected_element:
                # On met à jour la position RELATIVE (rect.x/y)
                # Attention : Si l'élément a un parent, il faut soustraire la position du parent !
                parent_x = 0
                parent_y = 0
                if self.selected_element.parent:
                    parent_rect = self.selected_element.parent.get_absolute_rect()
                    parent_x = parent_rect.x
                    parent_y = parent_rect.y
                
                # Nouvelle position locale
                new_x = mouse_pos[0] - self.offset_x # - parent_x
                new_y = mouse_pos[1] - self.offset_y # - parent_y
                
                # Application (avec Snapping à la grille 10px pour être propre ?)
                self.selected_element.rect.x = round(new_x / 10) * 10
                self.selected_element.rect.y = round(new_y / 10) * 10
                return True

        # C. Relâchement : On lâche et ON IMPRIME LE CODE
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.selected_element:
                el = self.selected_element
                print(f"NOUVELLE POSITION pour {type(el).__name__}: x={el.rect.x}, y={el.rect.y}")
                self.selected_element = None
                return True
        
        return False


    def find_element_under_mouse(self, parent: "UIElement", pos):
        # Récursion pour trouver l'élément le plus haut (dernier dessiné)
        # On parcourt à l'envers
        child: "UIElement"
        for child in reversed(parent.children):
            # D'abord on regarde dans les enfants des enfants
            found = self.find_element_under_mouse(child, pos)
            if found: return found
            
            # Sinon on regarde l'enfant lui-même
            if child.get_absolute_rect().collidepoint(pos):
                return child
        
        # Si aucun enfant, on regarde le parent lui-même
        if parent.get_absolute_rect().collidepoint(pos):
            return parent
        return None