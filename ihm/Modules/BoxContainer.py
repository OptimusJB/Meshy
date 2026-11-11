import curses
from multiprocessing.forkserver import read_signed

from Modules import Widget
from Modules.Log import log
from Modules.Signals import signals
import time

class BoxContainer(Widget.Widget):
    # container qui crée une bordure autour de son fils (qui possède un x, y et size), et qui peut éventuellement mettre un titre
    # c'est le container qui s'adapte au fils, pas l'inverse
    def __init__(self):
        super().__init__()
        self.titre = ""
        self.x = 0
        self.y = 0
        self.size = [0, 0]  # largeur, hauteur


    def draw_custom(self):
        try:
            self.ecran.box()
            if self.titre:
                self.ecran.addstr(0, 2, " " + self.titre + " ", curses.A_BOLD)
        except curses.error:
            log.log("BoxContainer : la fenêtre est trop petite pour dessiner la bordure")

    def resize_custom(self, largeur_max, hauteur_max) -> tuple[int, int, int, int]:
        self.do_draw = True
        x, y, largeur, hauteur = self.auto_fit(self.x, self.y, self.size[0], self.size[1], largeur_max, hauteur_max)
        if y != self.y:
            self.do_draw = False

        return (x, y, largeur, hauteur)