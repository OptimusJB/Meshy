import curses
from Vues import Intro
from Modules.Signals import signals
from Modules import Widget

class Orchestrateur:
    def __init__(self):
        self.vue_base = "intro"
        #self.changement_vue = None  # mettre une vue pour que le changement s'opère
        self.vue = None
        self.focus = None
        self.do_draw = False

        self.vues = {"intro":Intro.Intro}

    def changer_vue(self, nom_vue:str, ecran:curses.window):
        if not (nom_vue in self.vues.keys()):
            raise ValueError(f"la vue {nom_vue} n'existe pas")

        self.vue = self.vues[nom_vue]()
        self.vue.resize(ecran)
        #self.changement_vue = None
        self.set_focus(self.vue)
        self.vue.on_ready()

    def set_focus(self, widget:Widget.Widget) -> None:
        if not isinstance(widget, Widget.Widget):
            widget = self.vue

        # on retire le a_focus de l'ancien s'il y en a un
        if isinstance(self.focus, Widget.Widget):
            self.focus.a_focus = False

        self.focus = widget
        self.focus.a_focus = True
        self.do_draw = True

    def verifier_focus(self):
        # fonction qui vérifie que le focus est bien dans l'arborescence
        # utile dans le cas où le fils puis le parent ont été supprimé dans le même évènement (avant que le ask_focus du fils soit exécuté)
        if self.focus is not None:
            if not self.focus.est_dans(self.vue):
                # on met le focus a self.vue
                self.set_focus(self.vue)

    def run(self, ecran:curses.window):
        # initialisation
        curses.curs_set(0)  # curseur caché
        ecran.timeout(50) # timeout de 50ms pour ne pas rester bloqué au getch()

        self.changer_vue(self.vue_base, ecran)

        self.do_draw = True
        while True:
            # on vérifie le focus
            self.verifier_focus()

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
                            self.set_focus(signal["data"])

                    elif signal["nom"] == "&ask_changement_vue&":
                        signals.clear()
                        self.changer_vue(signal["data"], ecran)
                        break
                    else:
                        # on envoie le signal aux widgets
                        self.vue.signal_received(signal["nom"], signal["data"])

                signaux = signals.traiter_signaux()


if __name__ == '__main__':
    orchestrateur = Orchestrateur()
    curses.wrapper(orchestrateur.run) # lancement du main