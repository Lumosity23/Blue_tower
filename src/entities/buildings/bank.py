from .Building import Building


class Bank(Building):
    def __init__(self, x, y, data, game, uid):
        super().__init__(x, y, data, game, tag="BANK", uid=uid)

        # Gain section
        self.gain = 100

        self.mapping = {"xy": self.rect.center, "text": self.gain}

    def update(self, dt):

        if self.delay(3, dt):
            self._EVENTBUS.publish("EARN_MONEY", self.gain)
            self._EVENTBUS.publish("SHOW_FT", self.mapping)

        super().update(dt)


Bank.ui_config(("STAT", "Gain", "gain"))


Bank.upgrade_config(("Gain", "gain", 100, 400, 5))
