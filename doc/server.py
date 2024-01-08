import asyncio
import logging
from datetime import datetime
import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16.datatypes import IdTagInfo
from ocpp.v16.enums import *
from ocpp.v16 import call
from threading import Thread
import time

logging.basicConfig(level=logging.INFO)

class ChargePoint(cp):
    def __init__(self, id, connection, response_timeout=30):
        super().__init__(id, connection, response_timeout)
        Thread(target=self.test,daemon=True).start()

    def test(self):
        asyncio.set_event_loop(loop)
        while True:
            time.sleep(1)
            x = input()
            if x=="1":
                future = self.send_cancel_reservation()
                future.add_done_callback(self.send_cancel_reservation_callback)

    def send_cancel_reservation(self):
        return asyncio.ensure_future(self.send_cancel_reservation_func())
    
    def send_cancel_reservation_callback(self,future):
        result = future.result()
        print("result",result)

    async def send_cancel_reservation_func(self):
        try:
            request = call.CancelReservationPayload(1)
            response = await self.call(request)
            return response
        except Exception as e:
            print(e)


    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted,
        )
    
    @on(Action.Heartbeat)
    def on_heartbeat(self):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat()
        )
        
    @on(Action.StatusNotification)
    def on_status_notification(self,**kwargs):
        print(kwargs)
        return call_result.StatusNotificationPayload(
        )
    
    @on(Action.Authorize)
    def on_authorize(self,id_tag:str):
        return call_result.AuthorizePayload(
            id_tag_info={
                "status":"Accepted"
            }
        )
    
    @on(Action.MeterValues)
    def on_meter_values(self,**kwargs):
        print("on_meter_values:",kwargs)
        return call_result.MeterValuesPayload()
    
    @on(Action.StartTransaction)
    def on_start_transaction(self,**kwargs):
        print("on_start_transaction:",kwargs)
        return call_result.StartTransactionPayload(
            transaction_id=1,
            id_tag_info = {
                "status":"Accepted"
            }
        )
        
    @on(Action.StartTransaction)
    def on_stop_transaction(self,**kwargs):
        print("on_start_transaction:",kwargs)
        return call_result.StopTransactionPayload(

        )


async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)

    await cp.start()




async def main():
    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"]
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


if __name__ == "__main__":
    global loop
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(main())
    print(res)