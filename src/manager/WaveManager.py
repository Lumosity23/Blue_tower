import pygame
import random
from entities.enemy import Enemie
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class WaveManager:


    def __init__(self, game: "App"):
        # Cree un instance de notre app
        self.game = game
        self.last_spawn_time = pygame.time.get_ticks() # heure de demarage (ms)
        self.cooldown = 2000 # (ms) -> 2 (sec)
        self.wave_difficulty = 3 # Null
        self.wave_number = 0
        self.first_round = True
        self.end_wave = False

        self.dpg = 10           # Difficulties Point Global 
        self.status_point = 1   # Influence la puissance des ennemis 
        self.spawn_point = 1    # Influence le nombre d'ennemis 
        self.gold_point = 1     # Influence les gains d'argent

        self.game.eventManager.subscribe("NEW_GAME", self.reset)   


    def update(self, dt):

        # On recupere le temps ecouler jusqu'a maintenant
        current_time = pygame.time.get_ticks()

        # Seulement pour la premier vague
        if self.first_round:
            self.spawn_wave()
            self.first_round = False
            self.last_spawn_time = current_time

        # Fin de vague
        if len(self.game.sceneManager.entityManager.get_entities("ENEMY")) == 0 and self.end_wave == False:
            self.end_wave = True
            self.last_spawn_time = current_time

        # Verification du temps apres fin de vague
        if current_time - self.last_spawn_time > self.cooldown and self.end_wave == True :
            # Creation de la vague
            self.spawn_wave()

            # Chamgement de difficulter si quota de vague atteint <<<<  A REVOIR CAR COMME IL FAUT 
            if self.wave_number in self.game.st.DIFFICULTY:
                self.wave_difficulty = self.game.st.DIFFICULTY[self.wave_number]

            # On set les nouveau reperes
            self.last_spawn_time = current_time
            self.end_wave = False
            
            
    def spawn_wave(self):
        """ Déclenche une vague en utilisant le Pooling et le DDA """
        
        # 1. Calcul du nombre d'ennemis (CPT) selon la formule du papier 
        # CPT = 20 + (30 * DPG / 100) + Spawn_Point
        cpt = 20 + (30 * self.dpg / 100) + self.spawn_point
        
        # 2. Spawn des unités via l'EntityManager (Pooling)
        for _ in range(int(cpt)):
            posx, posy, size = self.get_enemy_config()
            
            # On demande à l'EntityManager de nous donner un ennemi (neuf ou recyclé)
            enemy: "Enemie" = self.game.sceneManager.entityManager.spawn(Enemie, posx, posy, size=size, game=self.game)
            
            # 3. Ajustement de la santé selon la formule DDA [cite: 191]
            # %HM = Base_HP * Status_Point + (20% de DPG)
            base_hp = self.game.st.ENEMIE_STATS["hp"]
            enemy.max_hp = base_hp * self.status_point + (20 * self.dpg / 100)
            enemy.current_hp = enemy.max_hp

        # Logique de progression classique
        self.wave_number += 1
        # Le papier suggère que le DDA remplace l'incrément manuel, 
        # mais on peut garder un petit cooldown de confort.
        self.cooldown += 1000 

    def get_enemy_config(self):
        """ Calcule une position et une taille valide (Ancien enemy_maker) """
        good_pos = False
        posx, posy = 0, 0

        while not good_pos:
            posx = random.randint(self.game.st.CELL_SIZE, self.game.st.SCREEN_WIDTH - self.game.st.CELL_SIZE)
            posy = random.randint(self.game.st.CELL_SIZE, self.game.st.SCREEN_HEIGHT - self.game.st.CELL_SIZE)

            # Sécurité : distance minimale avec le joueur et le kernel
            dist_player = pygame.math.Vector2(posx, posy).distance_to(self.game.player.pos)
            dist_kernel = pygame.math.Vector2(posx, posy).distance_to(self.game.kernel.pos)
            
            if dist_player > 100 and dist_kernel > 100:
                good_pos = True

        radius = random.randint(15, 30)
        return posx, posy, (radius * 2, radius * 2)
    

    def reset(self):
        self.wave_difficulty = 0
        self.wave_number = 0
    

    def nearest_enemy(self, pos_node: tuple) -> Enemie:

        shortest_lenght = (float("inf"),None)
        enemy: Enemie
        for enemy in self.game.sceneManager.entityManager.get_entities("ENEMY"):
            lenght = pygame.Vector2((pos_node)).distance_to(enemy.pos)
            if lenght < shortest_lenght[0]:
                shortest_lenght = lenght, enemy
        return shortest_lenght[1]
    

    def handle_event(self, event) -> bool:
        return False

    def draw(self, screen) -> None:
        return