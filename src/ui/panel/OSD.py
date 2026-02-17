from ui.UIElement import UIElement
from ui.UIText import UIText
from settings import Settings
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


# Cette classe n'est la que pour afficher des chose factuel c'est l'OSD pas de choses interactive
class OSD(UIElement):

    def __init__(self, game: "App", uid: str=None):
        super().__init__(0, 0, 0, 0, uid=uid)
        '''
            Permet d'afficher du text sur l'ecran
        '''
        # Transparent car beosin que d'afficher du text
        self.uid = 'OSD'
        self.game = game
        self.image.set_alpha(0)
        self.st = Settings()

        if self.uid:
            self.child_uid = f"{self.uid}_"
        else:
            self.child_uid = ""
    

    def post_init(self) -> None:
        # Nombre de vague
        self.wave_text = UIText(self.st.SCREEN_WIDTH / 2, 50, "Wave", 50, uid=f"{self.child_uid}wave_text")
        self.number_wave = UIText(self.st.SCREEN_WIDTH / 2, 50, self.get_wave_number, text_update=True, uid=f"{self.child_uid}wave_number")

        # Nombre d'ennemis qui restent
        self.nmb = UIText(self.st.SCREEN_WIDTH - 50, 60, self.get_len_enemies, text_update=True,  uid=f"{self.child_uid}enemis_restant")

        # Nombre de FPS
        self.fps = UIText(10, 0, self.get_fps, 50, text_update=True)

        # Wallet
        if self.game.walletManager.creatif:
            self.wallet = UIText(self.st.SCREEN_WIDTH - 50, 20, "CREATIF", uid=f"{self.child_uid}creatif_text")
        else: self.wallet = UIText(self.st.SCREEN_WIDTH - 50, 20, self.get_amount_wallet, text_update=True, uid=f"{self.child_uid}creatif_text")

        # Liste des text enfants
        self.text = [self.wave_text, self.number_wave, self.nmb, self.fps, self.wallet]

        # ajout des text aux enfants
        for child in self.text:
            self.add_child(child)
        
    
    def get_wave_number(self) -> str:
        return str(self.game.wave_manager.wave_number)
    
    def get_len_enemies(self) -> str:
        return str(len(self.game.enemies))

    def get_fps(self) -> str:
        return str(int(self.game.clock.get_fps()))
    
    def get_amount_wallet(self) -> str:
        return str(self.game.walletManager.get_wallet_val())