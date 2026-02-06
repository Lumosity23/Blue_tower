import pygame
from settings import Settings
from sprite_custom import get_custom_sprite
from grid import Grid


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.st = Settings()
        self.size = (self.st.PLAYER_WIDTH, self.st.PLAYER_HEIGHT)
        self.image = get_custom_sprite(self.st.PLAYER_SPRITE, self.size)
        self.rect = self.image.get_rect(center=(self.st.SCREEN_WIDTH / 2, self.st.SCREEN_HEIGHT / 2))
        self.velocity = 500
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        self.max_hp = Settings.PLAYER_HEALTH
        self.current_hp = self.max_hp
        self.damage = self.current_hp
        self.alive = True
        
    def update(self, dt, walls: list[object], grid: Grid, player, enemis, all_sprite):
        keys = pygame.key.get_pressed()

        # ---------------------------------------------------------
        # PARTIE 1 : MOUVEMENT HORIZONTAL (X)
        # ---------------------------------------------------------
        # Vers la gauche
        if keys[pygame.K_LEFT] | keys[pygame.K_a]:
            self.pos.x -= self.velocity * dt
        # Vers la droite
        if keys[pygame.K_RIGHT] | keys[pygame.K_d]:
            self.pos.x += self.velocity * dt
        # mise a jour de la position de notre hitbox
        self.rect.x = self.pos.x

        # check de collisions
        hits = pygame.sprite.spritecollide(self, walls, False)
        if hits: # si collision
            hit: object = hits[0]
            # collision a gauche
            if keys[pygame.K_LEFT] | keys[pygame.K_a]:
                 self.rect.left = hit.rect.right
                 self.pos.x = self.rect.x
            # collision a droite
            elif keys[pygame.K_RIGHT] | keys[pygame.K_d]:
                 self.rect.right = hit.rect.left
                 self.pos.x = self.rect.x

        # ---------------------------------------------------------
        # PARTIE 2 : MOUVEMENT VERTICAL (Y)
        # ---------------------------------------------------------
        # Vers le haut
        if keys[pygame.K_UP] | keys[pygame.K_w]:
            self.pos.y -= self.velocity * dt # ATTENTION l'axe de y est a l'envers
        # Vers le bas
        if keys[pygame.K_DOWN] | keys[pygame.K_s]:
            self.pos.y += self.velocity * dt
        self.rect.y = self.pos.y

        # check de collisions
        hits = pygame.sprite.spritecollide(self, walls, False)
        if hits: # si collision
             hit = hits[0]
             if keys[pygame.K_UP] | keys[pygame.K_w]:
                self.rect.top = hit.rect.bottom
                self.pos.y = self.rect.y
             elif keys[pygame.K_DOWN] | keys[pygame.K_s]:
                self.rect.bottom = hit.rect.top
                self.pos.y = self.rect.y       
        # check collision avec la fenetre et les murs
        self.constraints_screen()
    

    def constraints_screen(self):
        # Gauche
        if self.pos.x <= 0:
                self.pos.x = 0
                self.rect.x = self.pos.x
        # Droite
        if self.pos.x >= self.st.SCREEN_WIDTH - self.rect.width:
                self.pos.x = self.st.SCREEN_WIDTH - self.rect.width
                self.rect.x = self.pos.x
        # Haut
        if self.pos.y <= 0:
                self.pos.y = 0
                self.rect.y = self.pos.y
        # Bas
        if self.pos.y >= self.st.SCREEN_HEIGHT - self.rect.height:
                self.pos.y = self.st.SCREEN_HEIGHT - self.rect.height
                self.rect.y = self.pos.y

    def take_damage(self, amount):
        self.current_hp -= amount
        self.damage = self.current_hp
        # si 0 HP alors -> mort
        if self.current_hp <= 0:
            self.alive = False
    

    def reset(self):
        # Remis au centre de l'ecran
        self.pos.xy = self.st.SCREEN_WIDTH / 2, self.st.SCREEN_HEIGHT / 2
        self.current_hp = self.max_hp
        self.damage = self.current_hp
        self.alive = True