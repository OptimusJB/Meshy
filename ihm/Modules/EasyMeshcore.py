from meshcore import MeshCore, EventType
import asyncio

class EasyMeshCore:
    def __init__(self):
        self.types = {0:"ble", 1:"usb"}
        self.type = 0
        self.meshcore = None

    async def se_connecter(self):
        # connexion automatique au meschore
        if self.types[self.type] == "ble":
            self.meshcore = await MeshCore.create_ble()
        elif self.types[self.type] == "usb":
            self.meshcore = await MeshCore.create_serial()