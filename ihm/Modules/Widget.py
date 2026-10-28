import curses
from Modules.Signals import signals

class Widget:
    def __init__(self):
        self.ecran = None
        self.parent = None
        self.fils = [] # liste de Widgets qui recevront automatiquement l'input, le draw et le resize
        self.a_focus = False
        self.ready_trigger = False  # permet de n'appeler qu'une seule fois le ready

    def get_dimensions(self)->tuple:
        # renvoie un tuple de la forme (largeur, hauteur)
        dimensions = self.ecran.getmaxyx()
        return (dimensions[1], dimensions[0])

    def contient_focus(self) -> bool:
        # renvoie True si lui ou ses enfants contiennent le focus
        if self.a_focus:
            return True

        resultat = False
        for element in self.fils:
            if element.contient_focus():
                resultat = True
        return resultat

    def create_sub_window(self, ecran_parent, x, y, largeur, hauteur):
        self.ecran = ecran_parent.derwin(hauteur, largeur, y, x)

    def add_child(self, widget_fils) -> None:
        if self.ecran is None:
            # le parent n'est pas dans l'arborescence
            raise RuntimeError("add_child appelé avant que le parent ait un écran (utilise on_ready)")

        if widget_fils.parent is None:
            # on appelle resize pour le widget_fils et pour les potentiels fils
            widget_fils.resize(self.ecran)

            widget_fils.parent = self
            self.fils.append(widget_fils)

            if not widget_fils.ready_trigger:
                widget_fils.ready_trigger = True
                widget_fils.on_ready()
            return
        raise RuntimeError("le widget en paramètre de add_child est déjà dans l'arborescence (faire remove_child avant)")

    def remove_child(self, widget_fils) -> None:
        if widget_fils in self.fils:
            # on le retire
            if widget_fils.contient_focus():
                # le focus est donné au parent
                self.ask_focus()
            widget_fils.parent = None
            #widget_fils.ecran = None
            self.fils.remove(widget_fils)
            return
        raise RuntimeError("le widget à supprimer n'est pas un fils de ce widget")

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
        hauteur_max, largeur_max = ecran_parent.getmaxyx()
        x, y, largeur, hauteur = self.resize_custom(largeur_max, hauteur_max)  # important que çe soit en premier (parent -> fils)

        # on vérifie la taille
        if largeur > largeur_max or hauteur > hauteur_max:
            raise ValueError(f"sous fenêtre trop grande, maximale : ({largeur_max}, {hauteur_max}), actuelle : ({largeur}, {hauteur})")

        # on recrée la fenêtre
        self.create_sub_window(ecran_parent, x, y, largeur, hauteur)

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

    def resize_custom(self, largeur_max, hauteur_max) -> tuple[int, int, int, int]:
        # doit renvoyer un tuple de 4 éléments indiquant les nouvelles dimensions à adopter : (x, y, largeur, hauteur)
        # note : x et y sont le coin supérieur gauche du parent, pas du terminal
        return (0, 0, largeur_max, hauteur_max)  # à redéfinir dans les classes filles

    def signal_custom(self, nom_signal:str, data):
        pass  # à redéfinir dans les classes filles

    def on_ready(self):
        pass  # à redéfinir dans les classes filles