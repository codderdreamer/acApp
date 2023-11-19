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

LOGGER_CHARGE_POINT = logging.getLogger('charge_point')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER_CHARGE_POINT.addHandler(handler)
LOGGER_CHARGE_POINT.setLevel(logging.INFO)

LOGGER_CENTRAL_SYSTEM = logging.getLogger('central_system')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER_CENTRAL_SYSTEM.addHandler(handler)
LOGGER_CENTRAL_SYSTEM.setLevel(logging.INFO)


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
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
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
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            if response.status == RegistrationStatus.accepted:
                print("Connected to central system.")
                await self.send_heartbeat(response.interval)
            return response
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
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
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
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
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
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
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
                LOGGER_CHARGE_POINT.info("Request:%s", request)
                response = await self.call(request)
                LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
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
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
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
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
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
                connector_id,
                error_code,
                status,
                timestamp,
                info,
                vendor_id,
                vendor_error_code
            )
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 10. STOP TTANSACTION
    async def send_stop_transaction(
                                    self,
                                    meter_stop: int,
                                    timestamp: str,
                                    transaction_id: int,
                                    reason: Reason = None,
                                    id_tag: str = None,
                                    transaction_data: list = None
                                    ):
        """
        meter_stop: int,
        timestamp: str,
        transaction_id: int,
        reason: Reason | None = None,
        id_tag: str | None = None,
        transaction_data: List | None = None
        """
        try :
            request = call.StopTransactionPayload(
                meter_stop,
                timestamp,
                transaction_id,
                reason,
                id_tag,
                transaction_data
                )
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # --------------------------------------------- OPERATIONS INITIATED BY CENTRAL SYSTEM ---------------------------------------------

    # 1. CANCEL RESERVATION
    @on(Action.CancelReservation)
    def on_cancel_reservation(self,reservation_id: int):
        try :
            request = call.CancelReservationPayload(
                reservation_id
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.CancelReservationPayload(
                status = CancelReservationStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 2. CHANGE AVAILABILITY
    @on(Action.ChangeAvailability)
    def on_change_availability(self,connector_id: int, type: AvailabilityType):
        try :
            request = call.ChangeAvailabilityPayload(
                connector_id,
                type
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.ChangeAvailabilityPayload(
                status = AvailabilityStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 3. CHANGE CONFIGRATION
    @on(Action.ChangeConfiguration)
    def on_change_configration(self,key:str,value):
        try :
            request = call.ChangeConfigurationPayload(
                key,
                value
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.ChangeAvailabilityPayload(
                status= AvailabilityStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 4. CLEAR CACHE
    @on(Action.ClearCache)
    def on_clear_cache(self):
        try :
            request = call.ClearCachePayload()
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.ClearCachePayload(
                status= ClearCacheStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 5. CLEAR CHARGING PROFILE
    @on(Action.ClearChargingProfile)
    def on_clear_charging_profile(self,id:int,connector_id:int,charging_profile_purpose:ChargingProfilePurposeType=None,stack_level:int=None):
        try :
            request = call.ClearChargingProfilePayload(
                id,
                connector_id,
                charging_profile_purpose,
                stack_level
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.ClearChargingProfilePayload(
                status=ClearChargingProfileStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 6. DATA TRANSFER
    @on(Action.DataTransfer)
    def on_data_transfer(self,vendor_id:str, message_id:str = None, data:str = None):
        try :
            request = call.DataTransferPayload(
                vendor_id,
                message_id,
                data
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.DataTransferPayload(
                status= DataTransferStatus.unknown_message_id,
                data = data
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 7. GET COMPOSITE SCHEDULE
    @on(Action.GetCompositeSchedule)
    def on_get_composite_schedule(self,connector_id: int, duration: int, charging_rate_unit: ChargingRateUnitType = None):
        try :
            request = call.GetCompositeSchedulePayload(
                connector_id,
                duration,
                charging_rate_unit
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.GetCompositeSchedulePayload(
                status= GetCompositeScheduleStatus.rejected,
                connector_id = connector_id,
                schedule_start = None,
                charging_schedule = None
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 8. GET CONFIGRATION
    @on(Action.GetConfiguration)
    def on_get_configration(self,key):
        try :
            request = call.GetConfigurationPayload(
                key
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.GetConfigurationPayload(
                configuration_key = None,
                unknown_key = None
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

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



    

    






