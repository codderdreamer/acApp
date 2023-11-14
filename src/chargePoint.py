import asyncio
import logging
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16 import call_result
from ocpp.v16.enums import *
from ocpp.routing import *

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    def __init__(self, application, id, connection, response_timeout=30):
        super().__init__(id, connection, response_timeout)
        self.application = application

    async def send_heartbeat(self, interval):
        try :
            request = call.HeartbeatPayload()
            while True:
                await self.call(request)
                await asyncio.sleep(interval)
        except Exception as e:
            print(e)


    async def send_boot_notification(self):
        try:
            request = call.BootNotificationPayload(
                charge_point_model=self.application.config.charge_point_model, charge_point_vendor=self.application.config.charge_point_vendor
            )
            response = await self.call(request)
            if response.status == RegistrationStatus.accepted:
                print("Connected to central system.")
                await self.send_heartbeat(response.interval)
        except Exception as e:
            print(e)

    async def send_authorize(self,id_tag):
        try:
            request = call.AuthorizePayload(
                id_tag = id_tag,
            )
            response = await self.call(request)
            if response != None:
                if response.id_tag_info['status'] == AuthorizationStatus.accepted:
                    print("Authorized.")
                else:
                    print("UnAuthorized!")
        except Exception as e:
            print(e)






