import pygame
import heapq
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    from entities.Entity import Entity


class Grid:
    def __init__(self, game: "App"):
        self.game = game
        self.rows = self.game.st.WORLD_ROWS
        self.cols = self.game.st.WORLD_COLS
        self.cell_size = self.game.st.CELL_SIZE
        self.chunk_size = self.game.st.CHUNK_SIZE
        
        # On stocke juste le TYPE de la cellule dans le dictionnaire
        # {(0,0): "EMPTY", (0,1): "WALL", ...
        self.grid = {}
        self.flow_field = {}
        self.chunks = {}

        # Init de la grille et des chunks
        self.init_grid()

        # Ecoute l'event de NEW_GAME
        self.game.eventManager.subscribe("NEW_GAME", self.restart)


    def init_grid(self) -> None:
        # Init de la grille ( CELLS )
        self.grid = {(c, r): self.game.st.EMPTY for c in range(self.cols) for r in range(self.rows)}
        # Init de la grille ( CHUNKS )
        self.chunks = {(c, r): set() for c in range(self.cols // self.game.st.CELLS_FOR_CHUNK) for r in range(self.rows // self.game.st.CELLS_FOR_CHUNK)}
        #print(len(self.chunks))


    def draw(self, surface: pygame.Surface):
        cam_offset = self.game.sceneManager.main_camera.offset
        grid_color = (40, 40, 40)

        # 1. On calcule la première et la dernière case visible à l'écran
        start_col = int(cam_offset.x // self.cell_size)
        end_col = int((cam_offset.x + surface.get_width()) // self.cell_size) + 1
        
        start_row = int(cam_offset.y // self.cell_size)
        end_row = int((cam_offset.y + surface.get_height()) // self.cell_size) + 1

        # 2. Lignes verticales (On ne boucle QUE sur ce qui est à l'écran)
        for col in range(start_col, end_col + 1):
            world_x = col * self.cell_size
            # RÈGLE 1 : World -> Screen
            screen_x = world_x - cam_offset.x 
            pygame.draw.line(surface, grid_color, (screen_x, 0), (screen_x, surface.get_height()))

        # 3. Lignes horizontales
        for row in range(start_row, end_row + 1):
            world_y = row * self.cell_size
            # RÈGLE 1 : World -> Screen
            screen_y = world_y - cam_offset.y
            pygame.draw.line(surface, grid_color, (0, screen_y), (surface.get_width(), screen_y))


    def get_cell_pos(self, world_x, world_y) -> tuple[int, int]:
        ''' Renvoie la posisiotn cell du monde '''
        return int(world_x // self.cell_size), int(world_y // self.cell_size)


    def get_pos_cell(self, cx, cy) -> tuple[int, int]:
        ''' Renvoie la posisiotn monde de la cell '''
        return int(cx * self.cell_size), int(cy * self.cell_size)
    

    def get_cell_value(self, world_x, world_y, iscellpos=False):
        if iscellpos:
            return self.grid.get((world_x, world_y))
        
        gx, gy = int(world_x // self.cell_size), int(world_y // self.cell_size)
        return self.grid.get((gx, gy))


    def set_cell_value(self, world_x, world_y, value):
        gx, gy = int(world_x // self.cell_size), int(world_y // self.cell_size)
        if (gx, gy) in self.grid:
            self.grid[(gx, gy)] = value
            return
        # print(f"pas de cell a cet endroit la : {(gx, gy)}")


    def get_cell_isOccupied(self, world_x, world_y) -> bool:
        val = self.get_cell_value(world_x, world_y)
        return val != self.game.st.EMPTY


    def get_chunk_cell(self, cell: tuple[int, int]) -> tuple[int, int]:
        cx, cy = cell
        return cx // self.game.st.CHUNK_SIZE, cy // self.game.st.CHUNK_SIZE
    

    def get_chunk(self, chunk_pos) -> set["Entity"]:
        return self.chunks[chunk_pos]
    

    def update_flow_field(self, target_world_pos):
        # Même logique qu'avant, mais plus légère sans l'objet Cell
        target_node = (int(target_world_pos[0] // self.cell_size), 
                       int(target_world_pos[1] // self.cell_size))
        
        self.flow_field = {target_node: 0}
        pq = [(0, target_node)]

        while pq:
            current_cost, current_node = heapq.heappop(pq)
            if current_cost > self.flow_field.get(current_node, float('inf')): continue

            for neighbor in self.getValidNeighbors(*current_node):
                # Récupère le coût depuis Settings via le type (String)
                cell_type = self.grid[neighbor]
                weight = self.game.st.TYPE_COST.get(cell_type, 1)
                
                # if weight == 0: continue # Infranchissable
                
                new_cost = current_cost + weight
                if new_cost < self.flow_field.get(neighbor, float('inf')):
                    self.flow_field[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor))


    def getValidNeighbors(self, gx, gy) -> list[tuple[int, int]]:
        neighbors = []
        for dx, dy in self.game.st.DIRECTIONS_ALGO:
            node = (gx + dx, gy + dy)
            if node in self.grid: 
                neighbors.append(node)
        return neighbors


    def getNeighborsAndCost(self, gx, gy) -> dict[tuple[int, int], int]:
        NeighborsAndCost = {}
        for neighbor in self.getValidNeighbors(gx, gy):
            NeighborsAndCost[neighbor] = self.flow_field[neighbor]
        return NeighborsAndCost
    

    def get_entities_around(self, entity_pos: pygame.Vector2 , radius: int ) -> set["Entity"]:

        cx, cy = self.get_cell_pos(entity_pos.x, entity_pos.y)
        area_cells = [(c + cx, r + cy) for c in range( 1 + ( 2 * radius )) for r in range( 1 + ( 2 * radius ))]

        chunks = set()
        for cell in area_cells:
            chunks.add(self.get_chunk_cell(self.get_pos_cell(*cell)))
        
        entities_around = set()
        for chunk in chunks:
            if chunk in self.chunks:
                entities_around.update(self.chunks[chunk])
        
        return entities_around


    def get_entity_at(self, wx, wy) -> "Entity":
        ''' Renvoi l'entity au corrdonne proposer, si personne renvoir None '''
        chunk_entity = self.get_chunk_cell((wx, wy))

        for entity in self.get_chunk(chunk_entity):
            if entity.rect.collidepoint(wx, wy):
                return entity
            
        return False


    def move_entity_chunk(self, entity: "Entity", old_chunk_coords, new_chunk_coords):
        # O(1) : On retire de l'ancien Set
        if old_chunk_coords in self.chunks:
            self.chunks[old_chunk_coords].discard(entity)
            entity.chunk_changed = False
        # else: print(f"l'ancien chunk de {entity} n'as pas ete trouve : {old_chunk_coords}")

        # O(1) : On ajoute au nouveau Set
        if new_chunk_coords in self.chunks:
            self.chunks[new_chunk_coords].add(entity)
            entity.chunk = new_chunk_coords
            entity.old_chunk = new_chunk_coords


    def set_entity_chunk(self, entity: "Entity") -> None:
        ''' Ajouter une entity a un chunk ( ex : lors de son spawn )'''
        chunk = entity.rect.centerx // self.chunk_size, entity.rect.centery // self.chunk_size
        # print(chunk)

        if chunk in self.chunks:
            self.chunks[chunk].add(entity)
            entity.chunk = chunk
            entity.old_chunk = chunk
            return
        
        # print(f"{entity.tag} n'as pas pu etre ajouter au chunk : {chunk}")
    

    def remove_entity_chunk(self, entity: "Entity") -> None:
        ''' Enleve une entity de son chunk ( ex : lors de sa mort ) '''
        if entity.chunk in self.chunks:
            self.chunks[entity.chunk].discard(entity)
            # print(f"{entity} a ete retire de son chunk !")
        else: print(f"l'entity : {entity} n'as pa pu etre retirer de son chunk : {entity.chunk} | son chunk actule {entity.chunk}")
 

    def show_chunk(self) -> None:
        print("_________________________________________________________________")
        for pc, chunk in self.chunks.items():
            if chunk:    
                print(f"le chunk : {pc} a comme entity ceci : {[entity.tag for entity in chunk]}")
        

    def restart(self):
        
        # self.init_grid()
        self.flow_field.clear()
        self.update_flow_field(self.game.kernel.pos)