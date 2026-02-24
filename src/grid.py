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
        self.update_flow_field(self.game.kernel.pos)
        self.game.eventManager.subscribe("NEW_GAME", self.restart)


    def init_grid(self) -> dict:
        print(f"Grid init avec une taille de {self.cols}x{self.rows} cells")
        return {(c, r): self.game.st.EMPTY for c in range(self.cols) for r in range(self.rows)}


    def draw(self, surface: pygame.Surface):
        # IMPORTANT : On dessine la grille avec le décalage de la caméra
        cam_x = self.game.sceneManager.camera.pos.x
        cam_y = self.game.sceneManager.camera.pos.y
        grid_color = (40, 40, 40)

        # Lignes verticales
        for col in range(self.cols + 1):
            x = col * self.cell_size + cam_x
            pygame.draw.line(surface, grid_color, (x, cam_y), (x, self.rows * self.cell_size + cam_y))

        # Lignes horizontales
        for row in range(self.rows + 1):
            y = row * self.cell_size + cam_y
            pygame.draw.line(surface, grid_color, (cam_x, y), (self.cols * self.cell_size + cam_x, y))


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