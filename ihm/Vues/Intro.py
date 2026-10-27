import curses
from SuperClasses import Widget

class Intro(Widget.Widget):
    def __init__(self, ecran_parent:curses.window, x:int, y:int, largeur:int, hauteur:int):
        super().__init__(ecran_parent, x, y, largeur, hauteur)
        self.transposition = {0:"ihm", 1:"flash"}
        self.selected = 0

    def draw_custom(self):
        # on affiche les deux choix au centre
        x = round(self.pourcentage_vers_coordonnes(50)[0] - len("Se connecter à un compagnon")/2)
        y = self.pourcentage_vers_coordonnes(50)[1]
        self.ecran.addstr(y, x, "Se connecter à un compagnon")

        x = round(self.pourcentage_vers_coordonnes(50)[0] - len("Flasher un compagnon")/2)
        y += 1
        self.ecran.addstr(y, x, "Flasher un compagnon")

    def input_custom(self, touche:int):
        pass

    def resize_custom(self, largeur_max:int, hauteur_max:int):
        self.ecran.resize(hauteur_max, largeur_max)