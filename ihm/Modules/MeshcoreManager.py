from meshcore import MeshCore, EventType
from bleak import BleakScanner
import asyncio

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
        appareils = await BleakScanner.discover()
        resultat = []
        for appareil in appareils:
            resultat.append(appareil.name)
        return resultat

meshcore_manager = MeshcoreManager()

if __name__ == '__main__':
    # tests zone
    truc = asyncio.run(MeshcoreManager().scan_ble())
    print(truc)