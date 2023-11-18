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

    # --------------------------------------------- OPERATIONS INITIATED BY CHARGE POINT ---------------------------------------------

    # 1. AUTHORIZE
    async def send_authorize(
                                self,id_tag:str
                            ):
        """
        id_tag: str
        """
        try:
            request = call.AuthorizePayload(
                id_tag = id_tag,
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 2. BOOT NOTIFICATION
    async def send_boot_notification(
                                        self,charge_point_model:str, 
                                        charge_point_vendor:str, 
                                        charge_box_serial_number:str=None,
                                        charge_point_serial_number:str=None,
                                        firmware_version:str=None,
                                        iccid:str=None,
                                        imsi:str=None,
                                        meter_serial_number:str=None,
                                        meter_type:str=None
                                        ):
        """
        charge_point_model: str,
        charge_point_vendor: str,
        charge_box_serial_number: str | None = None,
        charge_point_serial_number: str | None = None,
        firmware_version: str | None = None,
        iccid: str | None = None,
        imsi: str | None = None,
        meter_serial_number: str | None = None,
        meter_type: str | None = None
        """
        try:
            request = call.BootNotificationPayload(
                charge_point_model,charge_point_vendor,charge_box_serial_number,charge_point_serial_number,firmware_version,iccid,imsi,meter_serial_number,meter_type
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 3. DATA TRANSFER
    async def send_data_transfer(self,vendor_id:str,message_id:str=None,data:str=None):
        """
        vendor_id: str,
        message_id: str | None = None,
        data: str | None = None
        """
        try:
            request = call.DataTransferPayload(
                vendor_id,message_id,data
            )

        except Exception as e:
            print(e)


    # 4. DIAGNOSTICS STATUS NOTIFICATION

    # 5. FIRMWARE STATUS NOTIFICATION

    # 6. HEARTBEAT
    async def send_heartbeat(self, interval):
        try :
            request = call.HeartbeatPayload()
            while True:
                await self.call(request)
                await asyncio.sleep(interval)
        except Exception as e:
            print(e)

    # 7.METER VALUES

    # 8. START TRANSACTION

    # 9. STATUS NOTIFICATION

    # 10. STOP TTANSACTION





    # --------------------------------------------- OPERATIONS INITIATED BY CENTRAL SYSTEM ---------------------------------------------

    # 1. CANCEL RESERVATION

    # 2. CHANGE AVAILABILITY

    # 3. CHANGE CONFIGRATION

    # 4. CLEAR CACHE

    # 5. CLEAR CHARGING PROFILE

    # 6. DATA TRANSFER

    # 7. GET COMPOSITE SCHEDULE

    # 8. GET CONFIGRATION

    # 9. GET DIAGNOSTICS

    # 10. GET LOCAL LIST VERSION

    # 11. REMOTE START TRANSACTION

    # 12. REMOTE STOP TRANSACTION

    # 13. RESERVE NOW

    # 14. RESET

    # 15. SEND LOCAL LIST

    # 16. SET CHARGING PROFILE

    # 17. TRIGGER MESSAGE

    # 18. UNLOCK CONNECTOR 

    # 19. UPDATE FIRMWARE



    

    






