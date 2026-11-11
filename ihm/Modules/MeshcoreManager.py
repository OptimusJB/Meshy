from meshcore import MeshCore, EventType
from bleak import BleakScanner
import asyncio
from Modules.Log import log
import serial.tools.list_ports
import pexpect

class MeshcoreManager:
    def __init__(self):
        self.types = {0:"ble", 1:"usb"}
        self.type = 0
        self.meshcore = None
        self.nom_appareil = None
        self.pin_appareil = None

    async def se_connecter(self):
        # connexion automatique au meschore
        if self.types[self.type] == "ble":
            self.meshcore = await MeshCore.create_ble(self.nom_appareil, self.pin_appareil)
        elif self.types[self.type] == "usb":
            self.meshcore = await MeshCore.create_serial(self.nom_appareil)

    async def scan_ble(self):
        log.log("Recherche d'appareils BLE...")
        try:
            appareils = await BleakScanner.discover()
        except:
            appareils = ["Une erreur est survenue"]
            resultat = ["Une erreur est survenue"]
            adresses = []


        if appareils != ["Une erreur est survenue"]:
            resultat = []
            adresses = []
            for appareil in appareils:
                resultat.append(appareil.name)
                adresses.append(appareil.address)
            log.log(f"{len(resultat)} appareils BLE trouvés")
        return {"type":"bluetooth", "appareils":resultat, "adresses":adresses}

    async def scan_usb(self):
        log.log("Recherche d'appareils USB...")
        ports = serial.tools.list_ports.comports()
        resultat = []
        for port in ports:
            resultat.append(port.device)
        log.log(f"{len(resultat)} appareils USB trouvés")
        return {"type":"usb", "appareils":resultat, "adresses":resultat}

    async def se_connecter_usb(self, nom_appareil):
        self.meshcore = await MeshCore.create_serial(nom_appareil)
        return self.meshcore

    async def se_connecter_ble(self, nom_appareil, pin_appareil):
        await asyncio.to_thread(self.appairer_ble, nom_appareil, pin_appareil)
        try:
            self.meshcore = await MeshCore.create_ble(address=nom_appareil)
        except Exception as e:
            log.log(f"{e}")
        return self.meshcore

    def appairer_ble(self, adresse, pin):
        PROMPT = r"\[[^\]\r\n]+\][>#]"
        bt = pexpect.spawn(
            "bluetoothctl",
            encoding="utf-8",
            timeout=20
        )

        log.log("lancement de l'appairage")

        try:
            bt.expect(PROMPT)

            # Activation Bluetooth
            log.log("power on")
            bt.sendline("power on")
            bt.expect("(?i)succeeded")

            # Configuration de l'agent
            log.log("agent KeyboardDisplay")
            bt.sendline("agent KeyboardDisplay")
            bt.expect("(?i)registered")

            log.log("default-agent")
            bt.sendline("default-agent")
            bt.expect("(?i)successful")

            # Vérification de l'appairage existant
            log.log(f"info {adresse}")
            bt.sendline(f"info {adresse}")
            bt.expect("(?i)AdvertisingFlags")

            log.log("bt.before : " + str(bt.before))
            if "Paired: yes" in bt.before:
                # Appareil déjà appairé
                log.log("Appareil déjà appairé")
            else:
                # Appairage
                log.log(f"pair {adresse}")
                bt.sendline(f"pair {adresse}")

                while True:
                    resultat = bt.expect([
                        r"(?i)enter pin code",
                        r"(?i)enter passkey",
                        r"(?i)pairing successful",
                        r"(?i)failed to pair",
                    ])

                    if resultat in (0, 1):
                        # Envoi du PIN
                        log.log("Envoi du pin")
                        bt.sendline(str(pin))

                    elif resultat == 2:
                        # Appairage réussi
                        log.log("Appairage réussi")
                        break

            # Autorisation permanente
            log.log(f"trust {adresse}")
            bt.sendline(f"trust {adresse}")
            bt.expect(PROMPT)

        finally:
            log.log("Fermeture")
            bt.sendline(f"disconnect {adresse}")
            bt.expect(r"(?i)Successful")
            bt.sendline("quit")
            bt.close()


meshcore_manager = MeshcoreManager()

if __name__ == '__main__':
    # tests zone
    MeshcoreManager().appairer_ble("E7:08:A7:5D:47:28", "123456")
    #truc = asyncio.run(MeshcoreManager().scan_ble())
    #print(truc)