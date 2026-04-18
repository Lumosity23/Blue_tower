from .Building import Building


class Bank(Building):

    def __init__(self, x, y, data, game, uid):
        super().__init__(x, y, data, game, tag="BANK", uid=uid)

        # Gain section
        self.gain = 100
        self.max_gn = 1000
        self.price_gn = 400
        self.rate_gn = 5

        self.mapping = {
            "xy" : self.rect.center,
            "text" : self.gain
        }
    

    def update(self, dt):
        
        if self.delay(3, dt):
            self._EVENTBUS.publish("EARN_MONEY", self.gain)
            self._EVENTBUS.publish("SHOW_FT", self.mapping)
        
        super().update(dt)


Bank.ui_config(
    ("STAT", "Gain", "gain")
)


Bank.upgrade_config(
    ("Gain", "gain", "max_gn", "price_gn", "rate_gn")
    )