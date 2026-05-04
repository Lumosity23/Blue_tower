from random import randint
from typing import TYPE_CHECKING

import pygame

from entities.bullet import Bullet
from entities.Entity import Entity
from ui.element.UIProgressBar import UIProgressBar

if TYPE_CHECKING:
    from main import App


class Player(Entity):
    def __init__(self, spawn_x, spawn_y, uid, tag, game: "App"):
        self.game = game
        self.stats = self.game.st.ENTITIES_DATA["PLAYER"]
        w, h = self.stats["size"]

        super().__init__(spawn_x, spawn_y, w, h, tag=tag, uid=uid)

        # Stats vitales
        self.max_hp = self.stats["hp"]
        self.current_hp = self.max_hp
        self.kills = 0
        self.alive = True
        self.is_moving = False

        # ----------------------------------------------------------------
        # Stats upgradables — uniquement la VALEUR COURANTE sur l'entité.
        # max / price / rate vivent dans le JSON d'upgrade, pas ici.
        # ----------------------------------------------------------------
        self.damage = 10
        self.velocity = 500

        # Barre de vie
        self.hp_bar = UIProgressBar(x=0, y=-15, uid="PLAYER_HP")
        self.hp_bar.setup(w=self.rect.w, h=8, show_text=False)
        self.hp_bar.dynamic_color = True
        self.add_child(self.hp_bar)

        # Animations
        self.set_anim("IDLE", (w, h), 1.5, 2)
        self.set_anim("MOVE", (w, h), 1, 2)

        # Events
        self.game.eventManager.subscribe("NEW_GAME", self.reset)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, dt):
        if not self.active:
            return

        im = self.game.input_manager

        # --- Axe X ---
        move_x = 0
        if im.is_pressed("left"):
            move_x -= 1
        if im.is_pressed("right"):
            move_x += 1

        if move_x != 0:
            self.pos.x += move_x * self.velocity * dt
        self.rect.x = self.pos.x

        hits = [
            b
            for b in self.game.sceneManager.buildManager.entities
            if b.active and self.rect.colliderect(b.rect)
        ]
        if hits:
            hit = hits[0]
            if move_x < 0:
                self.rect.left = hit.rect.right
            else:
                self.rect.right = hit.rect.left
            self.pos.x = self.rect.x

        # --- Axe Y ---
        move_y = 0
        if im.is_pressed("up"):
            move_y -= 1
        if im.is_pressed("down"):
            move_y += 1

        if move_y != 0:
            self.pos.y += move_y * self.velocity * dt
        self.rect.y = self.pos.y

        hits = [
            b
            for b in self.game.sceneManager.buildManager.entities
            if b.active and self.rect.colliderect(b.rect)
        ]
        if hits:
            hit = hits[0]
            if move_y < 0:
                self.rect.top = hit.rect.bottom
            else:
                self.rect.bottom = hit.rect.top
            self.pos.y = self.rect.y

        # --- Finalisation ---
        self.constraints_world()
        self.check_chunk()

        if move_x != 0 or move_y != 0:
            self.is_moving = True
            self.state = "MOVE"
        else:
            self.is_moving = False
            self.state = "IDLE"

        if self.is_moving and self.delay(0.40, dt):
            self.game.eventManager.publish("PLAY_SFX", "WALK")

        self.update_animation(dt, self.state)
        super().update(dt)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def constraints_world(self):
        self.pos.x = max(0, min(self.pos.x, self.game.st.WORLD_WIDTH - self.rect.w))
        self.pos.y = max(0, min(self.pos.y, self.game.st.WORLD_HEIGHT - self.rect.h))
        self.rect.topleft = self.pos

    def check_chunk(self) -> None:
        self.new_chunk = self.game.grid.get_chunk_cell(self.rect.center)
        if self.new_chunk != self.old_chunk:
            self.chunk_changed = True
            self.old_chunk = self.chunk

    def take_damage(self, amount):
        super().take_damage(amount)
        self.hp_bar.update_values(self.current_hp, self.max_hp)

    def reset(self):
        spawn_x = randint(
            self.game.st.WORLD_WIDTH // 2 - 300,
            self.game.st.WORLD_WIDTH // 2 + 300,
        )
        spawn_y = randint(
            self.game.st.WORLD_HEIGHT // 2 - 300,
            self.game.st.WORLD_HEIGHT // 2 + 300,
        )
        self.spawn(spawn_x, spawn_y, "PLAYER")
        self.current_hp = self.max_hp
        self.hp_bar.update_values(self.current_hp, self.max_hp)
        self.kills = 0
        self.alive = True

    def shoot(self) -> None:
        mx, my = pygame.mouse.get_pos()
        cam_offset = self.game.sceneManager.main_camera.offset
        world_x = mx + cam_offset.x
        world_y = my + cam_offset.y

        self.game.sceneManager.entityManager.spawn(
            Bullet,
            self.rect.centerx,
            self.rect.centery,
            uid="Player_Bullet",
            target_pos=(world_x, world_y),
            owner=self,
            bullet_damage=self.damage,
        )

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        cam_offset = self.game.sceneManager.main_camera.offset
        world_mouse_pos = (
            mouse_pos[0] + cam_offset.x,
            mouse_pos[1] + cam_offset.y,
        )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_screen_rect().collidepoint(world_mouse_pos):
                self.game.eventManager.publish("ELEMENT_SELECTED", self)
                self.selected = True
                return True

            if self.selected:
                self.game.eventManager.publish("ELEMENT_UNSELECTED")

            if not self.game.edit_mode:
                self.shoot()
                self.game.eventManager.publish("PLAY_SFX", "SHOOT")
                return True

        super().handle_event(event)


# ----------------------------------------------------------------------
# Déclaration de l'UI info (inchangée)
# ----------------------------------------------------------------------
Player.ui_config(
    ("ICON", "you", "image"),
    ("BAR", "Vie", "current_hp", "max_hp"),
    ("STAT", "kills", "kills"),
    ("STAT", "STATE", "state"),
)

# ----------------------------------------------------------------------
# Déclaration des upgrades — format propre :
#   ("Label affiché", "attribut_entité", valeur_max, prix, taux_%")
# Le JSON est généré automatiquement au lancement, rien d'autre à faire.
# ----------------------------------------------------------------------
Player.upgrade_config(
    ("Damage", "damage", 100, 200, 10),
    ("Velocity", "velocity", 1000, 300, 5),
    ("Vie", "current_hp", 1000, 500, 5),
)
