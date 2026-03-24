import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class TileMap:

    def __init__(self, game: "App"):
        
        self.game = game
        self.st = self.game.st
        self.chunk_size = self.st.CELLS_FOR_CHUNK
        self.cell_size = self.st.CELL_SIZE
        self.chunk_pixel_size = self.cell_size * self.chunk_size

        # self.tiles = self.game.spriteManager.slice_sprite( self.st.ASSET_PATHS["chunk"], (self.chunk_size * self.cell_size, self.chunk_size * self.cell_size) )
        
        # Pour les test
        self.tile = self.game.spriteManager.get_base_image("chunk")

        self.baked_chunks: dict[tuple[int, int], pygame.Surface] = {}

        self.init_chunk()

    def init_chunk(self) -> None:

        for col in range( self.st.WORLD_COLS // self.chunk_size ):
            for row in range( self.st.WORLD_ROWS // self.chunk_size ):
                self.baked_chunks[ col, row ] = self.tile.copy()


    def bake_chunk( self, chunk_x: int, chunk_y: int, chunk_size: tuple[int, int] ) -> None:

        chunk_surface = pygame.Surface( chunk_size )

        for local_col in range( self.chunk_size ):
            for local_row in range( self.chunk_size ):
                
                # Coordonnées absolues dans le monde (pour le Perlin Noise plus tard)
                # world_col = (chunk_x * self.chunk_size) + local_col
                # world_row = (chunk_y * self.chunk_size) + local_row
                
                # --- PLUS TARD : Utiliser le Perlin Noise ici pour choisir la tuile ---
                tile_image = self.tiles[ local_col, local_row ] 
                
                # 3. On blit la petite tuile SUR la grosse surface du chunk
                pixel_x = local_col * self.cell_size
                pixel_y = local_row * self.cell_size
                chunk_surface.blit( tile_image, ( pixel_x, pixel_y ) )
                
        # 4. On sauvegarde le chunk terminé !
        self.baked_chunks[( chunk_x, chunk_y )] = chunk_surface


    def get_visible_chunks( self, cam_offset: pygame.math.Vector2, width, height ) -> dict[tuple[int, int], pygame.Surface]:
        ''' Renvoie les chunk visible pas la camera via une liste de Surface '''

        visible_chunks = {}

        start_col = int( cam_offset.x // self.chunk_pixel_size )
        start_row = int( cam_offset.y // self.chunk_pixel_size )
        end_col   = int( (cam_offset.x + width) // self.chunk_pixel_size )
        end_row   = int( (cam_offset.y + height) // self.chunk_pixel_size )

        cols = (end_col - start_col) + 1
        rows = (end_row - start_row) + 1

        for col in range(cols):
            for row in range(rows):
                # Calcule des chunks conserner
                x = start_col + col
                y = start_row + row

                # Recupere la surface du chunk via ses coordonnees (de chunk)
                if (x, y) in self.baked_chunks:
                    visible_chunks[x, y] = self.baked_chunks[ x, y ]

        return visible_chunks
    

    def draw(self, screen: pygame.Surface) -> None:
        
        # Dessiner le background ( Les chunks )
        cam_offset = self.game.sceneManager.main_camera.offset
        visible_chunks = self.get_visible_chunks(cam_offset, *screen.get_size())
        
        for pos, chunk_image in visible_chunks.items():
            # A. Position absolue MONDE
            world_x = pos[0] * self.chunk_pixel_size
            world_y = pos[1] * self.chunk_pixel_size

            # B. RÈGLE D'AFFICHAGE : Position ECRAN = Monde - Offset
            screen_x = world_x - cam_offset.x
            screen_y = world_y - cam_offset.y

            # Blit du chunk directement
            screen.blit(chunk_image, (screen_x, screen_y))