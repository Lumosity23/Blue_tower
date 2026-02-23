from ui.UIElement import UIElement
from ui.UIText import UIText
from ui.UIProgressBar import UIProgressBar
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
        self.st = Settings()

        if self.uid:
            self.child_uid = f"{self.uid}_"
        else:
            self.child_uid = ""

        self.game.eventManager.subscribe("UPDATE_KERNEL_HP", self.update_hud_hp)


    def post_init(self) -> None:
        # Nombre de vague
        self.wave_text = UIText(self.st.SCREEN_WIDTH // 2, 50, "Wave", 50, uid=f"{self.child_uid}wave_text")
        self.number_wave = UIText(self.st.SCREEN_WIDTH // 2, 50, self.get_wave_number, text_update=True, uid=f"{self.child_uid}wave_number")

        # Nombre d'ennemis qui restent
        self.nmb = UIText(self.st.SCREEN_WIDTH - 50, 60, self.get_len_enemies, text_update=True,  uid=f"{self.child_uid}enemis_restant")

        # Nombre de FPS
        self.FPS = UIText(10, 0, self.get_fps, 50, text_update=True, uid=f"{self.child_uid}FPS")

        # Wallet
        if not self.game.walletManager.creatif:
            self.wallet = UIText(self.st.SCREEN_WIDTH - 50, 20, self.get_amount_wallet, text_update=True, uid=f"{self.child_uid}creatif_text")
        else: self.wallet = None

        self.gameMode = UIText(self.st.SCREEN_WIDTH - 50, 20, self.game.mode, uid=f"{self.child_uid}gameMode_text")
        
        self.kernel_hp_bar = UIProgressBar(
            x=self.game.st.SCREEN_WIDTH // 2 - 100, # Centré en haut
            y=20, 
            w=400, h=40,
            uid="HUD_KERNEL_HP"
        )
        self.kernel_hp_bar.dynamic_color = True

        # Liste des text enfants
        if not self.wallet:
            self.text = [self.wave_text, self.number_wave, self.nmb, self.FPS, self.gameMode, self.kernel_hp_bar]
        else:
            self.text = [self.wave_text, self.number_wave, self.nmb, self.FPS, self.gameMode, self.wallet, self.kernel_hp_bar]

        # ajout des text aux enfants
        for child in self.text:
            self.add_child(child)
    

    def update_hud_hp(self, current_hp):
        # On met à jour la barre qui est dans le HUD
        self.kernel_hp_bar.update_values(current_hp, self.game.kernel.current_hp)

    
    def get_wave_number(self) -> str:
        return str(self.game.sceneManager.entityManager.waveManager.wave_number)
    
    def get_len_enemies(self) -> str:
        return str(len(self.game.sceneManager.entityManager.get_entities("ENEMY")))

    def get_fps(self) -> str:
        return str(int(self.game.clock.get_fps()))
    
    def get_amount_wallet(self) -> str:
        return str(self.game.walletManager.get_wallet_val())