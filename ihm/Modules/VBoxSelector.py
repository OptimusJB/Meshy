import curses
from pickle import FALSE

from Modules import Widget
from Modules.Label import Label
from Modules.Log import log


class VBoxSelector(Widget.Widget):
    # il s'agit d'un module prenant une liste de labels, et permettant de choisir entre tous
    def __init__(self):
        super().__init__()
        self.selected = 0

    def draw_custom(self):
        # on check et change la position et la taille y des labels (car leur taille a peut-être changé sans resize)
        y = 0
        i = 0
        for label in self.fils:
            # on vérifie qu'on est toujours dans la fenêtre
            if y >= self.get_dimensions()[1]:
                label.do_draw = False
                continue

            label.do_draw = True
            nb_lignes = len(label.get_lignes())
            label.size[1] = nb_lignes
            label.y = y
            y += nb_lignes

            # on change le surlignage
            log.log("selected = " + str(self.selected) + " i = " + str(i))
            if i == self.selected:
                label.style = curses.A_REVERSE
            else:
                label.style = curses.A_NORMAL
            i += 1
            label.resize(self.ecran)

    def selection(self, label_select):
        pass    # à réécrire dans les classes filles, pour faire quelque chose quand on sélectionne un label

    def input_custom(self, touche: int) -> bool:
        if len(self.fils) > 0:
            if touche == curses.KEY_UP:
                self.selected = (self.selected - 1) % len(self.fils)
                return True
            elif touche == curses.KEY_DOWN:
                self.selected = (self.selected + 1) % len(self.fils)
                return True
            elif touche == ord("\n"):
                self.selection(self.fils[self.selected])
                return True
        return False

    def on_ready_custom(self):
        for fils in list(self.fils):
            self.remove_child(fils)