from entities.Entity import Entity
from manager.WaveManager import WaveManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    from entities.bullet import Bullet


class EntityManager:
    def __init__(self, game: "App"):
        self.game = game
        self.entities: list["Entity"] = []  # Notre pool global
        self.root = Entity(0, 0, 0, 0, "ROOT", "Entity_manager_ROOT")

        self.waveManager = WaveManager(game)
        self.root.add_child(self.waveManager)
        

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
            recycled_entity.spawn(x, y, uid)
            # On peut passer des arguments supplémentaires si besoin
            if hasattr(recycled_entity, 'reset'):
                recycled_entity.reset(**kwargs)
            return recycled_entity

        # 3. Sinon, on en crée une nouvelle
        new_entity = entity_class(x, y, uid=uid, **kwargs)
        self.entities.append(new_entity)
        
        # On l'attache à la caméra pour le rendu (SceneManager coordination)
        if hasattr(self.game.sceneManager, "main_camera"):
            self.game.sceneManager.camera.add_child(new_entity)
            
        return new_entity

    def update(self, dt):
        """ Update uniquement les entités actives """
        e: "Entity"
        for e in self.entities:
            if e.active:
                e.update(dt)


    def check_bullet_collisions(self):
        active_bullets = [b for b in self.entities if b.tag == "BULLET" and b.active]
        active_enemies = [e for e in self.entities if e.tag == "ENEMY" and e.active]

        for b in active_bullets:
            for e in active_enemies:
                if b.rect.colliderect(e.rect):
                    b: "Bullet"
                    b.on_hit(e)
                    break # Une balle ne touche qu'un ennemi à la fois (sauf pénétration)


    def get_active_entities(self):
        """ Retourne la liste triée pour le rendu (Z-Sorting) """
        active_list = [e for e in self.entities if e.active and e.visible]
        # Tri par le bas du rect (pour la perspective 2D)
        return sorted(active_list, key=lambda e: e.rect.bottom)
    

    def get_entities(self, tag: str) -> list["Entity"]:
        ''' Retourne la liste de entites active du tag passer
            tag: nom en str qui reprenset le type d'enties voulu
        '''
        return [e for e in self.entities if e.active and e.visible and e.tag == tag]
        

    def clear_pool(self):
        """ Vide la mémoire (utile lors d'un changement de niveau) """
        self.entities.clear()