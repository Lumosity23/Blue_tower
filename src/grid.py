import heapq
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from entities.buildings.Building import Building
    from entities.Entity import Entity
    from main import App


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

        # Debug font
        self.font = self.game.spriteManager.get_font(12)

        # Ecoute l'event de NEW_GAME
        self.game.eventManager.subscribe("NEW_GAME", self.restart)

    def init_grid(self) -> None:
        # Init de la grille ( CELLS )
        self.grid: dict[tuple[int, int], str | "Building"] = {
            (c, r): self.game.st.EMPTY
            for c in range(self.cols)
            for r in range(self.rows)
        }
        # Init de la grille ( CHUNKS )
        self.chunks = {
            (c, r): set()
            for c in range(self.cols // self.game.st.CELLS_FOR_CHUNK)
            for r in range(self.rows // self.game.st.CELLS_FOR_CHUNK)
        }
        # print(len(self.chunks))

    def draw(self, surface: pygame.Surface):
        cam_offset = self.game.sceneManager.main_camera.offset
        grid_color = (40, 40, 40)

        # 1. On calcule la première et la dernière case visible à l'écran
        start_col = max(0, int(cam_offset.x // self.cell_size))
        end_col = min(
            self.cols, int((cam_offset.x + surface.get_width()) // self.cell_size) + 1
        )

        start_row = max(0, int(cam_offset.y // self.cell_size))
        end_row = min(
            self.rows, int((cam_offset.y + surface.get_height()) // self.cell_size) + 1
        )

        # 2. Lignes verticales (On ne boucle QUE sur ce qui est à l'écran)
        for col in range(start_col, end_col + 1):
            world_x = col * self.cell_size
            # RÈGLE 1 : World -> Screen
            screen_x = world_x - cam_offset.x
            pygame.draw.line(
                surface, grid_color, (screen_x, 0), (screen_x, surface.get_height())
            )  # , width=2

        # 3. Lignes horizontales
        for row in range(start_row, end_row + 1):
            world_y = row * self.cell_size
            # RÈGLE 1 : World -> Screen
            screen_y = world_y - cam_offset.y
            pygame.draw.line(
                surface, grid_color, (0, screen_y), (surface.get_width(), screen_y)
            )  # , width=2

        # 4. Debug info (Si mode edit actif)
        if self.game.edit_mode:
            for col in range(start_col, end_col):
                for row in range(start_row, end_row):
                    if (col, row) in self.grid:
                        val = self.get_cell_value(col, row, iscellpos=True)
                        cost = self.get_cell_cost(col, row, iscellpos=True)
                        flow = self.flow_field.get((col, row), -1)

                        sx = col * self.cell_size - cam_offset.x
                        sy = row * self.cell_size - cam_offset.y

                        # Texte : Type[0]:Cout
                        debug_txt = f"{val[0]}:{cost}"
                        img = self.font.render(debug_txt, True, (255, 255, 255))
                        surface.blit(img, (sx + 5, sy + 5))

                        # Texte : Flow
                        flow_txt = f"F:{flow}"
                        img_flow = self.font.render(flow_txt, True, (150, 150, 150))
                        surface.blit(img_flow, (sx + 5, sy + 20))

    def get_cell_pos(self, world_x, world_y) -> tuple[int, int]:
        """World to grid"""
        return int(world_x // self.cell_size), int(world_y // self.cell_size)

    def get_pos_cell(self, cx, cy) -> tuple[int, int]:
        """Grid to world"""
        return int(cx * self.cell_size), int(cy * self.cell_size)

    def get_cell_value(self, world_x, world_y, iscellpos=False):
        # Recupere le batiment GRIDPOS
        if iscellpos:
            build = self.grid.get((world_x, world_y))

        # Recupere le batiment CELLPOS
        else:
            gx, gy = self.get_cell_pos(world_x, world_y)
            build = self.grid.get((gx, gy))

        if build is not None:
            if type(build) != str:
                return build.tag

            return self.game.st.EMPTY

    def get_cell_cost(self, world_x, world_y, iscellpos=False) -> int:

        value = self.get_cell_value(world_x, world_y, iscellpos=iscellpos)

        return self.game.st.TYPE_COST.get(value, 1)

    def get_build_at(self, world_x, world_y, iscellpos=False):
        # Recupere le batiment GRIDPOS
        if iscellpos:
            build = self.grid.get((world_x, world_y))

        # Recupere le batiment CELLPOS
        else:
            gx, gy = self.get_cell_pos(world_x, world_y)
            build = self.grid.get((gx, gy))

        if build is not None:
            if type(build) is not str:
                return build

            return self.game.st.EMPTY

    def remove_build_at(self, world_x, world_y, iscellpos=False) -> None:
        # Recupere le batiment GRIDPOS
        if iscellpos:
            gx, gy = world_x, world_y
            build = self.grid.get((gx, gy))

        # Recupere le batiment CELLPOS
        else:
            gx, gy = self.get_cell_pos(world_x, world_y)
            build = self.grid.get((gx, gy))

        if build != self.game.st.EMPTY and not None:
            self.grid[(gx, gy)] = self.game.st.EMPTY

    def set_cell_value(self, world_x, world_y, value):
        gx, gy = int(world_x // self.cell_size), int(world_y // self.cell_size)
        if (gx, gy) in self.grid:
            self.grid[(gx, gy)] = value
            return
        # print(f"pas de cell a cet endroit la : {(gx, gy)}")

    def add_building(
        self, world_x, world_y, building: "Building"
    ) -> tuple[int, int] | None:
        gx, gy = int(world_x // self.cell_size), int(world_y // self.cell_size)
        if (gx, gy) in self.grid:
            self.grid[(gx, gy)] = building
            return (gx, gy)

    def get_cell_isOccupied(self, world_x, world_y) -> bool:
        val = self.get_cell_value(world_x, world_y)
        return val != self.game.st.EMPTY

    def get_chunk_cell(self, cell: tuple[int, int]) -> tuple[int, int]:
        cx, cy = cell
        return cx // self.game.st.CHUNK_SIZE, cy // self.game.st.CHUNK_SIZE

    def get_chunk(self, chunk_pos) -> set["Entity"]:
        if chunk_pos in self.chunks:
            return self.chunks[chunk_pos]
        return None

    def update_flow_field(self, target_world_pos):
        # Même logique qu'avant, mais plus légère sans l'objet Cell
        target_node = self.get_cell_pos(*target_world_pos)

        self.flow_field = {target_node: 0}
        pq = [(0, target_node)]

        while pq:
            current_cost, current_node = heapq.heappop(pq)
            if current_cost > self.flow_field.get(current_node, float("inf")):
                continue

            for neighbor in self.getValidNeighbors(*current_node):
                # Récupère le coût depuis Settings via le type (String)
                weight = self.get_cell_cost(*neighbor, iscellpos=True)

                if weight <= 0:
                    continue

                new_cost = current_cost + weight
                if new_cost < self.flow_field.get(neighbor, float("inf")):
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
            if neighbor in self.flow_field:
                NeighborsAndCost[neighbor] = self.flow_field[neighbor]
        return NeighborsAndCost

    def get_entities_around(
        self, entity_pos: pygame.Vector2, radius: int
    ) -> set["Entity"]:

        cx, cy = self.get_cell_pos(entity_pos.x, entity_pos.y)

        chunks = set()
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                # Récupère le chunk pour la cellule (cx+dx, cy+dy)
                # On passe par get_pos_cell pour avoir des coord mondes car get_chunk_cell attend du monde
                world_pos = self.get_pos_cell(cx + dx, cy + dy)
                chunks.add(self.get_chunk_cell(world_pos))

        entities_around = set()
        for chunk in chunks:
            if chunk in self.chunks:
                entities_around.update(self.chunks[chunk])

        return entities_around

    def get_neighbors_buildings(
        self, build: "Building"
    ) -> dict[tuple[int, int], "Building"]:
        """Renvoie la list des building autour d'un batiment donne"""
        gx, gy = build.grid_pos

        neighbors = self.getValidNeighbors(gx, gy)
        buildNeighbors = {}

        for nx, ny in neighbors:
            building = self.get_build_at(nx, ny, iscellpos=True)
            # Direction relative du voisin par rapport à MOI
            dx = nx - gx
            dy = ny - gy
            if building != self.game.st.EMPTY:
                buildNeighbors[(dx, dy)] = building

        return buildNeighbors

    def get_entity_at(self, wx, wy) -> "Entity":
        """Renvoi l'entity au corrdonne proposer, si personne renvoie None"""
        chunk_entity = self.get_chunk_cell((wx, wy))

        chunk = self.get_chunk(chunk_entity)
        if chunk:
            for entity in chunk:
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
        """Ajouter une entity a un chunk ( ex : lors de son spawn )"""
        chunk = (
            entity.rect.centerx // self.chunk_size,
            entity.rect.centery // self.chunk_size,
        )
        # print(chunk)

        if chunk in self.chunks:
            self.chunks[chunk].add(entity)
            entity.chunk = chunk
            entity.old_chunk = chunk
            return

        # print(f"{entity.tag} n'as pas pu etre ajouter au chunk : {chunk}")

    def set_entity_at_chunk(self, entity: "Entity", w_pos: tuple[int, int]) -> None:
        """Ajouter une entity a un chunk avec une position donnee"""
        chunk = self.get_chunk_cell(w_pos)
        # print(chunk)

        if chunk in self.chunks:
            self.chunks[chunk].add(entity)
            entity.chunk = chunk
            entity.old_chunk = chunk
            return True

    def remove_entity_chunk(self, entity: "Entity") -> None:
        """Enleve une entity de son chunk ( ex : lors de sa mort )"""
        if entity.chunk in self.chunks:
            self.chunks[entity.chunk].discard(entity)
            # print(f"{entity} a ete retire de son chunk !")
        else:
            print(
                f"l'entity : {entity} n'as pa pu etre retirer de son chunk : {entity.chunk} | son chunk actule {entity.chunk}"
            )

    def show_chunk(self) -> None:
        print("_________________________________________________________________")
        for pc, chunk in self.chunks.items():
            if chunk:
                print(
                    f"le chunk : {pc} a comme entity ceci : {[entity.tag for entity in chunk]}"
                )

    def restart(self):

        # self.init_grid()
        self.flow_field.clear()
        self.update_flow_field(self.game.kernel.pos)
