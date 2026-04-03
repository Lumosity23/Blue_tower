import pygame
import random
import math 
from entities.enemy import Enemie
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

class WaveManager:


    def __init__(self, game: "App"):
        # Cree un instance de notre app
        self.game = game
        self.last_spawn_time = pygame.time.get_ticks() # heure de demarage (ms)
        self.cooldown = 5 # (ms) -> 2 (sec)
        self.wave_difficulty = 3 # Null
        self.wave_number = 0
        self.first_round = True
        self.end_wave = True
        self.spawn_area = (0, 0)
        self.timers = {self.cooldown : 0}

        self.dpg = 10           # Difficulties Point Global 
        self.status_point = 1   # Influence la puissance des ennemis 
        self.spawn_point = 1    # Influence le nombre d'ennemis 
        self.gold_point = 1     # Influence les gains d'argent

        self.time_before_new_wave = 5
        self.game.eventManager.subscribe("NEW_GAME", self.reset)   


    def update(self, dt):

        # Verification du temps apres fin de vague
        if self.end_wave == True :
            if self.delay(self.cooldown, dt):
                self.game.eventManager.publish("HIDE_COOLDOWN")
                # Creation de la vague
                self.spawn_wave()

                # Chamgement de difficulter si quota de vague atteint <<<<  A REVOIR CAR COMME IL FAUT 
                if self.wave_number in self.game.st.DIFFICULTY:
                    self.wave_difficulty = self.game.st.DIFFICULTY[self.wave_number]

                # On set les nouveau reperes
                self.end_wave = False
            
        # Fin de vague
        if len(self.game.sceneManager.entityManager.get_entities("ENEMY")) == 0 and self.end_wave == False:
            self.end_wave = True
            self.game.eventManager.publish("SHOW_COOLDOWN")

            
    def spawn_wave(self):
        """ Déclenche une vague en utilisant le Pooling et le DDA """
        
        # 1. Calcul du nombre d'ennemis (CPT) selon la formule du papier 
        # CPT = 20 + (30 * DPG / 100) + Spawn_Point
        cpt = 5 + (30 * self.dpg / 100) + self.spawn_point * self.wave_number
        
        # recupere une zone de spawn
        spawn_area = self.get_spawn_area()

        # 2. Spawn des unités via l'EntityManager (Pooling)
        for _ in range(int(cpt)):
            posx, posy, size = self.get_enemy_config(spawn_area)
            
            # On demande à l'EntityManager de nous donner un ennemi (neuf ou recyclé)
            type = random.randint(1, 4)
            enemy: "Enemie" = self.game.sceneManager.entityManager.spawn(Enemie, posx, posy, size=size, game=self.game, type=type)

            # 3. Ajustement de la santé selon la formule DDA [cite: 191]
            # %HM = Base_HP * Status_Point + (20% de DPG)
            base_hp = enemy.stats["hp"]
            enemy.max_hp = base_hp * self.status_point + (20 * self.dpg / 100)
            enemy.current_hp = enemy.max_hp

        # Logique de progression classique
        self.wave_number += 1
    
        self.cooldown += 2
        self.timers[self.cooldown] = 0
        self.game.eventManager.publish("NEW_WAVE")
        

    def get_enemy_config(self, spawn_area: tuple[int, int]):
        """ Calcule une position et une taille valide """
        
        posx = random.randint(spawn_area[0] - 200, spawn_area[0] + 200)
        posy = random.randint(spawn_area[1] - 200, spawn_area[1] + 200)

        radius = random.randint(15, 30)
        return posx, posy, (radius * 2, radius * 2)
    

    def reset(self):
        self.wave_difficulty = 0
        self.wave_number = 0
        self.cooldown = 5
        self.game.eventManager.publish("SHOW_COOLDOWN")
    

    def nearest_enemy(self, pos_node: tuple) -> Enemie:

        shortest_lenght = (float("inf"),None)
        enemy: Enemie
        for enemy in self.game.sceneManager.entityManager.get_entities("ENEMY"):
            lenght = pygame.Vector2((pos_node)).distance_to(enemy.pos)
            if lenght < shortest_lenght[0]:
                shortest_lenght = lenght, enemy
        return shortest_lenght[1]
    

    def handle_event(self, event) -> bool:
        # Debug des vague
        if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            print(self.game.sceneManager.entityManager.get_active_entities())


    def get_spawn_area(self) -> tuple[int, int]:
        # 1. On définit le centre (ton Kernel est généralement au milieu du monde)
        center_x = self.game.st.WORLD_WIDTH // 2
        center_y = self.game.st.WORLD_HEIGHT // 2

        # 2. On choisit un rayon aléatoire 
        # (Entre la zone de sécurité et le bord de la carte)
        min_dist = 600
        max_dist = self.game.st.WORLD_WIDTH // 2 - 200
        rayon = random.randint(min_dist, max_dist)

        # 3. On choisit un angle aléatoire entre 0 et 2π (360°)
        angle = random.uniform(0, 2 * math.pi)

        # 4. Conversion coordonnées polaires -> cartésiennes
        x = center_x + rayon * math.cos(angle)
        y = center_y + rayon * math.sin(angle)

        return int(x), int(y)
    
    
    def get_cooldown(self) -> int:
        return self.cooldown - int(self.timers[self.cooldown])


    def delay(self, time_s, dt) -> bool:
        ''' Renvoie si le temps voulu est passe '''
        if time_s in self.timers:
            self.timers[time_s] += dt
            if self.timers[time_s] >= time_s:
                self.timers[time_s] = 0
                return True
            return False
        
        else :
            self.timers[time_s] = dt
            return False