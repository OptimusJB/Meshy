import curses
from Vues import Intro
from Modules.Signals import signals
from Modules import Widget

class Orchestrateur:
    def __init__(self):
        self.vue_base = Intro.Intro
        #self.changement_vue = None  # mettre une vue pour que le changement s'opère
        self.vue = None
        self.focus = None
        self.do_draw = False

        self.vues = {"intro":Intro.Intro}

    def changer_vue(self, nom_vue:str, ecran:curses.window, dimensions):
        self.vue = self.vues[nom_vue](ecran, 0, 0, dimensions[1], dimensions[0])
        #self.changement_vue = None
        self.focus = self.vue
        self.vue.a_focus = True
        self.do_draw = True

    def run(self, ecran:curses.window):
        # initialisation
        curses.curs_set(0)  # curseur caché
        ecran.timeout(50) # timeout de 50ms pour ne pas rester bloqué au getch()
        dimensions = ecran.getmaxyx()

        self.vue = self.vue_base(ecran, 0, 0, dimensions[1], dimensions[0])
        self.focus = self.vue
        self.vue.a_focus = True

        self.do_draw = True
        while True:

            if self.do_draw:
                self.do_draw = False
                ecran.erase()  # clear de l'écran

                self.vue.draw()
                ecran.refresh()  # refresh de l'écran

            # ecran.untouchwin() # permet de ne pas rafraîchir l'écran principal
            touche = ecran.getch()  # récupération de la touche (bloquant pendant 50ms max)

            if touche != -1:
                self.do_draw = True
                # on check si la touche est un resize
                if touche == curses.KEY_RESIZE:
                    dimensions = ecran.getmaxyx()
                    self.vue.resize(ecran)
                else:
                    self.focus.input(touche)

            # TODO ajouter ici traitement signaux (traiter_signaux avec un while)
            signaux = signals.traiter_signaux()
            while(signaux != []):
                self.do_draw = True
                for signal in signaux:
                    if signal["nom"] == "&ask_focus&":
                        # on vérifie que le widget est dans l'arborescence
                        if isinstance(signal["data"], Widget.Widget) and signal["data"].est_dans(self.vue):
                            # on retire le a_focus de l'ancien s'il y en a un
                            if isinstance(self.focus, Widget.Widget):
                                self.focus.a_focus = False
                            self.focus = signal["data"]
                            self.focus.a_focus = True

                    elif signal["nom"] == "&ask_changement_vue&":
                        signals.clear()
                        self.changer_vue(signal["data"], ecran, dimensions)
                        break
                    else:
                        # on envoie le signal aux widgets
                        self.vue.signal_received(signal["nom"], signal["data"])

                signaux = signals.traiter_signaux()


if __name__ == '__main__':
    orchestrateur = Orchestrateur()
    curses.wrapper(orchestrateur.run) # lancement du main