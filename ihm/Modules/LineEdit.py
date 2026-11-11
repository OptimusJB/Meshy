import curses
from Modules import Widget
from Modules import Label
from Modules.Log import log
from Modules.Signals import signals
import time

CENTER = -1

class LineEdit(Label.Label):
    def __init__(self):
        super().__init__()
        self.prefixe = ""
        self.contenu = ""

        self.available_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_&é'\"èà()[]{}#<>ùô$€!.,?/:; "
        self.x_offset = 0
        self.retour_ligne = False

    def maj_offset(self):
        x_max = self.get_dimensions()[0] - 1
        if len(self.texte) > x_max:
            self.x_offset = len(self.texte) - x_max
        else:
            self.x_offset = 0
        return self.x_offset

    def maj_texte(self):
        self.texte = self.prefixe + self.contenu + "_"

        self.maj_offset()
        if self.x_offset != 0:
            # on change le texte
            self.texte = self.prefixe + "..." + self.contenu[self.x_offset + 3:] + "_"

    def draw_custom(self):
        self.maj_texte()
        super().draw_custom()

    def input_custom(self, touche:int) -> bool:
        if touche == curses.KEY_BACKSPACE or touche == 127:
            self.contenu = self.contenu[:-1]
            self.maj_texte()
            return True
        else:
            char = chr(touche)
            if char in self.available_characters:
                self.contenu += char
                self.maj_texte()
                return True
        return False