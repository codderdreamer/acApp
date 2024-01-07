import asyncio
from src.chargePoint16 import ChargePoint16
import websockets
import time

class EnsureFutures():
    def __init__(self,application) -> None:
        self.application = application
        self.chargePoint = None
        self.on_run_charge_point()
        
    async def run_charge_point(self):
        try:
            print("******************************************* websockets.connect")
            async with websockets.connect(self.application.config.ocpp_server_url + self.application.config.charge_point_id, subprotocols=[self.application.ocpp_subprotocols.value]) as ws:
                self.chargePoint = ChargePoint16(self,self.application.config.charge_point_id, ws)
                future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.application.loop)
                await self.chargePoint.send_boot_notification(self.application.config.charge_point_model,self.application.config.charge_point_vendor)
        except Exception as e:
            print("run_charge_point",e)
        
    def on_run_charge_point(self):
        print("*******************************************ensure_future on_run_charge_point")
        asyncio.ensure_future(self.run_charge_point())

    def on_authorize(self,id_tag):
        return asyncio.ensure_future(self.application.chargePoint.send_authorize(id_tag))