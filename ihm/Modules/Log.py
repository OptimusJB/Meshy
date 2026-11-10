class Log:
    def __init__(self):
        self.chemin_fichier = "log.txt"

    def log(self, message:str):
        fichier = open(self.chemin_fichier, "a")
        fichier.write(str(message) + "\n")
        fichier.close()

    def reset(self):
        fichier = open(self.chemin_fichier, "w")
        fichier.close()

log = Log()
log.reset()