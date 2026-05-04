from random import randint
from typing import TYPE_CHECKING

import pygame

from entities.Entity import Entity
from entities.player import Player

if TYPE_CHECKING:
    from entities.bullet import Bullet
    from entities.enemy import Enemie
    from main import App


class EntityManager:
    def __init__(self, game: "App"):
        self.game = game
        self.st = self.game.st
        self.entities: list["Entity"] = []  # Notre pool global

        # Donne l'acces a l'API au entities
        Entity.get_eventBus(self.game.eventManager)
        Entity.get_spriteManager(self.game.spriteManager)

        self.game.eventManager.subscribe("NEW_GAME", self.new_game)

    def spawn(self, entity_class, x, y, uid=None, **kwargs):
        """
        Gère la récupération d'une entité inactive ou en crée une nouvelle.
        entity_class : La classe à instancier (ex: Enemy, Soldier)
        """
        # 1. Chercher si une entité de la MÊME CLASSE est disponible (inactive)
        recycled_entity: "Entity" = None
        for e in self.entities:
            if not e.active and isinstance(e, entity_class):
                recycled_entity = e
                break

        # 2. Si on en trouve une, on la réactive
        if recycled_entity:
            recycled_entity.spawn(x, y, uid=uid, **kwargs)
            # On l'attache à la caméra pour le rendu (SceneManager coordination)
            self.game.sceneManager.main_camera.add_entity(recycled_entity)
            self.game.grid.set_entity_chunk(recycled_entity)
            return recycled_entity

        # 3. Sinon, on en crée une nouvelle
        new_entity = entity_class(x, y, uid=uid, **kwargs)
        self.entities.append(new_entity)

        # On l'attache à la caméra pour le rendu (SceneManager coordination)
        self.game.sceneManager.main_camera.add_entity(new_entity)
        self.game.grid.set_entity_chunk(new_entity)

        return new_entity

    def update(self, dt):
        """Update uniquement les entités actives"""
        # Update tout le entites active
        for entity in self.entities:
            if entity.active:
                entity.update(dt)

                # Check de changement de chunk pour les entity qui n'on pas acces au Game.object
                if entity.tag == "BULLET":
                    self.check_chunk_entity(entity)

                # Apres l'update si l'entite est morte, on la retire de la camera
                if not entity.alive:
                    self.game.sceneManager.main_camera.remove_entity(entity)
                    self.game.grid.remove_entity_chunk(entity)
                    entity.active = False
                    # print(f"{entity} a ete retirer de ce chunk : {self.game.grid.get_chunk_cell(entity.pos)}")

                if entity.chunk_changed:
                    new_chunk_entity = self.game.grid.get_chunk_cell(entity.rect.center)
                    self.game.grid.move_entity_chunk(
                        entity, entity.old_chunk, new_chunk_entity
                    )
                    # print(f"| EntityManager LOG | : {entity} a bien ete retirer de son chunk chunk !")

        self.check_bullet_collisions()
        self.check_enemies_collisions(dt)

    def check_bullet_collisions(self):
        active_bullets = [b for b in self.entities if b.tag == "BULLET" and b.active]
        active_enemies = [e for e in self.entities if e.tag == "ENEMY" and e.active]

        for b in active_bullets:
            for e in active_enemies:
                if b.rect.colliderect(e.rect):
                    b: "Bullet"
                    b.on_hit(e)
                    break  # Une balle ne touche qu'un ennemi à la fois (sauf pénétration)

    def check_enemies_collisions(self, dt):
        active_enemies = [e for e in self.entities if e.tag == "ENEMY" and e.active]

        for e1 in active_enemies:
            # 1. Attaque Joueur / Kernel
            if self.game.player and e1.rect.colliderect(self.game.player.rect):
                e1.attack(dt, self.game.player)
            elif self.game.kernel and e1.rect.colliderect(self.game.kernel.rect):
                e1.attack(dt, self.game.kernel)

            # 2. Séparation entre ennemis (Rigidbody feel)
            # On utilise la grille pour ne vérifier que les ennemis proches
            nearby = self.game.grid.get_entities_around(
                pygame.Vector2(e1.rect.center), radius=1
            )
            for e2 in nearby:
                # On ne se compare pas à soi-même et on ne compare qu'aux ennemis actifs
                if e1 != e2 and e2.tag == "ENEMY" and e2.active:
                    vec = pygame.Vector2(e1.rect.center) - pygame.Vector2(
                        e2.rect.center
                    )
                    dist = vec.length()
                    # Distance minimale pour éviter l'overlap (somme des rayons avec marge)
                    min_dist = (e1.rect.width + e2.rect.width) * 0.45

                    if dist < min_dist:
                        if dist == 0:
                            # Cas rare : superposition parfaite
                            vec = pygame.Vector2(randint(-1, 1), randint(-1, 1))
                            if vec.length() == 0:
                                vec = pygame.Vector2(1, 0)
                            dist = 1

                        overlap = min_dist - dist
                        push = vec.normalize() * (overlap * 0.5)

                        # On pousse les deux entités
                        e1.pos += push
                        e2.pos -= push

                        # On synchronise leurs Rects immédiatement pour les autres collisions
                        if hasattr(e1, "sync_rect"):
                            e1.sync_rect()
                        if hasattr(e2, "sync_rect"):
                            e2.sync_rect()

    def get_entities(self, tag: str) -> list["Entity"]:
        """Retourne la liste de entites active du tag passer\n
        tag: nom en str qui reprenset le type d'enties voulu
        """
        return [
            e for e in self.entities if e.active and e.visible and e.tag == tag.upper()
        ]

    def clear_pool(self):
        """Vide la mémoire (utile lors d'un changement de niveau)"""
        for entity in self.entities:
            entity.kill()
            # On la retire de la camera
            self.game.sceneManager.main_camera.remove_entity(entity)

    def check_chunk_entity(self, entity: Entity) -> None:
        # Verifier si on a changer de chunk
        entity.new_chunk = self.game.grid.get_chunk_cell(entity.rect.center)
        if entity.new_chunk != entity.old_chunk:
            entity.chunk_changed = True
            entity.old_chunk = entity.chunk

    def new_game(self) -> None:

        self.clear_pool()

        x = randint(self.st.WORLD_WIDTH // 2 - 300, self.st.WORLD_WIDTH // 2 + 300)
        y = randint(self.st.WORLD_HEIGHT // 2 - 300, self.st.WORLD_HEIGHT // 2 + 300)

        # 1. On spawn le joueur via le système standard
        # Le spawn() renvoie l'entité créée/recyclée, on l'assigne au pointeur global !
        self.game.player = self.spawn(
            Player, x, y, uid="PLAYER_1", tag="PLAYER", game=self.game
        )

        # 2. On dit à la caméra de le suivre
        self.game.sceneManager.main_camera.follow(self.game.player)
