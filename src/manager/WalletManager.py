import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class WalletManager:

    def __init__(self, game: "App"):
        self.game = game
        self.init_amount = self.game.st.MODE[self.game.mode]
        self.amount = self.init_amount
        self.creatif = False
        if not self.amount:
            self.creatif = True
            print("mode creatif activer")

        # Declaration des subscribe
        self.game.eventManager.subscribe("ERROR_PAYMENT", self.error)
        self.game.eventManager.subscribe("NEW_GAME", self.reset)

    
    def buy(self, amount: int) -> bool:
        '''
            Acheter qqch -> confimer par un bool
        '''
        # Creatif mode
        if self.creatif:
            return True

        if self.amount - amount >= 0 and not self.creatif:
            self.amount -= amount
            return True
        
        else:
            return False

    def earn_money(self, amount: int) -> None:
        '''
            Gagner de l'argent (ajout au portefeuille)
        '''
        self.amount += amount

    
    def get_wallet_val(self) -> int:
        '''
            Savoir combien il rest dans le portefeuille
        '''
        return int(self.amount)
    

    def reset(self):
        self.amount = self.init_amount
    

    def error(self):
        print("erreur de payement -> manque de cash !")