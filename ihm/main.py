import curses
from Vues import Intro

class Orchestrateur:
    def __init__(self):
        self.vue_base = Intro.Intro
        self.changement_vue = None  # mettre une vue pour que le changement s'opère

    def run(self, ecran:curses.window):
        # initialisation
        curses.curs_set(0)  # curseur caché
        dimensions = ecran.getmaxyx()

        vue = self.vue_base(ecran, 0, 0, dimensions[1], dimensions[0])

        while True:
            # on vérifie si'il y a un changement de vue
            if self.changement_vue:
                vue = self.changement_vue(ecran, 0, 0, dimensions[1], dimensions[0])
                self.changement_vue = None

            ecran.erase()  # clear de l'écran

            vue.draw()
            ecran.refresh()  # refresh de l'écran

            # ecran.untouchwin() # permet de ne pas rafraîchir l'écran principal
            touche = ecran.getch()  # récupération de la touche (bloquant)

            # on check si la touche est un resize
            if touche == curses.KEY_RESIZE:
                dimensions = ecran.getmaxyx()
                vue.resize(dimensions[1], dimensions[0])
            else:
                vue.input(touche)


if __name__ == '__main__':
    orchestrateur = Orchestrateur()
    curses.wrapper(orchestrateur.run) # lancement du main