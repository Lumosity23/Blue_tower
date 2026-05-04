from typing import TYPE_CHECKING

import pygame

from utils.path import resource_path as rp

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
        self.masterV = self.game.save_manager.get_setting("master_volume")
        self.musicV = self.game.save_manager.get_setting("music_volume")
        self.sfxV = self.game.save_manager.get_setting("sfx_volume")

        # To play musique in game
        self.event.subscribe("PLAY_SFX", self.play_sfx)
        self.event.subscribe("PLAY_MUSIC", self.play_music)
        self.event.subscribe("PLAY_MUSIC_LOOP", self.play_music_in_bg)
        self.event.subscribe("STOP_SFX", self.stop_sfx)
        self.event.subscribe("STOP_MUSIC", self.stop_music)
        self.event.subscribe("TOGGLE_MUTE", self.mute)

        # To set Volume ( eg: in settings )
        self.event.subscribe("SET_MASTER_VOLUME", self.set_volume_master)
        self.event.subscribe("SET_SFX_VOLUME", self.set_volume_sfx)
        self.event.subscribe("SET_MUSIC_VOLUME", self.set_volume_music)

        # On applique immédiatement les volumes au démarrage (respecte le mute persistant)
        self.set_volume_master(None)

    def _load_musics(self) -> dict[str, str]:
        """Renvoie le nom de la musique et son chemin d'acces"""
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

    def set_volume_master(self, volume_val: float = None) -> None:
        if volume_val is not None:
            if volume_val > 1:
                volume_val /= 100
            self.masterV = volume_val
            self.game.save_manager.set_setting("master_volume", self.masterV)

        # Calcul du volume effectif (0 si mute est ON dans les saves)
        is_muted = self.game.save_manager.get_setting("mute")
        effective_master = 0.0 if is_muted else self.masterV

        # Met à jour le volume de la musique
        pygame.mixer.music.set_volume(self.musicV * effective_master)

        # Met à jour le volume de tous les SFX
        new_sfx_vol = self.sfxV * effective_master
        for s_name, sound in self.sounds.items():
            sound.set_volume(new_sfx_vol)

    def set_volume_sfx(self, volume_val: float = None) -> None:
        if volume_val is not None:
            if volume_val > 1:
                volume_val /= 100
            self.sfxV = volume_val
            self.game.save_manager.set_setting("sfx_volume", self.sfxV)

        is_muted = self.game.save_manager.get_setting("mute")
        effective_master = 0.0 if is_muted else self.masterV
        new_vol = self.sfxV * effective_master

        for s_name, sound in self.sounds.items():
            sound.set_volume(new_vol)

    def set_volume_music(self, volume_val: float = None) -> None:
        if volume_val is not None:
            if volume_val > 1:
                volume_val /= 100
            self.musicV = volume_val
            self.game.save_manager.set_setting("music_volume", self.musicV)

        is_muted = self.game.save_manager.get_setting("mute")
        effective_master = 0.0 if is_muted else self.masterV
        new_vol = self.musicV * effective_master

        pygame.mixer.music.set_volume(new_vol)

    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()

    def mute(self, is_mute: bool = False) -> None:
        # On enregistre l'état dans le SaveManager
        self.game.save_manager.set_setting("mute", is_mute)
        # On déclenche une mise à jour des volumes réels sans changer les valeurs de base
        self.set_volume_master(None)
