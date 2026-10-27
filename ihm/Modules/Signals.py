class Signal:
    # classe qui permet d'envoyer des infos aux différents Widgets de l'interface, ainsi qu'à l'orchestrateur
    def __init__(self):
        self.signaux = []  # contient des dico sous la forme {nom, data} avec nom str et data inconnu

    def add_signal(self, nom_signal:str, data):
        # data peut être n'importe quoi
        signal = {"nom":nom_signal, "data":data}
        self.signaux.append(signal) # ce signal sera envoyé à tout le monde par l'orchestrateur

    def traiter_signaux(self):
        # renvoie la liste de tous les signaux et supprime le contenu de self.signaux
        signaux_renvoi = list(self.signaux)
        self.signaux = []
        return signaux_renvoi

    def clear(self):
        # supprime tous les signaux stockés
        self.signaux = []

signals = Signal()
