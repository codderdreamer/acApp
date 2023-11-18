import asyncio
import websockets
from src.chargePoint import ChargePoint
from src.configModule import Config
from threading import Thread
from src.ensureFutures import EnsureFutures
from src.callbacks import OcppCallbacks
import time

class Application():
    def __init__(self,loop) -> None:
        self.loop = loop
        self.chargePoint = None
        self.config = Config()
        self.ensureFutures = EnsureFutures(self)
        self.ocppCallbacks =  OcppCallbacks(self)
        while self.config.config_writed == False:
            time.sleep(0.01)
        Thread(target=self.flow_test,daemon=True).start()
        
    async def main(self):
        try:
            async with websockets.connect(self.config.ocpp_server_url + self.config.charge_point_id, subprotocols=["ocpp1.6"]) as ws:
                self.chargePoint = ChargePoint(self,self.config.charge_point_id, ws)
                future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                await self.chargePoint.send_boot_notification()
                # await asyncio.gather(self.chargePoint.start(), self.chargePoint.send_boot_notification())
        except Exception as e:
            print(e)

    def run(self):
        asyncio.run(self.main())

    def flow_test(self):
        asyncio.set_event_loop(loop)
        while True:
            x = input()
            if x == "1":
                future = self.ensureFutures.on_authorize("454353455")
                future.add_done_callback(self.on_authorize_callback)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(Application(loop).main())
    print(res)