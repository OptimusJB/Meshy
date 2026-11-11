import curses
from asyncio import CancelledError
from bleak.exc import BleakDBusError
from Modules import Widget
import asyncio
from Modules.Log import log
from Modules.MeshcoreManager import meshcore_manager
from Modules.Signals import signals
from Composants.SelecteurAppareil import SelecteurAppareil
from Modules.Label import Label
from Composants.PinEdit import PinEdit
from Modules.BoxContainer import BoxContainer

class Connexion(Widget.Widget):
    def __init__(self):
        super().__init__()
        self.transposition_mode = {0:"bluetooth", 1:"usb"}
        self.selected_mode = 0
        self.search = None

        self.selecteur = SelecteurAppareil()
        self.add_child(self.selecteur)

        self.search_usb_actif = False
        self.search_bluetooth_actif = False
        #self.task_finished = True

        self.tentative_connexion = None

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
        resultat = False
        if touche == curses.KEY_LEFT:
            self.selected_mode = (self.selected_mode - 1) % len(self.transposition_mode.keys())
            resultat = True
        elif touche == curses.KEY_RIGHT:
            self.selected_mode = (self.selected_mode + 1) % len(self.transposition_mode.keys())
            resultat = True

        if resultat == True and (touche == curses.KEY_LEFT or touche == curses.KEY_RIGHT):
            # on reset les appareils et on lance une recherche
            self.selecteur.clear()
            if self.search is not None:
                #self.search.cancel()
                #self.task_finished = False
                self.search = None
            if self.transposition_mode[self.selected_mode] == "bluetooth" and not self.search_bluetooth_actif:
                self.search = asyncio.create_task(meshcore_manager.scan_ble())
                self.search_bluetooth_actif = True
                self.search.add_done_callback(self.search_fini)
            elif not self.search_usb_actif:
                self.search = asyncio.create_task(meshcore_manager.scan_usb())
                self.search_usb_actif = True
                self.search.add_done_callback(self.search_fini)

        if touche == ord("\n") and self.search is None:   # KEY_ENTER ne fonctionne pas
            if self.transposition_mode[self.selected_mode] == "bluetooth":
                # on demande le pin (on crée un boxcontainer avec un lineedit dedans)
                pin = BoxContainer()
                pin.selected = self.selecteur.fils[self.selecteur.selected].adresse
                pin.titre = "Entrez le pin"
                pin.size = [20, 3]
                pin.x, pin.y = [len(pin.selected), self.selecteur.fils[self.selecteur.selected].y + 1]

                line_edit = PinEdit()
                line_edit.prefixe = "Pin : "
                line_edit.size = [100.0, 1]
                line_edit.x, line_edit.y = 1, 1
                pin.add_child(line_edit)
                self.add_child(pin)
                line_edit.ask_focus()
                return True
            elif self.transposition_mode[self.selected_mode] == "usb":
                self.changer_vue("connexion_usb")
                return True
        return resultat

    def resize_custom(self, largeur, hauteur) -> tuple[int, int, int, int]:
        return (0, 0, largeur, hauteur)

    def search_fini(self, tache):
        resultat = tache.result()

        #self.task_finished = True
        if resultat["type"] == "bluetooth":
            self.search_bluetooth_actif = False
        elif resultat["type"] == "usb":
            self.search_usb_actif = False

        # on return si pas le bon type
        if resultat["type"] != self.transposition_mode[self.selected_mode]:
            return

        liste_appareils = resultat["appareils"]
        liste_adresses = resultat["adresses"]

        """
        fichier = open("appareils.txt", "w")
        fichier.write(str(liste_appareils))
        fichier.close()
        """
        self.search = None

        # on crée les labels pour le selecteur
        self.selecteur.clear()
        i = -1
        for appareil in liste_appareils:
            i += 1
            # on filtre les none
            if appareil is None:
                continue
            label = Label()
            label.texte = appareil
            label.size = [self.selecteur.get_dimensions()[0], 1]
            label.adresse = liste_adresses[i]
            self.selecteur.add_child(label)

        # on envoie un signal pour refresh l'affichage
        signals.add_signal("refresh_affichage", None)


    def on_ready_custom(self):
        # on reset les appareils et on lance une recherche
        if self.transposition_mode[self.selected_mode] == "bluetooth":
            self.selecteur.clear()
            if not self.search_bluetooth_actif:
                self.search = asyncio.create_task(meshcore_manager.scan_ble())
                self.search_bluetooth_actif = True
                self.search.add_done_callback(self.search_fini)

    def tentative_connexion_fini(self, tache):
        self.tentative_connexion = None
        try:
            resultat = tache.result()
        except FileNotFoundError:   # erreur au pif qui ne va pas trigger (TODO à changer)
            return

        if not resultat:
            return

        log.log("connexion réussie")

    def signal_custom(self, nom_signal:str, data):
        if nom_signal == "pin choisi":
            pin = data["pin"]
            appareil = data["appareil"]
            # on tente la connexion s'il n'y en a pas encore
            if not self.tentative_connexion:
                self.tentative_connexion = asyncio.create_task(meshcore_manager.se_connecter_ble(appareil, pin))
                self.tentative_connexion.add_done_callback(self.tentative_connexion_fini)