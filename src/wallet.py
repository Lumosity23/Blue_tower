import pygame
from settings import Settings


class Wallet:

    def __init__(self, mode: str):
        self.init_amount = Settings.MODE[mode]
        self.amount = self.init_amount
        self.creatif = False
        if not self.amount:
            self.creatif = True

    
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