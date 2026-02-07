from settings import Settings


class EventManager():

    def __init__(self):
        
        self.listeners = {}

    
    def subscribe(self, event_type: str, callback: function) -> None:
        '''
            permet de cree un eventment\n
            event_type = nom significatif pour le callback\n
            callback = le nom de la fontction que tu assigne a l'evenement\n
        '''
        if event_type not in self.listeners:
            # Cree une liste pour stocker les different fonction a executer pour l'evenement
            self.listeners[event_type] = []

        # Ajout de la fonction a exec pour un l'evenement
        self.listeners[event_type].append(callback)

    
    def publish(self, event_type: str, data=None) -> None:
        '''
            executer un event avec de la donner en particuler (data facultatif)
        '''
        if event_type in self.listeners:
            # Executer tout les fonction associer a l'evenement
            for callback in self.listeners[event_type]:
                # Appel la fonction en question avec les argument
                callback(data)