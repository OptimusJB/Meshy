import curses
from Modules import Widget
import asyncio
from Modules.MeshcoreManager import meshcore_manager
from Modules.Signals import signals
from Composants.SelecteurAppareil import SelecteurAppareil

from Modules.Label import Label

class Connexion(Widget.Widget):
    def __init__(self):
        super().__init__()
        self.transposition_mode = {0:"bluetooth", 1:"usb"}
        self.selected_mode = 0
        self.appareils = []
        self.search = None

        self.selected_device = 0

        self.selecteur = SelecteurAppareil()
        self.add_child(self.selecteur)

    def draw_custom(self):
        # on met un try au cas où la fenêtre est trop petite
        try:
            # on affiche les deux choix au centre
            x = round(self.pourcentage_vers_coordonnes(50)[0] - len("Bluetooth  usb")/2)
            y = 0
            attribut_texte = curses.A_NORMAL
            if self.transposition_mode[self.selected_mode] == "bluetooth":
                attribut_texte = curses.A_REVERSE
            self.ecran.addstr(y, x, "Bluetooth", attribut_texte)

            attribut_texte = curses.A_NORMAL
            if self.transposition_mode[self.selected_mode] == "usb":
                attribut_texte = curses.A_REVERSE
            self.ecran.addstr(y, x + len("Bluetooth  "), "Usb", attribut_texte)
        except curses.error:
            pass

        try:
            # affichage des appareils
            y = 2
            x = 0
            attribut_texte = curses.A_NORMAL

        except curses.error:
            pass

    def input_custom(self, touche:int) -> bool:
        if touche == curses.KEY_LEFT:
            self.selected_mode = (self.selected_mode - 1) % len(self.transposition_mode.keys())
            return True
        elif touche == curses.KEY_RIGHT:
            self.selected_mode = (self.selected_mode + 1) % len(self.transposition_mode.keys())
            return True
        return False

    def resize_custom(self, largeur, hauteur) -> tuple[int, int, int, int]:
        return (0, 0, largeur, hauteur)

    def search_fini(self, tache):
        try:
            liste_appareils = tache.result()
        except ValueError:
            liste_appareils = ["Une erreur est survenue"]
        fichier = open("appareils.txt", "w")
        fichier.write(str(liste_appareils))
        fichier.close()
        self.search = None

        # on crée les labels pour le selecteur
        for appareil in liste_appareils:
            label = Label()
            label.texte = appareil
            label.size = [self.selecteur.get_dimensions()[0], 1]
            self.selecteur.add_child(label)

        # on envoie un signal pour refresh l'affichage
        signals.add_signal("refresh_affichage", None)


    def on_ready_custom(self):
        # on reset les appareils et on lance une recherche
        self.selected_device = 0
        self.appareils = []
        if self.transposition_mode[self.selected_mode] == "bluetooth":
            self.search = asyncio.create_task(meshcore_manager.scan_ble())
            self.search.add_done_callback(self.search_fini)