import pygame
from ui.UIElement import UIElement
from ui.UIButton import UIButton
from ui.UIText import UIText


class UICompose(UIElement):
    '''
            Permet de cree un pack de UIElement pour faire un Element compose\n
            x, y, w, h : argument de base d'un UIElement\n
            label_text : Titre de la stack\n
            sprite : pygame.Surface\n
            text_button : donner un text au button (facultatif)\n
            info_button : permet d'ajouter un petit bouton bleu en haut a droite de la stack pour afficher une description ou infos supplementaires\n
            ce text est a fournir via la methode : set_description(text) (voir methode pour plus d'info)
        '''
    def __init__(self, x: int, y: int, w: int, h: int, label_text: str, sprite: pygame.Surface, action_button, text_button: str, uid: str | None = None):
        super().__init__(x, y, w, h, uid)

        child_uid = f"{uid}_" if uid else ""
        pygame.draw.rect(self.image, (100, 100, 100), (0, 0, self.rect.w, self.rect.h), border_radius=15)
        pygame.draw.rect(self.image, (255, 0, 0), (0, 0, self.rect.w, self.rect.h), 4, 15)

        ## LABEL
        self.label = UIText(0, 10, label_text, size_text=50, uid=f"{child_uid}label")
        # Centrage horizontal
        self.label.rect.centerx = w // 2
        
        ## SPRITE
        sprite_w, sprite_h = sprite.get_size()
        self.sprite_display = UIElement((w - sprite_w) // 2, (h - sprite_h) // 2, sprite_w, sprite_h, uid=f"{child_uid}sprite")
        self.sprite_display.image = sprite
        
        ## BOUTON ACTION
        self.button = UIButton(0, 0, text_button, action_button, (25, 100, 155), size_text=25, uid=f"{child_uid}btn")
        # Positionnement : 15 pixels au dessus du bord bas, centré
        self.button.rect.centerx = w // 2
        self.button.rect.bottom = h - 15

        ## INFO BUTTON
        self.info_button = None
        self.info_text = ""
        
        self.add_child(self.label)
        self.add_child(self.sprite_display)
        self.add_child(self.button)

    
    def draw(self, surface):
        super().draw(surface)


    def set_info_button(self, text: str) -> None:
        ''' Ajoute dynamiquement le bouton info s'il y a une description '''
        self.info_text = text
        if not self.info_button:
            # Petit bouton rond
            btn_size = 25
            self.info_button = UIButton(
                self.rect.w - btn_size - 5, 5, btn_size, btn_size, 
                "i", self.show_description, (0, 150, 255), size_text=25, uid=f"{self.uid}_info"
            )
            self.add_child(self.info_button)

    
    def show_description(self):
        print(f"Info demandée : {self.info_text}")