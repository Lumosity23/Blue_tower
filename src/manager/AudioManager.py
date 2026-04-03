import pygame
from utils.path import resource_path as rp
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class AudioManager:

    def __init__(self, game: "App"):
        
        self.game = game
        self.st = game.st
        self.event = game.eventManager
        self.musics = self._load_musics()
        self.sounds = self._load_sfx()
        
        # Volume settings
        self.masterV = 0.5
        self.musicV = 1.0
        self.sfxV = 1.0

        # To play musique in game
        self.event.subscribe("PLAY_SFX", self.play_sfx)
        self.event.subscribe("PLAY_MUSIC", self.play_music)
        self.event.subscribe("PLAY_MUSIC_LOOP", self.play_music_in_bg)
        self.event.subscribe("STOP_SFX", self.stop_sfx)
        self.event.subscribe("STOP_MUSIC", self.stop_music)

        # To set Volume ( eg: in settings )
        self.event.subscribe("SET_MASTER_VOLUME", self.set_volume_master)
        self.event.subscribe("SET_SFX_VOLUME", self.set_volume_sfx)
        self.event.subscribe("SET_MUSIC_VOLUME", self.set_volume_music)
        
        # Applique le volumede base a nos sons
        self.set_volume_master(0.5)


    def _load_musics(self) -> dict[str, str]:
        ''' Renvoie le nom de la musique et son chemin d'acces '''
        musics = {}
        # On setup le chemin correctement pour le Release du jeu
        for name, path in self.game.st.MUSIC_PATH.items():
            musics[name] = rp(path)
        
        return musics


    def _load_sfx(self) -> dict[str, pygame.mixer.Sound]:
        sounds = {}
        # Load les differents SFX depuis les settings.py
        for sound, path in self.st.SOUND_PATH.items(): 
            # On setup le chemin correctement pour le Release du jeu
            sounds[sound] = pygame.mixer.Sound(rp(path))

        return sounds
    

    def play_sfx(self, sfx_name) -> None:
        # Verifier que le son existe
        if sfx_name in self.sounds:
            self.sounds[sfx_name].play()


    def play_music(self, music_name, loops=0) -> None:
        # On verifie que la musique existe
        if music_name in self.musics:
            pygame.mixer.music.load(self.musics[music_name])
            pygame.mixer.music.play(loops)


    def play_music_in_bg(self, music_name) -> None:
        self.play_music(music_name, -1)


    def stop_sfx(self) -> None:
        # Pas encore implementer ( pas super utile )
        pass


    def stop_music(self) -> None:
        pygame.mixer.music.stop()
    

    def set_volume_master(self, volume_val: float=0) -> None:
        
        if volume_val is None:
            return

        else:
            if volume_val > 1:
                # On imagine que la personne a donner en % au lieu de 0.0 -> 1.0
                volume_val /= 100
        
        self.masterV = volume_val
        
        # Met a jour le volume des autre element audio ( MUSIQUE, SFX )
        self.set_volume_music(volume_val=None)
        self.set_volume_sfx(volume_val=None)


    def set_volume_sfx(self, volume_val: float=0) -> None:
        
        # Pour la mise a jour du Volume depuis le master
        if volume_val is None:
            volume_val = self.sfxV
        else:
            if volume_val > 1:
                # On imagine que la personne a donner en % au lieu de 0.0 -> 1.0
                volume_val /= 100
        
        self.sfxV = volume_val

        # On affecte le volume par celui du MASTER
        new_vol = self.sfxV * self.masterV

        for s_name, sound in self.sounds.items():
            sound.set_volume(new_vol)


    def set_volume_music(self, volume_val: float=0) -> None:
        
        # Pour la mise a jour du Volume depuis le master
        if volume_val is None:
            volume_val = self.musicV

        else:
            if volume_val > 1:
                # On imagine que la personne a donner en % au lieu de 0.0 -> 1.0
                volume_val /= 100

        self.musicV = volume_val

        new_vol = self.musicV * self.masterV

        pygame.mixer.music.set_volume(new_vol)
    

    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()