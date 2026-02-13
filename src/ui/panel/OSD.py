from ui.UIElement import UIElement
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


# Cette classe n'est la que pour afficher des chose factuel c'est l'OSD pas de choses interactive
class OSD(UIElement):

    def __init__(self, x, y, w, h, game, color=...):
        super().__init__(x, y, w, h, game, color)
        '''
            Permet d'afficher du text sur l'ecran
        '''
        # Transparent car beosin que d'afficher du text
        self.image.set_alpha(0)
        self.UI = self.game.spriteManager
        self.st = self.game.st

    
    def draw(self, surface):
        
        # ICI on va retrouver tout le donner et valuer interessante, stats, portefeuille et autres

        # Nombre de vague
        self.UI.draw_text(surface, "Wave", self.st.SCREEN_WIDTH / 2, 50, (255,255,255), 'center')
        self.UI.draw_text(surface, f"       {self.game.wave_manager.wave_number}", self.st.SCREEN_WIDTH / 2, 50, (255,255,255), 'center')

        # Nombre d'ennemis qui restent
        self.UI.draw_text(surface, str(len(self.game.enemies)), self.st.SCREEN_WIDTH - 50, 60, (255,255,255), 'topright')

        # Nombre de FPS
        self.UI.draw_text(surface, str(int(self.game.clock.get_fps())), 10, 0, (255,255,255))

        # Wallet
        money = str(self.game.walletManager.get_wallet_val())
        if self.game.walletManager.creatif:
            money = "CREATIF"
        self.UI.draw_text(surface, money, self.st.SCREEN_WIDTH - 50, 20, (255,255,255), 'topright')