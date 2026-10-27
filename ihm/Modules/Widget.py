import curses
from Modules.Signals import signals

class Widget:
    def __init__(self, widget_parent, ecran_parent, x:int, y:int, largeur:int, hauteur:int):
        # note : x et y sont le coin supérieur gauche du parent, pas du terminal
        # on met à la fois widget et ecran pour le parent, car dans le cas où on est tout en haut on a seulement un écran et pas un widget
        self.parent = widget_parent
        self.ecran = ecran_parent.derwin(hauteur, largeur, y, x)
        self.fils = [] # liste de Widgets qui recevront automatiquement l'input, le draw et le resize
        self.a_focus = False

    def get_dimensions(self)->tuple:
        # renvoie un tuple de la forme (largeur, hauteur)
        dimensions = self.ecran.getmaxyx()
        return (dimensions[1], dimensions[0])

    def pourcentage_vers_coordonnes(self, pourcentage:float) -> tuple:
        # renvoie un tuple de la forme (x, y)
        return (round(self.get_dimensions()[0] / 100 * pourcentage), round(self.get_dimensions()[1] / 100 * pourcentage))

    def coordonnes_vers_pourcentage(self, x, y) -> tuple:
        # renvoie un tuple de la forme (%x, %y)
        return (100 / self.get_dimensions()[0] * x, 100 / self.get_dimensions()[1] * y)

    def draw(self) -> None:
        #self.ecran.erase()
        #self.ecran.refresh()
        self.draw_custom()
        for element in self.fils:
            element.draw()

    def input(self, touche:int) -> None:
        # on check l'input, si input_custom renvoie False on l'envoi au parent
        if not self.input_custom(touche) and self.parent is not None:
            self.parent.input(touche)

    def resize(self, ecran_parent:curses.window) -> None:
        self.resize_custom(ecran_parent)  # important que çe soit en premier (parent -> fils)

        for element in self.fils:
            element.resize(self.ecran)

    def est_dans(self, racine):
        widget_actuel = self
        while (widget_actuel != racine and isinstance(widget_actuel, Widget)):
            widget_actuel = widget_actuel.parent
        if widget_actuel == racine:
            return True
        return False

    def signal_received(self, nom_signal:str, data):
        self.signal_custom(nom_signal, data)
        for element in self.fils:
            element.signal_received(nom_signal, data)

    def ask_focus(self):
        signals.add_signal("&ask_focus&", self)

    def changer_vue(self, nom_vue:str):
        signals.add_signal("&ask_changement_vue&", nom_vue)

    def draw_custom(self) -> None:
        pass    # à redéfinir dans les classes filles

    def input_custom(self, touche:int) -> bool:
        return False  # à redéfinir dans les classes filles
        # note : si le booléen est à False, l'input est transmis au parent

    def resize_custom(self, ecran_parent:curses.window) -> None:
        pass  # à redéfinir dans les classes filles

    def signal_custom(self, nom_signal:str, data):
        pass  # à redéfinir dans les classes filles
