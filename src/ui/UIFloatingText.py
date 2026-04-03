from ui.UIText import UIText


class UIFloatingText(UIText):

    def __init__(self, x, y, text):
        
        super().__init__(x, y, text, 30, (150,50,50))

        if text is "":
            self.visible = False
            self.active = False

        self.lifespan = 1.0
        self.rest_time = self.lifespan
        self.velocity = 50
    

    def reset(self, x, y, text) -> None:
        
        self.remove_all_child()
        self.rest_time = self.lifespan
        self.pos.update(x, y)
        self.rect.center = self.pos.xy
        self.set_text(text, 30, (150,50,50))


    def update(self, dt):
        
        # MAJ du temps de vie
        self.rest_time -= dt

        # On met a jour la transparance du text
        Alpha = (self.rest_time / self.lifespan) * 255
        self.image.set_alpha(int(Alpha))
        
        # MAJ de sa position
        self.pos.y -= self.velocity * dt
        self.rect.center = self.pos.xy
        
        # Verification si encore en vie
        if self.rest_time <= 0:
            self.visible = False
            self.active = False
            return False
        
        super().update(dt)

        return True


    def draw(self, surface, cam_offset: tuple):
        
        self.rect.centerx = self.pos.x - cam_offset[0]
        self.rect.centery = self.pos.y - cam_offset[1]

        super().draw(surface)