import pygame
import heapq
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class Grid:
    def __init__(self, game: "App"):
        self.game = game
        self.rows = self.game.st.ROWS
        self.cols = self.game.st.COLS
        self.cell_size = self.game.st.CELL_SIZE
        
        # On stocke juste le TYPE de la cellule dans le dictionnaire
        # {(0,0): "EMPTY", (0,1): "WALL", ...}
        self.grid = self.init_grid()
        self.flow_field = {}
        
        # Ecoute l'event de NEW_GAME
        self.game.eventManager.subscribe("NEW_GAME", self.restart)


    def init_grid(self) -> dict:
        # print(f"Grid init avec une taille de {self.cols}x{self.rows} cells")
        return {(c, r): self.game.st.EMPTY for c in range(self.cols) for r in range(self.rows)}


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
                
                if weight == 0: continue # Infranchissable
                
                new_cost = current_cost + weight
                if new_cost < self.flow_field.get(neighbor, float('inf')):
                    self.flow_field[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor))


    def getValidNeighbors(self, gx, gy) -> list[tuple[int, int]]:
        neighbors = []
        for dx, dy in self.game.st.DIRECTIONS_ALGO:
            node = (gx + dx, gy + dy)
            if node in self.grid: neighbors.append(node)
        return neighbors


    def getNeighborsAndCost(self, gx, gy) -> dict[tuple[int, int], int]:
        NeighborsAndCost = {}
        for neighbor in self.getValidNeighbors(gx, gy):
            NeighborsAndCost[neighbor] = self.flow_field[neighbor]
        return NeighborsAndCost


    def restart(self):
        
        self.grid = self.init_grid()
        self.flow_field.clear()
        self.update_flow_field(self.game.kernel.pos)