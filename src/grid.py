import pygame
import heapq
from entities.cell import Cell

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class Grid():

    def __init__(self, game: "App"):
        self.game = game
        self.rows = self.game.st.ROWS
        self.cols = self.game.st.COLS
        self.cell_size = self.game.st.CELL_SIZE
        self.grid = self.init_grid()
        self.flow_field = {}
        self.update_flow_field(game.kernel.pos)

        # Declaration des subscribe
        self.game.eventManager.subscribe("RESTART_GAME", self.restart)


    def init_grid(self):
        # Initialisation de la grid
        cells = {}
        for cols in range(self.cols):
            for rows in range(self.rows):
                cells[(cols,rows)] = Cell(cols, rows, self.game.st.EMPTY) # 0 car on a simplement init la grille
        return cells
    

    def restart(self) -> None:
        '''
            Reinitialise la grid pour une nouvelle partie
        '''
        self.grid.clear()
        self.grid = self.init_grid()


    def draw(self, surface) -> None:

        grid_color = (50, 50, 50)

        # le grillage en x
        for col in range(self.cols + 1):
            x = col * self.cell_size
            pygame.draw.line(surface, grid_color, (x, 0), (x, self.game.st.SCREEN_HEIGHT))

        # le grillage en y
        for row in range(self.rows + 1):
            y = row * self.cell_size
            pygame.draw.line(surface, grid_color, (0, y), (self.game.st.SCREEN_WIDTH, y))



    def get_cell_value(self, posx, posy) -> int | None:
        
        gx = posx // self.cell_size
        gy = posy // self.cell_size
        
        if (gx, gy) in self.grid:
            return self.grid[gx, gy].type
        # si hors champ
        return None
    

    def set_cell_value(self, posx, posy, value, already_cell_pos: bool=False) -> None:
        
        if not already_cell_pos:
            gx = posx // self.cell_size
            gy = posy // self.cell_size

            if (gx, gy) in self.grid:
                self.grid[gx, gy].type = value
        
        else: 
            if (posx, posy) in self.grid:
                self.grid[posx, posy].type = value


    def get_cell_pos(self, posx: float, posy: float) -> tuple:
        
        gx = posx // self.cell_size
        gy = posy // self.cell_size
        
        cell_pos = (gx, gy)

        if cell_pos in self.grid:
            return cell_pos
        else: 
            # print(f"{cell_pos} -> {posx, posy} -> possition invalide.....")
            return cell_pos
        
    
    def get_cell_isOccupied(self, posx, posy) -> bool:

        gx = posx // self.cell_size
        gy = posy // self.cell_size

        if (gx, gy) in self.grid:
            return self.grid[gx, gy].isOccupied
        
    
    def get_cells_in_rect(self, rect: pygame.Rect) -> list:
        """
        Renvoie la liste des coordonnées (gx, gy) de la grille touchées par ce Rect.
        """
        cells = []
        
        # 1. Convertir les bords du Rect en index de Grille
        # On utilise min/max pour rester dans les limites de la grille
        start_col = max(0, rect.left // self.cell_size)
        end_col = min(self.cols, (rect.right - 1) // self.cell_size) # -1 car rect.right est exclusif
        
        start_row = max(0, rect.top // self.cell_size)
        end_row = min(self.rows, (rect.bottom - 1) // self.cell_size)

        # 2. Double boucle simple
        # range(start, end + 1) pour inclure la dernière colonne/ligne
        for x in range(start_col, end_col + 1):
            for y in range(start_row, end_row + 1):
                cells.append((x, y))
                
        return cells


    def change_cells_state(self, last_cell: list, current_cell: list) -> None:

       if not last_cell:
           for cell in current_cell:
               if cell in self.grid:
                   self.grid[cell].isOccupied = not self.grid[cell].isOccupied

       # Cell qu'on dois changer pour l'affichage ( la diff entre les ancienne et le nouvelles)
       cell_to_change = [cell for cell in last_cell if cell not in set(current_cell)] + [cell for cell in current_cell if cell not in set(last_cell)]

       for cell in last_cell:
           if cell in self.grid:
               # Inversion de son etat pour l'affichage
               self.grid[cell].isOccupied = not self.grid[cell].isOccupied


    def get_cost(self, posx, posy, alredy_cell: bool=False):

        if alredy_cell:
            return self.game.st.cell_cost[self.grid[posx, posy].type]
        
        gx = posx // self.cell_size
        gy = posy // self.cell_size

        cell_pos = gx, gy
        if cell_pos in self.grid:
            cell_type = self.grid[cell_pos].type
            if cell_type in self.game.st.cell_cost:
                return self.game.st.cell_cost[cell_type]


    def getValidNeighbors(self, posX, posY) -> list[tuple[int, int]]:
        validNeighbors = []
        for dx, dy in self.game.st.DIRECTIONS_ALGO:
            newX = posX + dx
            newY = posY + dy

            # 1. Check Limites
            if (newX, newY) in self.grid:    
                validNeighbors.append((newX, newY))
        return validNeighbors


    def update_flow_field(self, target_pos: tuple) -> None:

        # Recuper la cell sur la quelle se trouve le target
        target_node = self.get_cell_pos(target_pos[0], target_pos[1])

        # On vide notre heatmap
        
        self.flow_field.clear()

        # 1. Utilisation de DEQUE pour la performance
        pq = []
        heapq.heappush(pq, (0, target_node))

        self.flow_field[target_node] = 0 # Distance 0

        while pq:
            current_cost, current_node = heapq.heappop(pq)
            
            if current_cost > self.flow_field.get(current_node, float('inf')):
                continue

            cx, cy = current_node

            for neighbor in self.getValidNeighbors(cx, cy):
                
                cell_cost = self.get_cost(neighbor[0], neighbor[1])

                if neighbor in self.flow_field:
                    continue
                
                # Nouveau cout (node actuel + cout du voisin)
                new_cost = current_cost + cell_cost

                if new_cost < self.flow_field.get(neighbor, float('inf')):
                    self.flow_field[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor))

    
    def get_neighbors(self, x, y) -> dict[tuple:int]:
        '''
            revoie un dict de coordonner (tuple) de cell avec leur valeur (int)
        '''
        Neighbors = {}
        for dx, dy in self.game.st.DIRECTIONS_ENEMIS:
            newX = int(x + dx)
            newY = int(y + dy)

            if (newX,newY) in self.flow_field:    
                Neighbors[newX, newY] = self.flow_field[newX, newY]

        return Neighbors
