import curses
from Modules.Signals import signals

class Widget:
    def __init__(self):
        self.ecran = None
        self.parent = None
        self.fils = [] # liste de Widgets qui recevront automatiquement l'input, le draw et le resize
        self.a_focus = False

    def get_dimensions(self)->tuple:
        # renvoie un tuple de la forme (largeur, hauteur)
        if self.ecran is None:
            raise RuntimeError("appel de get_dimensions alors que le widget n'est pas dans l'arborescence")
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
        if widget_fils.parent is None:
            # on appelle resize pour le widget_fils et pour les potentiels fils
            if self.ecran is not None:
                widget_fils.resize(self.ecran)  # important qu'il soit au début car il peut lever une exception

            widget_fils.parent = self
            self.fils.append(widget_fils)

            if self.ecran is not None:
                widget_fils.on_ready()
            return
        raise RuntimeError("le widget en paramètre de add_child est déjà dans l'arborescence (faire remove_child avant)")

    def remove_ecran(self):
        # on retire l'écran et on appelle aussi la fonction pour les fils
        self.ecran = None
        for element in self.fils:
            element.remove_ecran()

    def remove_child(self, widget_fils) -> None:

        if widget_fils in self.fils:
            # on le retire
            if widget_fils.contient_focus() and self.ecran is not None:
                # le focus est donné au parent
                # note importante : si le fils puis le parent sont supprimés dans le même évènement, le focus ira à la vue (vu que le parent n'a pas encore le focus à ce moment là, il n'enverra pas de signal pour mettre le focus au parent du parent)
                # pour ne pas avoir ce problème il faut supprimer le parent puis le fils (voire juste le parent)
                self.ask_focus()
            widget_fils.parent = None
            widget_fils.remove_ecran()
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
        # normalement lors d'un draw il n'y a pas de changement de self.fils mais on met quand même la sécurité
        for element in list(self.fils):
            if element in self.fils:
                element.draw()

    def input(self, touche:int) -> None:
        # on check l'input, si input_custom renvoie False on l'envoi au parent
        if not self.input_custom(touche) and self.parent is not None:
            self.parent.input(touche)

    def on_ready(self):
        self.on_ready_custom()
        # note importante : il y a ici un list() car dans le cas où un élément est add_child dans le on_ready_custom (le add_child déclenche le on_ready du nouveau child), celui-ci se retrouve dans la boucle et son on_ready est déclenché une seconde fois
        for element in list(self.fils):
            # on vérifie que l'élément est bien toujours dans self.fils
            if element in self.fils:
                element.on_ready()

    def resize(self, ecran_parent:curses.window) -> None:
        hauteur_max, largeur_max = ecran_parent.getmaxyx()
        x, y, largeur, hauteur = self.resize_custom(largeur_max, hauteur_max)  # important que çe soit en premier (parent -> fils)

        # on vérifie la taille
        if largeur <= 0 or hauteur <= 0:
            raise ValueError(f"dimensions sous-fenêtre invalide : ({largeur}, {hauteur})")
        if x + largeur > largeur_max or y + hauteur > hauteur_max:
            raise ValueError(f"sous-fenêtre trop grande, maximale : ({largeur_max}, {hauteur_max}), actuelle : ({largeur}, {hauteur})")

        # on recrée la fenêtre
        self.create_sub_window(ecran_parent, x, y, largeur, hauteur)

        # normalement lors d'un resize il n'y a pas de changement de self.fils mais on met quand même la sécurité
        for element in list(self.fils):
            if element in self.fils:
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
        # ici on met list() pour éviter qu'un nouveau venu (add_child pendant le parcours, et donc ajout dans self.fils) ne reçoive un signal arrivé avant son arrivé
        for element in list(self.fils):
            if element in self.fils:
                element.signal_received(nom_signal, data)

    def ask_focus(self):
        if self.ecran is None:
            raise RuntimeError("tentative de demande focus sur un widget qui n'est pas dans l'arborescence")
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

    def on_ready_custom(self):
        pass  # à redéfinir dans les classes filles