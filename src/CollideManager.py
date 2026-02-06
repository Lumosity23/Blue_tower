import pygame
from settings import Settings


class CollideManager():
    
    def __init__(self):
        pass


    def check_collisions(self, attaker, defendres, dokill1: bool, dokill2: bool):
        '''
            attaker : Peut être un GROUPE (ex: balles) OU un SPRITE SEUL (ex: joueur)\n
            defenders : Doit être un GROUPE (ex: ennemis)\n
            dokill1, dokill2 permet de dire si lors de la collision 'objet.kill()'
        '''
        # Colission avec Groupe 1 >< Group 2
        if isinstance(attaker, pygame.sprite.Group):

            hits = pygame.sprite.groupcollide(attaker, defendres, dokill1, dokill2)
            if hits:
                for att, defs in hits.items():
                    for d in defs:
                        if att.current_hp <= 0:
                            break
                        d_hp = d.current_hp
                        # On vérifie que les objets ont bien les attributs damage/take_damage
                        if hasattr(d, 'take_damage') and hasattr(att, 'damage'):
                            d.take_damage(att.damage)
                    
                        if hasattr(att, 'take_damage') and hasattr(d, 'current_hp'):
                            att.take_damage(d_hp)  
        else:    
            # faire un collision avec un sprite >< Groupe
            hits = pygame.sprite.spritecollide(attaker, defendres, dokill2)
            if hits:
                for enemy in hits:
                    # Valeur par défaut ou enemy.damage
                    damage_to_take = 10 
                    if hasattr(enemy, 'damage'):
                        damage_to_take = enemy.damage

                    attaker.take_damage(damage_to_take)
                    if hasattr(attaker, 'damage'):
                        enemy.take_damage(attaker.damage)
                    else:
                        enemy.take_damage(attaker.current_hp)
        