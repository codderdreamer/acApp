import asyncio
import websockets
from src.chargePoint16 import ChargePoint16
from src.configModule import Config
from threading import Thread
from src.ensureFutures import EnsureFutures
from src.callbacks import OcppCallbacks
from src.enums import *
import time
from src.ev import EV
from src.serialPort import SerialPort
from src.settings import Settings
from src.databaseModule import DatabaseModule
from src.networkSettings import NetworkSettings
from src.websocketServer import WebSocketServer

class Application():
    def __init__(self,loop) -> None:
        self.loop = loop
        self.chargePoint = None
        
        self.networkSettings = NetworkSettings(self)
        self.settings = Settings()
        self.databaseModule = DatabaseModule(self)
        self.webSocketServer = WebSocketServer(self)
        self.ev = EV()
        self.config = Config()
        self.ensureFutures = EnsureFutures(self)
        self.ocppCallbacks =  OcppCallbacks(self)
        self.ocpp_subprotocols = OcppVersion.ocpp16
        self.serialPort = SerialPort(self)
        while self.config.config_writed == False:
            time.sleep(0.01)
        
    async def main(self):
        try:
            async with websockets.connect(self.config.ocpp_server_url + self.config.charge_point_id, subprotocols=[self.ocpp_subprotocols.value]) as ws:
                if self.ocpp_subprotocols == OcppVersion.ocpp16:
                    self.chargePoint = ChargePoint16(self,self.config.charge_point_id, ws)
                    future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                    await self.chargePoint.send_boot_notification(self.config.charge_point_model,self.config.charge_point_vendor)
                elif self.ocpp_subprotocols == OcppVersion.ocpp20:
                    pass
                elif self.ocpp_subprotocols == OcppVersion.ocpp21:
                    pass
        except Exception as e:
            print("main",e)

    
if __name__ == "__main__":
    try:
        ocppActive = False
        loop = asyncio.get_event_loop()
        app = Application(loop)
        if ocppActive:
            res = loop.run_until_complete(app.main())
    except Exception as e:
        print("__main__",e)
    while True:
        time.sleep(5)

# ttyS5 rfid kart için 