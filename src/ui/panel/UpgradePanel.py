import json
from utils.path import resource_path as rp
from ui.UIPanel import UIPanel
from ui.UIProgressBar import UIProgressBar
from ui.UIButton import UIButton
from ui.UIUpgradeBoard import UIUpgradeBoard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App
    from entities.Entity import Entity
    from UIElement import UIElement


class UpgradePanel(UIPanel):

    def __init__( self, game: "App" ):

        self.game = game
        w, h = 400, game.st.SCREEN_HEIGHT
        self.size = w, h

        with open( rp(self.game.st.UPGRADE_SCHEMA_PATH), 'r') as f:
            self.schemas: dict[dict] = json.load(f)

        super().__init__( game.st.SCREEN_WIDTH, 0, w, h, uid="InfoPanel" )

        self.set_label("Ugrade", 100)
        self.set_animation( (self.game.st.SCREEN_WIDTH - self.size[0], 0), (self.game.st.SCREEN_WIDTH, 0), 1000 )
        self.visible = False

        self.back_btn = UIButton(self.rect.width - 40, 10, "X", lambda: self.kill(True), (50, 50, 50), uid=f"{self.uid}_btn_back")
        self.add_child(self.back_btn)

        # Entity INFO
        self.current_entity: Entity = None
        self.ui_pool = [UIUpgradeBoard() for _ in range(3)]
        self.active_children: list["UIElement"] = []

        # Souscription
        self.game.eventManager.subscribe( "ELEMENT_UPGRADE", self.show_element )
        self.game.eventManager.subscribe( "ELEMENT_UNUPGRADE", self.kill )     
        
        # Test de UIUpgradeBoard
        """ test_upboard = UIUpgradeBoard(20, 150, self.rect.width - 40, 220, "Test")
        test_upboard.set_progress_bar(100, lambda: 50) # max_val, curr_val
        test_upboard.set_upgrade_button(self.test_call, 30, 20) # callback, price, rate

        self.add_child(test_upboard) """


    def test_call(self) -> None:
        print("Test du UIUpgradeBoard")


    def show_element( self, entity: "Entity" ) -> None:

        self.game.eventManager.publish( "ELEMENT_UNSELECTED" )
        self.current_entity = entity
        self.make_data(entity)
        super().show()
    

    def kill(self, back: bool=False):
        
        if not self.visible:
            return
        if back:
            self._EVENTBUS.publish("ELEMENT_SELECTED", self.current_entity)

        super().kill()
    

    def reset_data_child( self ) -> None:

        while self.active_children:
            child = self.active_children.pop(0)
            child.active = False
            self.remove_child(child)


    def make_data(self, entity: "Entity") -> None:
        
        # Setup de notre nouvelle entite
        self.reset_data_child()
        self.current_entity = entity

        if entity.tag in self.schemas:
            entity_schema = self.schemas.get(entity.tag)
            # print(entity_schema)
        else: 
            # print("rien trouver dans les donner !")
            return

        # Variable de pos pour les different elements
        pos_x = 20 # constante le long de notre infoPanel
        pos_y = self.label.rect.bottom + 70 # valeur qui va augmenter au cours de la boucle de creation
        padding = 20

        for upgrade in entity_schema:
            # Recupere un element correspondant encore non utiliser
            upgrade: dict
            for e in self.ui_pool:
                if not e.active:
                    element: "UIUpgradeBoard" = e
                    element.active = True
                    element.visible = True
                    self.add_child(element)
                    self.active_children.append(element)

                    # Recupere les eventuelles pointers
                    def get_attribut(attr):
                        if attr is None: return None
                        if hasattr(entity, attr):
                             return entity.__getattribute__(attr)
                        print(f"aucun attribut du nom de {attr} n'as ete trouver sur {entity.__name__()}")
                    
                    def get_attribut_pointer(attr):
                        if attr is None: 
                            return lambda: None # Retourne une fonction qui renvoie None

                        if hasattr(entity, attr):
                            # On retourne une fonction (un "getter")
                            return lambda name=attr: getattr(entity, name)

                        print(f"aucun attribut du nom de {attr} sur {type(entity).__name__}")
                        return lambda: None

                    # Recuperation des info utile
                    label = upgrade["label"]
                    map: dict = upgrade["mapping"]

                    max_val = get_attribut(map.get("max"))
                    current_val = get_attribut_pointer(map.get("current"))
                    attr_name = map["current"]
                    price = get_attribut(map.get("price"))
                    rate = get_attribut(map.get("rate", 0))

                    # La lambda ne sert plus qu'à "emballer" l'appel avec les variables capturées
                    callback = lambda e=entity, a=attr_name, r=rate, p=price: self.apply_upgrade(e, a, r, p)

                    element.setup(pos_x, pos_y, self.rect.w - 40, 220, label)
                    element.set_progress_bar(max_val, current_val)
                    element.set_upgrade_button(callback, price, rate)

                    pos_y += 220 + padding
                    # print(f" ma taille : {rect.h} et mon topleft = {rect.topleft} -> la soustraction des deux dois faire mon topleft = {element.rect.h - pos_y}")
                    break
    

    def apply_upgrade(self, entity, attr_name, rate, price):
        # 1. Vérification du prix (via ton WalletManager par exemple)
        if not self.game.walletManager.buy(price):
            self._EVENTBUS.publish("PLAY_SFX", "ERROR")
            return

        # 2. On récupère la valeur actuelle
        current_val = getattr(entity, attr_name)

        # 3. Calcul de la nouvelle valeur (hausse en %)
        # On arrondit pour éviter les flottants bizarres (ex: 10.00000004)
        new_val = round(current_val * (1 + rate / 100))

        # 4. Application
        setattr(entity, attr_name, new_val)

        # 5. Paiement et Feedback
        # self._EVENTBUS.publish("PLAY_SFX", "UPGRADE_SUCCESS")
        # print(f"Upgrade {attr_name} : {current_val} -> {new_val}")