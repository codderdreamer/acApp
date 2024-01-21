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
from src.enums import *

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
        
        self.authorize = None
        self.transaction_id = None
        self.start_transaction_result = None
        self.id_tag = None
        

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
            self.authorize = response.id_tag_info['status']
            if self.authorize == AuthorizationStatus.accepted:
                self.application.serialPort.set_command_pid_led_control(LedState.RfidVerified)
            else:
                self.application.serialPort.set_command_pid_led_control(LedState.RfidFailed)
            return response
        except Exception as e:
            print(e)
            self.application.serialPort.set_command_pid_led_control(LedState.RfidFailed)

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
                if self.application.availability == AvailabilityType.operative:
                    await self.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.available)
                else:
                    await self.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.unavailable)
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
            while self.application.cardType == CardType.BillingCard:
                LOGGER_CHARGE_POINT.info("Request:%s", request)
                response = await self.call(request)
                LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
                await asyncio.sleep(interval)
        except Exception as e:
            print(e)

    # 7. METER VALUES
    async def send_meter_values(
                                self
                                ):
        """
        connector_id: int,
        meter_value: List = list,
        transaction_id: int | None = None
        """
        try :
            request = call.MeterValuesPayload(
                connector_id = 1,
                transaction_id = self.transaction_id,
                meter_value = [
                    {
                        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z",
                        "sampledValue": [
                            {
                                "value": str(self.application.ev.energy),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.energy_active_import_register,
                                "phase" : None,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.kwh
                            },
                            {
                                "value": str(self.application.ev.voltage_L1),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.voltage,
                                "phase" : Phase.l1,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.v
                            },
                            {
                                "value": str(self.application.ev.voltage_L2),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.voltage,
                                "phase" : Phase.l2,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.v
                            },
                            {
                                "value": str(self.application.ev.voltage_L3),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.voltage,
                                "phase" : Phase.l3,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.v
                            },
                            {
                                "value": str(self.application.ev.current_L1),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.current_export,
                                "phase" : Phase.l1,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.a
                            },
                            {
                                "value": str(self.application.ev.current_L2),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.current_export,
                                "phase" : Phase.l2,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.a
                            },
                            {
                                "value": str(self.application.ev.current_L3),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.current_export,
                                "phase" : Phase.l3,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.a
                            },
                            {
                                "value": str(self.application.ev.power),
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
                                        reservation_id: int=None
                                    ):
        """
        connector_id: int,
        id_tag: str,
        meter_start: int
        reservation_id: int | None = None
        """
        try :
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
            
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
            self.transaction_id = response.transaction_id
            self.start_transaction_result = response.id_tag_info['status']
            return response
        except Exception as e:
            print(e)

    # 9. STATUS NOTIFICATION
    async def send_status_notification(
                                        self,
                                        connector_id:int,
                                        error_code: ChargePointErrorCode,
                                        status: ChargePointStatus,
                                        info: str = None,
                                        vendor_id: str = None,
                                        vendor_error_code: str = None
                                        ):
        """
        connector_id: int,
        error_code: ChargePointErrorCode,
        status: ChargePointStatus,
        info: str | None = None,
        vendor_id: str | None = None,
        vendor_error_code: str | None = None
        """
        try :
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
            
            if self.application.availability == AvailabilityType.inoperative:
                status = ChargePointStatus.unavailable
            
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
                                    self
                                    ):
        """
        meter_stop: int,
        timestamp: str,
        transaction_id: int,
        reason: Reason | None = None,
        id_tag: str | None = None,
        transaction_data: List | None = None
        """
        meter_stop = int(self.application.ev.energy*1000)
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        transaction_id = self.transaction_id
        reason = None
        id_tag = self.application.process.id_tag
        transaction_data = None
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
            
    @after(Action.ChangeAvailability)
    def after_change_availability(self,connector_id: int, type: AvailabilityType):
        try :
            if type == AvailabilityType.operative:
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.available),self.application.loop)
            elif type == AvailabilityType.inoperative:
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.unavailable),self.application.loop)
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
    def on_get_configration(self,key:list=None):
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
    @on(Action.GetDiagnostics)
    def on_get_diagnostics(self,location:str, retries:int = None, retry_interval:int = None, start_time:str = None, stop_time:str = None):
        try :
            request = call.GetDiagnosticsPayload(
                location,
                retries,
                retry_interval,
                start_time,
                stop_time
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.GetDiagnosticsPayload(
                file_name = None
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 10. GET LOCAL LIST VERSION
    @on(Action.GetLocalListVersion)
    def on_get_local_list_version(self):
        try :
            request = call.GetLocalListVersionPayload()
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.GetLocalListVersionPayload(
                list_version=-1
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 11. REMOTE START TRANSACTION
    @on(Action.RemoteStartTransaction)
    def on_remote_start_transaction(self,id_tag: str, connector_id: int = None, charging_profile:dict = None):
        try :
            self.id_tag = id_tag
            request = call.RemoteStartTransactionPayload(
                id_tag,
                connector_id,
                charging_profile
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.RemoteStartTransactionPayload(
                status= RemoteStartStopStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)
            
    @after(Action.RemoteStartTransaction)
    def after_remote_start_transaction(self,id_tag: str, connector_id: int = None, charging_profile:dict = None):
        try :
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        except Exception as e:
            print(e)
            
            
            
    # 12. REMOTE STOP TRANSACTION
    @on(Action.RemoteStopTransaction)
    def on_remote_stop_transaction(self,transaction_id:int):
        try :
            request = call.RemoteStopTransactionPayload(
                transaction_id = transaction_id
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.RemoteStopTransactionPayload(
                status= RemoteStartStopStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)
            
    @after(Action.RemoteStopTransaction)
    def after_remote_stop_transaction(self,transaction_id:int):
        try :
            self.application.deviceState = DeviceState.STOPPED_BY_EVSE
        except Exception as e:
            print(e)
            

    # 13. RESERVE NOW
    @on(Action.ReserveNow)
    def on_reserve_now(self,connector_id:int, expiry_date:str, id_tag: str, reservation_id: int, parent_id_tag: str = None):
        try :
            request = call.ReserveNowPayload(
                connector_id,
                expiry_date,
                id_tag,
                reservation_id,
                parent_id_tag
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.ReserveNowPayload(
                status = ReservationStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 14. RESET
    @on(Action.Reset)
    def on_reset(self,type: ResetType):
        try :
            request = call.ResetPayload(
                type
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.ResetPayload(
                status = ResetStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 15. SEND LOCAL LIST
    @on(Action.SendLocalList)
    def on_send_local_list(self,list_version: int, update_type: UpdateType, local_authorization_list: list):
        try :
            request = call.SendLocalListPayload(
                list_version,
                update_type,
                local_authorization_list
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.SendLocalListPayload(
                status = UpdateStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 16. SET CHARGING PROFILE
    @on(Action.SetChargingProfile)
    def on_set_charging_profile(self,connector_id:int, cs_charging_profiles:dict):
        try :
            request = call.SetChargingProfilePayload(
                connector_id,
                cs_charging_profiles
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.SetChargingProfilePayload(
                status= ChargingProfileStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 17. TRIGGER MESSAGE
    @on(Action.TriggerMessage)
    def on_trigger_message(self,requested_message: MessageTrigger,connector_id: int = None):
        try :
            request = call.TriggerMessagePayload(
                requested_message,
                connector_id
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.TriggerMessagePayload(
                status= TriggerMessageStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)
        
    @after(Action.TriggerMessage)
    def after_trigger_message(self,requested_message,connector_id = None):
        try :
            if requested_message == MessageTrigger.bootNotification:
                pass
        except Exception as e:
            print(e)

    # 18. UNLOCK CONNECTOR 
    @on(Action.UnlockConnector)
    def on_unlock_connector(self, connector_id: int):
        try :
            request = call.UnlockConnectorPayload(
                connector_id = connector_id
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.UnlockConnectorPayload(
                status = UnlockStatus.not_supported
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)

    # 19. UPDATE FIRMWARE
    @on(Action.UpdateFirmware)
    def on_update_firmware(self,location: str,retrieve_date: str, retries: int = None, retry_interval: int = None):
        try :
            request = call.UpdateFirmwarePayload(
                location,
                retrieve_date,
                retries,
                retry_interval
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.UpdateFirmwarePayload()
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(e)



    

    






