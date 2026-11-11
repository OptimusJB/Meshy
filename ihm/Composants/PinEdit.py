import curses
from Modules import Widget
from Modules.LineEdit import LineEdit
from Modules.Log import log
from Modules.Signals import signals
import curses.ascii

CENTER = -1

class PinEdit(LineEdit):
    def __init__(self):
        super().__init__()

    def input_custom(self, touche:int) -> bool:
        if super().input_custom(touche):
            return True

        #log.log("touche : " + str(touche))
        if touche == curses.ascii.ESC: # note : esc prend du temps à cause de curses (peut être résolu avec set_escdelay() askip)
            # on enlève le popup pin
            self.parent.parent.remove_child(self.parent)
            signals.add_signal("pin popup deleted")

        elif touche == ord("\n"):   # KEY_ENTER ne fonctionne pas
            log.log("trigger entrée")
            # validation
            self.parent.parent.remove_child(self.parent)
            signals.add_signal("pin popup deleted")
            signals.add_signal("pin choisi", {"pin":self.contenu, "appareil":self.parent.selected})
        return True