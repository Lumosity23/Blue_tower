import pygame
import random
from enemy import Enemie
from settings import Settings
from UIManager import UIManager


class WaveManager():
    def __init__(self, game: object):
        # Cree un instance de notre app
        self.game = game
        self.last_spawn_time = pygame.time.get_ticks() # heure de demarage (ms)
        self.cooldown = 2000 # (ms) -> 2 (sec)
        self.wave_difficulty = 3 # Null
        self.wave_number = 0
        self.first_round = True
        self.end_wave = False
    

    def update(self):

        # On recupere le temps ecouler jusqu'a maintenant
        current_time = pygame.time.get_ticks()

        # Seulement pour la premier vague
        if self.first_round:
            self.spawn_wave()
            self.first_round = False
            self.last_spawn_time = current_time

        # Fin de vague
        if len(self.game.enemies) == 0 and self.end_wave == False:
            self.end_wave = True
            self.last_spawn_time = current_time

        # Verification du temps apres fin de vague
        if current_time - self.last_spawn_time > self.cooldown and self.end_wave == True :
            # Creation de la vague
            self.spawn_wave()

            # Chamgement de difficulter si quota de vague atteint <<<<  A REVOIR CAR COMME IL FAUT 
            if self.wave_number in Settings.DIFFICULTY:
                self.wave_difficulty = Settings.DIFFICULTY[self.wave_number]

            # On set les nouveau reperes
            self.last_spawn_time = current_time
            self.end_wave = False
            
            
    def spawn_wave(self):
        
        enemies = []
        # creation des ennemis
        for _ in range(self.wave_difficulty):
            enemy = self.enemy_maker()
            enemies.append(enemy)

        # Ajout des ennemis pour la logic et le rendu
        self.game.enemies.add(enemies)
        self.game.all_sprites.add(enemies)

        # Incrementation pour changer la diff et le temps de preparation entre chaque vague
        self.wave_number += 1
        self.cooldown += 1000 # ajout d'une seconde apres chaque vague


    def enemy_maker(self):
        good_pos = False

        # Securiter pour ne pas avoir d'ennemis sur le joueur
        while not good_pos:
            # Position aleatoire
            posx = random.randint(Settings.CELL_SIZE, Settings.SCREEN_WIDTH - Settings.CELL_SIZE)
            posy = random.randint(Settings.CELL_SIZE, Settings.SCREEN_HEIGHT - Settings.CELL_SIZE)

            # Verifier que l'ennemis n'est pas trop procher du joueur
            distance0 = pygame.math.Vector2((posx, posy)).distance_to(self.game.player.pos)
            distance1 = pygame.math.Vector2((posx, posy)).distance_to(self.game.kernel.pos)
            if distance0 > Settings.SECURITY_ZONE and distance1 > Settings.SECURITY_ZONE:
                good_pos = True

        # size aleatoire
        radius = random.randint(15, 32)
        size = radius * 2, radius * 2

        # Retourner l'objet ennemi
        return Enemie(posx, posy, size)
    

    def reset(self):
        self.wave_difficulty = 0
        self.wave_number = 0