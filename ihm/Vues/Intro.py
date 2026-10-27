import curses
from Modules import Widget

class Intro(Widget.Widget):
    def __init__(self, ecran_parent:curses.window, x:int, y:int, largeur:int, hauteur:int):
        super().__init__(None, ecran_parent, x, y, largeur, hauteur)
        self.transposition = {0:"ihm", 1:"flash"}
        self.selected = 0

    def draw_custom(self):
        # on met un try au cas où la fenêtre est trop petite
        try:
            # on affiche les deux choix au centre
            x = round(self.pourcentage_vers_coordonnes(50)[0] - len("Se connecter à un compagnon")/2)
            y = self.pourcentage_vers_coordonnes(50)[1]
            attribut_texte = curses.A_NORMAL
            if self.transposition[self.selected] == "ihm":
                attribut_texte = curses.A_REVERSE
            self.ecran.addstr(y, x, "Se connecter à un compagnon", attribut_texte)

            x = round(self.pourcentage_vers_coordonnes(50)[0] - len("Flasher un compagnon")/2)
            y += 1
            attribut_texte = curses.A_NORMAL
            if self.transposition[self.selected] == "flash":
                attribut_texte = curses.A_REVERSE
            self.ecran.addstr(y, x, "Flasher un compagnon", attribut_texte)
        except curses.error:
            pass

    def input_custom(self, touche:int) -> bool:
        if touche == curses.KEY_UP:
            self.selected = (self.selected - 1) % len(self.transposition.keys())
            return True
        elif touche == curses.KEY_DOWN:
            self.selected = (self.selected + 1) % len(self.transposition.keys())
            return True
        return False

    def resize_custom(self, ecran_parent:curses.window):
        dimensions = ecran_parent.getmaxyx()
        self.ecran.resize(dimensions[0], dimensions[1])