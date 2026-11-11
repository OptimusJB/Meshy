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
        self.y_offset = 0

    def draw_custom(self):
        # on check et change la position et la taille y des labels (car leur taille a peut-être changé sans resize)
        # on détermine l'offset y
        hauteur = self.get_dimensions()[1]

        if 0 <= self.selected < len(self.fils):
            debut = sum(len(l.get_lignes()) for l in self.fils[:self.selected])
            fin = debut + len(self.fils[self.selected].get_lignes())

            if debut < self.y_offset:  # sélection au-dessus de la fenêtre
                self.y_offset = debut
            elif fin > self.y_offset + hauteur:  # sélection sous la fenêtre
                self.y_offset = fin - hauteur

        # bornes : pas d'offset négatif, pas de vide en bas
        total = sum(len(l.get_lignes()) for l in self.fils)
        self.y_offset = max(0, min(self.y_offset, total - hauteur))

        y = -self.y_offset
        i = -1
        for label in self.fils:
            i += 1
            nb_lignes = len(label.get_lignes())
            label.size[1] = nb_lignes
            label.y = y


            # on vérifie qu'on est toujours dans la fenêtre
            if y >= self.get_dimensions()[1] or y < 0:
                label.do_draw = False
                y += nb_lignes
                continue

            label.do_draw = True
            y += nb_lignes

            # on change le surlignage
            #log.log("selected = " + str(self.selected) + " i = " + str(i))
            if i == self.selected:
                label.style = curses.A_REVERSE
            else:
                label.style = curses.A_NORMAL
            label.resize(self.ecran)

    def clear(self):
        for fils in list(self.fils):
            self.remove_child(fils)

    def selection(self, label_select):
        pass    # à réécrire dans les classes filles, pour faire quelque chose quand on sélectionne un label

    def input_custom(self, touche: int) -> bool:
        if len(self.fils) > 0:
            if touche == curses.KEY_UP:
                self.selected = (self.selected - 1) % len(self.fils)
                self.fils[self.selected].ask_focus()
                return True
            elif touche == curses.KEY_DOWN:
                self.selected = (self.selected + 1) % len(self.fils)
                self.fils[self.selected].ask_focus()
                return True
        return False