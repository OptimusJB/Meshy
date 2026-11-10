from Modules.Label import Label
from Modules.VBoxSelector import VBoxSelector

class SelecteurAppareil(VBoxSelector):
    def __init__(self):
        super().__init__()

    def resize_custom(self, largeur_max, hauteur_max) -> tuple[int, int, int, int]:
        # il y a le sélecteur bluetooth usb au dessus
        return [0, 2, largeur_max, hauteur_max - 2]

    def draw_custom(self):
        # on vérifie s'il n'y a pas d'erreur
        if self.parent.search:
            self.liste_labels = [Label("Recherche en cours...")]
            self.selected = -1
        elif self.liste_labels and self.liste_labels[0].texte == "Une erreur est survenue":
            self.selected = -1
        elif self.selected == -1:
            self.selected = 0
        super().draw_custom()

    def input_custom(self, touche: int) -> bool:
        if self.liste_labels and self.liste_labels[0].texte == "Une erreur est survenue":
            return False
        return super().input_custom(touche)

    def on_ready_custom(self):
        super().on_ready_custom()
        self.ask_focus()