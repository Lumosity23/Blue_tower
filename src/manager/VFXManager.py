from ui.UIFloatingText import UIFloatingText
from typing import TYPE_CHECKING, Any
import pygame

if TYPE_CHECKING:
    from main import App


class VFXManager:

    def __init__(self, game: "App"):
        
        self.game = game
        self.event = game.eventManager

        # Creation de notre pool de FT ( 30 pour l'instant )
        self.pool_FTC = [ UIFloatingText(0,0, "No text") for _ in range(30) ]
        self.active_element: list[UIFloatingText] = []

        # EndPoint ( API )
        self.event.subscribe("SHOW_FT", self.wake_up)

    

    def wake_up(self, mapping: dict[str, Any]) -> None:

        pos = mapping["xy"]
        text = str(mapping["text"])
        static = mapping.get("static", False)

        new_ft = None
        for ft in self.pool_FTC:
            if not ft.visible:
                new_ft = ft
                break
        
        if not new_ft:
            new_ft = UIFloatingText(*pos, text)
            self.pool_FTC.append(new_ft)
        
        else:
            new_ft.reset(*pos, text)

        new_ft.active = True
        new_ft.visible = True
        new_ft.static = static
        self.active_element.append(new_ft)

    
    def update(self, dt) -> None:
        
        dead_element = []
        for ft in self.active_element:
            # On verifie si fin de vie atteint
            if not ft.update(dt):
                dead_element.append(ft)

        # On retire tout les element qui sont "morts"
        for e in dead_element:
            self.active_element.remove(e)


    def draw(self, screen: pygame.Surface) -> None:
        
        
        offset = self.game.sceneManager.main_camera.offset.xy

        for e in self.active_element:
            if e.static:
                e.draw(screen, (0, 0))
                continue
            e.draw(screen, offset)

        