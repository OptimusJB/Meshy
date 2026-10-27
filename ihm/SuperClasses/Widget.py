import curses

class Widget:
    def __init__(self, ecran_parent:curses.window, x:int, y:int, largeur:int, hauteur:int):
        # note : x et y sont le coin supérieur gauche du parent, pas du terminal

        self.ecran = ecran_parent.derwin(hauteur, largeur, y, x)
        self.fils = [] # liste de Widgets qui recevront automatiquement l'input, le draw et le resize

    def get_dimensions(self)->tuple:
        # renvoie un tuple de la forme (largeur, hauteur)
        dimensions = self.ecran.getmaxyx()
        return (dimensions[1], dimensions[0])

    def pourcentage_vers_coordonnes(self, pourcentage:float) -> tuple:
        # renvoie un tuple de la forme (x, y)
        return (round(self.get_dimensions()[0] / 100 * pourcentage), round(self.get_dimensions()[1] / 100 * pourcentage))

    def coordonnes_vers_pourcentage(self, coordonnes:int) -> tuple:
        # renvoie un tuple de la forme (%x, %y)
        return (100 / self.get_dimensions()[0] * coordonnes, 100 / self.get_dimensions()[1] * coordonnes)

    def draw(self) -> None:
        #self.ecran.erase()
        #self.ecran.refresh()
        for element in self.fils:
            element.draw()

        self.draw_custom()

    def input(self, touche:int) -> None:
        # on parcours les éléments à l'envers pour garder une logique par rapport au draw (celui au premier plan prend l'input en premier)
        for element in reversed(self.fils):
            if not element.input(touche):
                break
        self.input_custom(touche)

    def resize(self, largeur_max:int, hauteur_max:int) -> None:
        self.resize_custom(largeur_max, hauteur_max)  # important que çe soit en premier (parent -> fils)
        # on récupère la nouvelle taille
        hauteur_max_fils, largeur_max_fils = self.ecran.getmaxyx()

        for element in self.fils:
            element.resize(largeur_max_fils, hauteur_max_fils)

    def draw_custom(self) -> None:
        pass    # à redéfinir dans les classes filles

    def input_custom(self, touche:int) -> bool:
        pass  # à redéfinir dans les classes filles
        # note : si le booléen est à False, l'input n'est plus transmis (ni au fils ni au parent)

    def resize_custom(self, largeur_max:int, hauteur_max:int) -> None:
        pass  # à redéfinir dans les classes filles