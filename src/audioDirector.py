from typing import TYPE_CHECKING
from manager.AudioManager import AudioManager
import pygame

if TYPE_CHECKING:
    from main import App


class AudioDirector:

    def __init__(self, game: "App"):
        
        self.game = game
        self.event_manager = game.eventManager
        self.audio_manager = AudioManager(game)
        self.event_to_track = {
            "CLICK_BUTTON": self.button,
            "MENU": self.menu,
            "NEW_GAME": self.in_game,
            "NEW_WAVE": self.prepare_next_wave,
            "TOGGLE_MUTE": self.mute
        }

        # On s'inscrit a toute le event annoncer au debut
        self.set_subscription()

    
    def set_subscription(self) -> None:

        for event, callback in self.event_to_track.items():
            self.event_manager.subscribe(event, callback)
    

    def button(self, sound) -> None:
        if sound == "click_default":
            sound = "UI_CLICK"

        self.event_manager.publish("PLAY_SFX", sound)
    

    def menu(self) -> None:
        if not self.audio_manager.is_playing() or self.game.state != "MENU":
            self.event_manager.publish("PLAY_MUSIC_LOOP", "MENU_THEME")
    

    def in_game(self) -> None:    
        if not self.audio_manager.is_playing() or self.game.state != "PLAYING": 
            self.event_manager.publish("PLAY_MUSIC_LOOP", "MENU_THEME")


    def mute(self, is_mute=False) -> None:
        if is_mute:
            self.event_manager.publish("SET_MASTER_VOLUME", 0.0)
        else:
            self.event_manager.publish("SET_MASTER_VOLUME", 0.5)


    # Dans ton AudioDirector ou AudioManager
    def prepare_next_wave(self, theme_name: str="GAME_THEME"):
        # 1. On baisse la musique (Fade out de 500ms pour plus de douceur)
        self.event_manager.publish("MUSIC_FADEOUT", 500)

        # 2. On joue le son d'alerte sur un canal SFX
        # On utilise le bus pour être cohérent avec ton code
        self.event_manager.publish("PLAY_SFX", "NEW_WAVE")

        # 3. On programme le retour de la musique
        # On attend par exemple 2 secondes (2000 ms) avant de relancer le thème
        pygame.time.set_timer(pygame.USEREVENT + 1, 2000, loops=1)
        self.next_theme = theme_name
