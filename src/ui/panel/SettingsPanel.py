from typing import TYPE_CHECKING

from ui.element.UIButton import UIButton
from ui.element.UIPanel import UIPanel
from ui.element.UIScroll import UIScroll
from ui.element.UIStat import UIStat
from ui.element.UISwitch import UISwitch
from ui.element.UIText import UIText

if TYPE_CHECKING:
    from main import App


class Settings(UIPanel):
    def __init__(self, game: "App"):
        self.game = game
        self.st = self.game.st
        # On centre le panel
        super().__init__(
            0,
            0,
            self.st.SCREEN_WIDTH,
            self.st.SCREEN_HEIGHT,
            color=(50, 50, 50),
            uid="SettingsPanel",
        )

        self.channels = {"Master": "masterV", "Music": "musicV", "SFX": "sfxV"}

        self.last_state = "MENU"
        self.set_label("Settings", 150)

        # --- DEMO UISCROLL ---
        # On crée une zone scrollable sur la gauche
        scroll_width, scroll_height = 400, 600
        self.demo_scroll = UIScroll(
            50,
            250,
            scroll_width,
            scroll_height,
            color=(40, 40, 40),
            uid="Settings_DemoScroll",
        )

        # On y ajoute plein d'éléments pour tester le scroll
        for i in range(25):
            y_pos = 10 + i * 60
            txt = UIText(
                20, y_pos, f"Option {i + 1}", size_text=30, uid=f"scroll_txt_{i}"
            )
            btn = UIButton(
                220,
                y_pos,
                "TEST",
                lambda val=i: print(f"Action sur l'élément {val + 1}"),
                size_text=25,
                uid=f"scroll_btn_{i}",
            )

            self.demo_scroll.add_child(txt)
            self.demo_scroll.add_child(btn)

        self.add_child(self.demo_scroll)

        # Calcul de la position de départ (sous le titre)
        center_x = self.rect.centerx
        current_y = self.label.rect.bottom + 250

        for channel_name, attr_name in self.channels.items():
            audio_manager = self.game.audio_director.audio_manager
            ptr = self.get_attribut_pointer(attr_name, audio_manager)

            vol_channel = UIStat(0, 0, f"{self.uid}_{channel_name}")
            vol_channel.custom_setup(center_x - 250, current_y + 10, channel_name, ptr)
            vol_channel.stat_value.rect.midleft = (
                vol_channel.rect.width,
                vol_channel.rect.height // 2,
            )

            # 2. Boutons + et -
            # On utilise une lambda pour passer l'attribut spécifique (ex: "musicV")
            btn_plus = UIButton(
                center_x + 90,
                current_y,
                "+",
                lambda a=attr_name: self.change_volume(a, 5),
                (255, 0, 0),
                uid=f"{self.uid}_plus_{channel_name}",
            )

            btn_moins = UIButton(
                center_x + 200,
                current_y,
                "-",
                lambda a=attr_name: self.change_volume(a, -5),
                (0, 0, 255),
                uid=f"{self.uid}_moins_{channel_name}",
            )

            # On ajoute les enfants
            self.add_child(vol_channel)
            self.add_child(btn_plus)
            self.add_child(btn_moins)

            current_y += 80  # Espace entre les lignes

        # --- SWITCH MUTE ---
        self.mute_btn = UISwitch(
            center_x - 250,
            current_y,
            "Mute :",
            self.toggle_mute,
            start_state=False,
            size_text=50,
            color_on=(50, 150, 50),
            color_off=(150, 50, 50),
            uid=f"{self.uid}_MuteBtn",
        )
        self.add_child(self.mute_btn)

        # 3. BOUTON RETOUR (en bas)
        back_btn = UIButton(
            center_x - 50,
            self.rect.bottom - 100,
            "BACK",
            self.go_back,
            (100, 100, 100),
            uid="Settings_Back",
        )
        self.add_child(back_btn)

    def toggle_mute(self) -> None:
        """Gère l'activation/désactivation du mode silencieux."""
        # Bascule l'état via la propriété state du switch
        is_muted = self.mute_btn.state
        print(f"Mute actif : {is_muted}")
        # Publie l'événement pour que le reste du jeu s'adapte
        self._EVENTBUS.publish("TOGGLE_MUTE", is_muted)

    def change_volume(self, attr_name: str, amount: int) -> None:
        """Gère l'augmentation ou la diminution pour n'importe quel canal"""
        audio_manager = self.game.audio_director.audio_manager

        current_float = getattr(audio_manager, attr_name)
        current_int = int(round(current_float * 100))

        # On applique la modification et on clamp entre 0 et 100
        val = current_int + amount
        if val > 100:
            print("trop fort")
            self._EVENTBUS.publish("PLAY_SFX", "ERROR")
        new_int = max(0, min(100, val))

        # On reconvertit en float 0.0 -> 1.0 avec 2 décimales
        new_float = round(new_int / 100, 2)

        setattr(audio_manager, attr_name, new_float)

        # On notifie le bus d'événement pour mettre à jour le volume réel des sons
        name = f"SET_{attr_name.upper()}"  # Ex : SET_MASTERV
        event_name = f"{name[:-1]}_VOLUME"  # Ex: SET_MASTER_VOLUME
        self._EVENTBUS.publish(event_name, new_float)

    def go_back(self) -> None:
        """Ferme les settings et retourne au menu pause"""
        # Ici, utilise ton système de SceneManager ou EventBus pour changer de panel
        self._EVENTBUS.publish(self.last_state)
        self.visible = False
        if self.game.state == "PAUSE":
            self._EVENTBUS.publish("SHOW_OSD")

    def get_attribut_pointer(self, attr, element):
        if attr is None:
            return lambda: None  # Retourne une fonction qui renvoie N

        if hasattr(element, attr):
            # On retourne une fonction (un "getter")
            return lambda name=attr: getattr(element, name)

        print(f"aucun attribut du nom de {attr} sur {element.__class__.__name__}")
        return lambda: None
