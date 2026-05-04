from typing import TYPE_CHECKING

import pygame

from ui.element.UIButton import UIButton
from ui.element.UIPanel import UIPanel
from ui.element.UIScroll import UIScroll
from ui.element.UISlider import UISlider
from ui.element.UISwitch import UISwitch
from ui.element.UIText import UIText

if TYPE_CHECKING:
    from main import App


class Settings(UIPanel):
    def __init__(self, game: "App"):
        self.game = game
        self.st = self.game.st

        # On occupe tout l'écran avec un fond sombre style AAA
        super().__init__(
            0,
            0,
            self.st.SCREEN_WIDTH,
            self.st.SCREEN_HEIGHT,
            color=(30, 30, 35),
            uid="SettingsPanel",
        )

        self.last_state = "MENU"
        self.set_label("SETTINGS", 120)

        # --- CRÉATION DU SCROLL PRINCIPAL ---
        scroll_w = self.st.SCREEN_WIDTH - 100
        scroll_h = self.st.SCREEN_HEIGHT - 200
        self.scroll = UIScroll(
            50, 100, scroll_w, scroll_h, color=(40, 40, 45), uid="Settings_Scroll"
        )
        self.add_child(self.scroll)

        self.rebind_action = None
        self._init_settings_content(scroll_w)

        # --- BOUTON RETOUR (Fixé en bas) ---
        back_btn = UIButton(
            self.st.SCREEN_WIDTH // 2 - 150,
            self.rect.bottom - 100,
            "SAVE & BACK",
            self.go_back,
            (100, 100, 100),
            uid="Settings_Back",
        )
        self.add_child(back_btn)

    def _init_settings_content(self, scroll_w: int):
        """Initialise les réglages avec labels à gauche et contrôles à droite."""
        current_y = 50
        row_height = 100
        control_x_right = scroll_w - 500

        # --- AUDIO SECTION ---
        self._add_section_title("AUDIO", current_y)
        current_y += 80

        for vol_type in ["master", "music", "sfx"]:
            label = f"{vol_type.capitalize()} Volume"
            initial = self.game.save_manager.get_setting(f"{vol_type}_volume")
            slider = UISlider(
                control_x_right,
                current_y,
                400,
                40,
                initial_value=initial,
                on_change_callback=lambda v, t=vol_type: self.game.eventManager.publish(
                    f"SET_{t.upper()}_VOLUME", v
                ),
                uid=f"Setting_{vol_type}_Slider",
            )
            self._add_setting_row(label, slider, current_y)
            current_y += row_height

        # Mute
        is_mute = self.game.save_manager.get_setting("mute")
        self._add_setting_row(
            "Mute All Sounds",
            UISwitch(
                control_x_right + 300,
                current_y,
                "",
                self.toggle_mute,
                start_state=is_mute,
                uid="Setting_Mute_Switch",
            ),
            current_y,
        )
        current_y += row_height + 50

        # --- DISPLAY SECTION ---
        self._add_section_title("DISPLAY", current_y)
        current_y += 80

        show_fps = self.game.save_manager.get_setting("show_fps")
        self._add_setting_row(
            "Show FPS Counter",
            UISwitch(
                control_x_right + 300,
                current_y,
                "",
                self.toggle_fps,
                start_state=show_fps,
                uid="Setting_FPS_Switch",
            ),
            current_y,
        )
        current_y += row_height + 50

        # --- CONTROLS SECTION ---
        self._add_section_title("CONTROLS", current_y)
        current_y += 80

        for action in ["up", "down", "left", "right"]:
            key_name = self.game.input_manager.get_key_name(action)
            btn_key = UIButton(
                control_x_right + 150,
                current_y,
                key_name,
                lambda a=action: self.start_rebind(a),
                (60, 60, 60),
                size_text=55,
                uid=f"Btn_Rebind_{action}",
            )
            self._add_setting_row(f"Move {action.capitalize()}", btn_key, current_y)
            current_y += row_height

        current_y += 50

        # --- DATA SECTION ---
        self._add_section_title("DATA", current_y)
        current_y += 80

        self._add_setting_row(
            "Clear Save Data",
            UIButton(
                control_x_right + 200,
                current_y,
                "RESET",
                lambda: print("Resetting Save..."),
                (150, 50, 50),
                size_text=30,
                uid="Setting_Reset_Btn",
            ),
            current_y,
        )

    def _add_section_title(self, text: str, y: int):
        title = UIText(
            50,
            y,
            text,
            size_text=50,
            color=(200, 200, 255),
            align="topleft",
            uid=f"Title_{text}",
        )
        self.scroll.add_child(title)

    def _add_setting_row(self, label_text: str, control_element: any, y: int):
        """Ajoute une ligne avec label à gauche et contrôle à droite."""
        label = UIText(
            80,
            y + 20,
            label_text,
            size_text=40,
            align="midleft",
            uid=f"Label_{label_text.replace(' ', '_')}",
        )
        self.scroll.add_child(label)
        self.scroll.add_child(control_element)

    def toggle_mute(self) -> None:
        for child in self.scroll.children:
            if child.uid == "Setting_Mute_Switch":
                is_muted = child.state
                self.game.save_manager.set_setting("mute", is_muted)
                self._EVENTBUS.publish("TOGGLE_MUTE", is_muted)
                break

    def toggle_fps(self) -> None:
        for child in self.scroll.children:
            if child.uid == "Setting_FPS_Switch":
                show_fps = child.state
                self.game.save_manager.set_setting("show_fps", show_fps)
                break

    def start_rebind(self, action: str) -> None:
        self.rebind_action = action
        for child in self.scroll.children:
            if child.uid == f"Btn_Rebind_{action}":
                child.set_text("PRESS KEY...")
                break

    def handle_event(self, event: pygame.event.EventType) -> bool:
        if self.rebind_action and event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            self.game.input_manager.set_key(self.rebind_action, key_name)
            for child in self.scroll.children:
                if child.uid == f"Btn_Rebind_{self.rebind_action}":
                    child.set_text(key_name.upper())
                    break
            self.rebind_action = None
            return True
        return super().handle_event(event)

    def go_back(self) -> None:
        self._EVENTBUS.publish(self.last_state)
        self._EVENTBUS.publish("SAVE_SETTINGS")
        self.visible = False
        if self.game.state == "PAUSE":
            self._EVENTBUS.publish("SHOW_OSD")
