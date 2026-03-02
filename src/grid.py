import pygame
import heapq
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    from entities.Entity import Entity


class Grid:
    def __init__(self, game: "App"):
        self.game = game
        self.rows = self.game.st.ROWS
        self.cols = self.game.st.COLS
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
        self.chunks = {(c, r): set() for c in range(self.cols // self.game.st.CHUNK_SIZE) for r in range(self.rows // self.game.st.CHUNK_SIZE)}
            

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
        return int(world_x // self.cell_size), int(world_y // self.cell_size)


    def get_cell_value(self, world_x, world_y):
        gx, gy = int(world_x // self.cell_size), int(world_y // self.cell_size)
        return self.grid.get((gx, gy))


    def set_cell_value(self, world_x, world_y, value):
        gx, gy = int(world_x // self.cell_size), int(world_y // self.cell_size)
        if (gx, gy) in self.grid:
            self.grid[(gx, gy)] = value


    def get_cell_isOccupied(self, world_x, world_y) -> bool:
        val = self.get_cell_value(world_x, world_y)
        return val != self.game.st.EMPTY


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
    

    def get_entities_around(self, entity_pos: pygame.Vector2 , radius: int ) -> list["Entity"]:

        cx, cy = self.get_cell_pos(entity_pos.x, entity_pos.y)
        area_cells = [(c + cx, r + cy) for c in range( 1 + ( 2 * radius )) for r in range( 1 + ( 2 * radius ))]
        
        chunks = set()
        for cells in area_cells:
            chunks.add(self.get_chunk_cell())
        
        entities_around = set()
        for chunk in chunks:
            if chunk in self.chunks:
                entities_around.update(self.chunks[chunk])
        
        return entities_around

    def move_entity_chunk(self, entity, old_chunk_coords, new_chunk_coords):
        # O(1) : On retire de l'ancien Set
        if old_chunk_coords in self.chunks:
            self.chunks[old_chunk_coords].discard(entity)

        # O(1) : On ajoute au nouveau Set
        if new_chunk_coords not in self.chunks:
            self.chunks[new_chunk_coords] = set()
        self.chunks[new_chunk_coords].add(entity)
                        

    def set_entity_chunk(self, entity: "Entity") -> None:
        ''' Ajouter une entity a un chunk ( ex : lors de son spawn )'''
        chunk = entity.pos.x // self.chunk_size, entity.pos.y // self.chunk_size

        if chunk in self.chunks:
            self.chunks[chunk].add(entity)
            entity.chunk = chunk
    

    def remove_entity_chunk(self, entity: "Entity") -> None:
        ''' Enleve une entity de son chunk ( ex : lors de sa mort ) '''
        if entity.chunk in self.chunks:
            self.chunks[entity.chunk].discard(entity)
 

    def restart(self):
        
        self.init_grid()
        self.flow_field.clear()
        self.update_flow_field(self.game.kernel.pos)