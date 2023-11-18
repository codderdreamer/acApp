"""
    OCPP 1.6
"""

import asyncio
import logging
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16 import call_result
from ocpp.v16.enums import *
from ocpp.routing import *
from datetime import datetime

logging.basicConfig(level=logging.INFO)


class ChargePoint16(cp):
    def __init__(self, application, id, connection, response_timeout=30):
        super().__init__(id, connection, response_timeout)
        self.application = application

    # --------------------------------------------- OPERATIONS INITIATED BY CHARGE POINT ---------------------------------------------

    # 1. AUTHORIZE
    async def send_authorize(
                                self,
                                id_tag:str
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
                                        self,
                                        charge_point_model:str, 
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
                charge_point_model,
                charge_point_vendor,
                charge_box_serial_number,
                charge_point_serial_number,
                firmware_version,
                iccid,
                imsi,
                meter_serial_number,
                meter_type
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 3. DATA TRANSFER
    async def send_data_transfer(
                                    self,
                                    vendor_id:str,
                                    message_id:str=None,
                                    data:str=None
                                ):
        """
        vendor_id: str,
        message_id: str | None = None,
        data: str | None = None
        """
        try:
            request = call.DataTransferPayload(
                vendor_id,
                message_id,
                data
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 4. DIAGNOSTICS STATUS NOTIFICATION
    async def send_diagnostics_status_notification(
                                                    self,
                                                    status : DiagnosticsStatus
                                                    ):
        """
        status: DiagnosticsStatus
        """
        try:
            request = call.DiagnosticsStatusNotificationPayload(
                status
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 5. FIRMWARE STATUS NOTIFICATION
    async def send_firmware_status_notification(
                                                self,
                                                status : FirmwareStatus
                                                ):
        """
        status: FirmwareStatus
        """
        try:
            request = call.FirmwareStatusNotificationPayload(
                status
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 6. HEARTBEAT
    async def send_heartbeat(self, interval):
        """
        interval: int
        """
        try :
            request = call.HeartbeatPayload()
            while True:
                await self.call(request)
                await asyncio.sleep(interval)
        except Exception as e:
            print(e)

    # 7. METER VALUES
    async def send_meter_values(
                                self,
                                connector_id:int,
                                output_energy_on_cable:float,
                                state_of_charge:int,
                                demandchargeVoltage:float,
                                demandchargeCurrent:float,
                                moduleOutputCurrent:float,
                                moduleOutputPower:float,
                                transaction_id:int=None
                                ):
        """
        connector_id: int,
        meter_value: List = list,
        transaction_id: int | None = None
        """
        try :
            request = call.MeterValuesPayload(
                connector_id = connector_id,
                transaction_id = transaction_id,
                meter_value = [
                    {
                        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z",
                        "sampledValue": [
                            {
                                "value": str(output_energy_on_cable),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.energy_active_import_register,
                                "phase" : None,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.kwh
                            },
                            {
                                "value": str(state_of_charge),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.soc,
                                "phase" : None,
                                "location": Location.ev,
                                "unit": UnitOfMeasure.percent
                            },
                            {
                                "value": str(demandchargeVoltage),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.voltage,
                                "phase" : None,
                                "location": Location.ev,
                                "unit": UnitOfMeasure.v
                            },
                            {
                                "value": str(demandchargeCurrent),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.current_export,
                                "phase" : None,
                                "location": Location.ev,
                                "unit": UnitOfMeasure.a
                            },
                            {
                                "value": str(moduleOutputCurrent),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.current_import,
                                "phase" : None,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.a
                            },
                            {
                                "value": str(moduleOutputPower),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.power_active_import,
                                "phase" : None,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.kw
                            }
                        ]
                    }
                ]
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 8. START TRANSACTION
    async def send_start_transaction(
                                        self,
                                        connector_id:int,
                                        id_tag:str,
                                        meter_start:int,
                                        timestamp: str,
                                        reservation_id: int=None
                                    ):
        """
        connector_id: int,
        id_tag: str,
        meter_start: int,
        timestamp: str,
        reservation_id: int | None = None
        """
        try :
            request = call.StartTransactionPayload(
                connector_id,
                id_tag,
                meter_start,
                timestamp,
                reservation_id
            )
            response = await self.call(request)
        except Exception as e:
            print(e)

    # 9. STATUS NOTIFICATION
    async def send_status_notification(
                                        self,
                                        connector_id:int,
                                        error_code: ChargePointErrorCode,
                                        status: ChargePointStatus,
                                        timestamp: str = None,
                                        info: str = None,
                                        vendor_id: str = None,
                                        vendor_error_code: str = None

                                        ):
        """
        connector_id: int,
        error_code: ChargePointErrorCode,
        status: ChargePointStatus,
        timestamp: str | None = None,
        info: str | None = None,
        vendor_id: str | None = None,
        vendor_error_code: str | None = None
        """
        try :
            request = call.StatusNotificationPayload(

            )

        except Exception as e:
            print(e)

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



    

    






