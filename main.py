import asyncio
import websockets
from src.chargePoint import ChargePoint
from src.configModule import Config
import time

class Application():
    def __init__(self) -> None:
        self.chargePoint = None
        self.config = Config()
        while self.config.config_writed == False:
            time.sleep(0.01)
        

    async def main(self):
        try:
            async with websockets.connect(self.config.ocpp_server_url + self.config.charge_point_id, subprotocols=["ocpp1.6"]) as ws:
                self.chargePoint = ChargePoint(self,self.config.charge_point_id, ws)
                await asyncio.gather(self.chargePoint.start(), self.chargePoint.send_boot_notification())
        except Exception as e:
            print(e)

    def run(self):
        asyncio.run(self.main())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(Application().main())
    print(res)