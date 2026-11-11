import curses
from Modules import Widget
from Modules.Log import log

CENTER = -1

class Label(Widget.Widget):
    def __init__(self, texte=""):
        super().__init__()
        self.x = 0  # nombre OU CENTER
        self.y = 0  # nombre OU CENTER
        self.size = [max(len(texte), 1) + 1, 1]  # largeur, hauteur
        self.texte = texte
        self.retour_ligne = True
        self.style = curses.A_NORMAL

        self.do_draw = True # si False, le label ne sera pas affiché, mais il sera toujours dans la liste des fils du parent. Cela permet de garder les labels en mémoire, mais de ne pas les afficher.


    def get_lignes(self):
        if not self.retour_ligne or not self.texte:
            return [str(self.texte)]
        liste = []
        texte_split = self.texte.split(" ")
        ligne_actuelle = ""
        avancement = 0

        while avancement < len(texte_split):
            premier_mot = True
            while len(ligne_actuelle + texte_split[avancement]) < self.size[0] - self.x or premier_mot:
                premier_mot = False
                ligne_actuelle = ligne_actuelle + texte_split[avancement] + " "
                avancement += 1
                if avancement == len(texte_split):
                    break
            if ligne_actuelle[-1] == " ":
                ligne_actuelle = ligne_actuelle[:-1]
            liste.append(ligne_actuelle)
            ligne_actuelle = ""
        return liste

    def draw_custom(self):
        # on met un try au cas où la fenêtre est trop petite
        if not self.do_draw:
            return
        try:
            lignes = self.get_lignes()
            x = 0#self.x
            if x == CENTER:
                x = round(self.pourcentage_vers_coordonnes(50)[0] - len(self.texte) / 2)
            y = 0#self.y
            if y == CENTER:
                y = round(self.pourcentage_vers_coordonnes(50)[1] - len(lignes) / 2)

            for ligne_actuelle in lignes:
                #log.log(ligne_actuelle)
                self.ecran.addstr(y, x, ligne_actuelle, self.style)
                y += 1

        except curses.error:
            pass

    def resize_custom(self, largeur_max, hauteur_max) -> tuple[int, int, int, int]:
        self.do_draw = True
        x, y, largeur, hauteur = self.auto_fit(self.x, self.y, self.size[0], self.size[1], largeur_max, hauteur_max)
        if y != self.y:
            self.do_draw = False

        return (x, y, largeur, hauteur)