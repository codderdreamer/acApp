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
from ocpp.v16.datatypes import *
import os
from threading import Thread
import time
import requests
import subprocess
import zipfile

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
    def __init__(self, application, id, connection, loop, response_timeout=30):
        super().__init__(id, connection, response_timeout)
        self.application = application
        
        self.loop = loop
        
        self.authorize = None
        self.transaction_id = None
        self.start_transaction_result = None
        
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
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidVerified,), daemon= True).start()
                if (self.application.ev.control_pilot == "A" and self.application.ev.charge == False) :
                    print("-------------------------------------------------------------------  Araç bağlı değil")
                    self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.preparing)
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.WaitingPluging,), daemon= True).start()
                if  self.application.ev.charge:
                    self.application.deviceState = DeviceState.STOPPED_BY_USER
            else:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
            return response
        except Exception as e:
            print(datetime.now(),"send_authorize Exception:",e)

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
                self.application.ocppActive = True
                if self.application.availability == AvailabilityType.operative:
                    self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
                else:
                    self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.unavailable)
                await self.send_heartbeat(response.interval)
            return response
        except Exception as e:
            print(datetime.now(),"send_boot_notification Exception:",e)

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
            print(datetime.now(),"send_data_transfer Exception:",e)

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
            print(datetime.now(),"send_diagnostics_status_notification Exception:",e)

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
            print(datetime.now(),"send_firmware_status_notification Exception:",e)

    # 6. HEARTBEAT
    async def send_heartbeat(self, interval):
        """
        interval: int
        """
        try :
            request = call.HeartbeatPayload()
            while self.application.cardType == CardType.BillingCard:
                if self.application.settings.change_ocpp:
                    self.application.settings.change_ocpp = False
                    break
                LOGGER_CHARGE_POINT.info("Request:%s", request)
                response = await self.call(request)
                LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
                await asyncio.sleep(interval)
        except Exception as e:
            print(datetime.now(),"send_heartbeat Exception:",e)
            self.application.ocppActive = False
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.DeviceOffline,), daemon= True).start()

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
                                "measurand": Measurand.current_import,
                                "phase" : Phase.l1,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.a
                            },
                            {
                                "value": str(self.application.ev.current_L2),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.current_import,
                                "phase" : Phase.l2,
                                "location": Location.cable,
                                "unit": UnitOfMeasure.a
                            },
                            {
                                "value": str(self.application.ev.current_L3),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.current_import,
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
                            },
                            {
                                "value": str(self.application.ev.temperature),
                                "context": ReadingContext.sample_periodic,
                                "format": ValueFormat.raw,
                                "measurand": Measurand.temperature,
                                "phase" : None,
                                "location": Location.body,
                                "unit": UnitOfMeasure.celsius
                            }
                        ]
                    }
                ])
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
        except Exception as e:
            print(datetime.now(),"send_meter_values Exception:",e)

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
            print(datetime.now(),"send_start_transaction Exception:",e)

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
            print(datetime.now(),"send_status_notification Exception:",e)

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
            print(datetime.now(),"send_stop_transaction Exception:",e)


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
            print(datetime.now(),"on_cancel_reservation Exception:",e)

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
            print(datetime.now(),"on_change_availability Exception:",e)
            
    @after(Action.ChangeAvailability)
    def after_change_availability(self,connector_id: int, type: AvailabilityType):
        try :
            if type == AvailabilityType.operative:
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
                self.application.databaseModule.set_availability(AvailabilityType.operative.value)
            elif type == AvailabilityType.inoperative:
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.unavailable)
                self.application.databaseModule.set_availability(AvailabilityType.inoperative.value)
        except Exception as e:
            print(datetime.now(),"after_change_availability Exception:",e)

    # 3. CHANGE CONFIGRATION
    @on(Action.ChangeConfiguration)
    def on_change_configration(self,key:str,value):
        try :
            request = call.ChangeConfigurationPayload(
                key,
                value
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            response = call_result.ChangeConfigurationPayload(
                status= AvailabilityStatus.rejected
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(datetime.now(),"on_change_configration Exception:",e)

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
            print(datetime.now(),"on_clear_cache Exception:",e)

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
            print(datetime.now(),"on_clear_charging_profile Exception:",e)

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
            print(datetime.now(),"on_data_transfer Exception:",e)

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
            print(datetime.now(),"on_get_composite_schedule Exception:",e)

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
            print(datetime.now(),"on_get_configration Exception:",e)

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
            print(datetime.now(),"on_get_diagnostics Exception:",e)

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
            print(datetime.now(),"on_get_local_list_version Exception:",e)

    # 11. REMOTE START TRANSACTION
    @on(Action.RemoteStartTransaction)
    def on_remote_start_transaction(self,id_tag: str, connector_id: int = None, charging_profile:dict = None):
        try :
            request = call.RemoteStartTransactionPayload(
                id_tag,
                connector_id,
                charging_profile
            )
            self.application.ev.id_tag = id_tag
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            
            # “Locker Initialize Error”  ve   “Rcd Initialize Error” hataları varsa şarja izin verme
            error = False
            if len(self.application.serialPort.error_list) > 0:
                for value in self.application.serialPort.error_list:
                    if value == PidErrorList.LockerInitializeError:
                        print("Şarja başlanamaz! PidErrorList.LockerInitializeError")
                        response = call_result.RemoteStartTransactionPayload(
                            status= RemoteStartStopStatus.rejected
                        )
                        error = True
                    if value == PidErrorList.RcdInitializeError:
                        print("Şarja başlanamaz! PidErrorList.RcdInitializeError")
                        response = call_result.RemoteStartTransactionPayload(
                            status= RemoteStartStopStatus.rejected
                        )
                        error = True
                        
            if error == False:
                response = call_result.RemoteStartTransactionPayload(
                            status= RemoteStartStopStatus.accepted
                )
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
                self.application.chargePoint.authorize = AuthorizationStatus.accepted
                Thread(target=self.remote_start_thread,daemon=True).start()
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(datetime.now(),"on_remote_start_transaction Exception:",e)
            
    def remote_start_thread(self):
        # Eğer kablo bağlı değilse
        # Waiting plug led yak
        # 30 saniye içinde kablo bağlanmazsa idle
        print("remote_start_thread")
        time_start = time.time()
        if self.application.ev.control_pilot != "B":
            print("self.application.ev.control_pilot",self.application.ev.control_pilot)
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.WaitingPluging,), daemon= True).start()
            while True:
                print("30 sn içinde kablo bağlantısı bekleniyor ! control pilot:",self.application.ev.control_pilot)
                if self.application.ev.control_pilot == "B":
                    print("Kablo bağlantısı sağlandı.")
                    break
                elif time.time() - time_start > 30:
                    print("Kablo bağlantısı sağlanamadı 30 saniye süre doldu!")
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
                    self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
                    self.application.ev.start_stop_authorize = False
                    self.application.chargePoint.authorize = None
                    self.application.ev.card_id = ""
                    self.application.ev.id_tag = None
                    self.application.ev.charge = False
                    break
                time.sleep(0.2)
                
    @after(Action.RemoteStartTransaction)
    def after_remote_start_transaction(self,id_tag: str, connector_id: int = None, charging_profile:dict = None):
        try :
            pass
        except Exception as e:
            print(datetime.now(),"after_remote_start_transaction Exception:",e)
            
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
            print(datetime.now(),"on_remote_stop_transaction Exception:",e)
            
    @after(Action.RemoteStopTransaction)
    def after_remote_stop_transaction(self,transaction_id:int):
        try :
            self.application.deviceState = DeviceState.STOPPED_BY_EVSE
        except Exception as e:
            print(datetime.now(),"after_remote_stop_transaction Exception:",e)
            

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
            if self.application.ev.reservation_id == None and self.application.availability == AvailabilityType.operative and self.application.chargingStatus == ChargePointStatus.available:
                self.application.ev.id_tag = id_tag
                self.application.ev.expiry_date = expiry_date
                self.application.ev.reservation_id = reservation_id
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.accepted
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            # Şarj Noktası rezervasyon kimliği ile eşleşiyorsa talepteki yeni rezervasyonla değiştirecektir.
            elif self.application.ev.reservation_id == reservation_id and self.application.availability == AvailabilityType.operative:
                self.application.ev.id_tag = id_tag
                self.application.ev.expiry_date = expiry_date
                self.application.ev.reservation_id = reservation_id
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.accepted
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            elif self.application.ev.reservation_id != None and self.application.availability == AvailabilityType.operative:
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.occupied
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            elif self.application.availability == AvailabilityType.inoperative:
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.rejected
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            elif self.application.chargingStatus == ChargePointStatus.faulted:
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.faulted
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            elif self.application.chargingStatus != ChargePointStatus.available:
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.rejected
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(datetime.now(),"on_reserve_now Exception:",e)

    # 14. RESET
    @on(Action.Reset)
    def on_reset(self,type: ResetType):
        try :
            request = call.ResetPayload(
                type
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            # Şarj Noktasında bir reservasyon yok ise ve bir şarj yok ise resetlenebilir
            if self.application.ev.charge == False or self.application.ev.reservation_id == None:
                response = call_result.ResetPayload(
                    status = ResetStatus.accepted
                )
            else:
                response = call_result.ResetPayload(
                    status = ResetStatus.rejected
                )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(datetime.now(),"on_reset Exception:",e)
            
    @after(Action.Reset)
    def after_reset(self,type: ResetType):
        try :
            if self.application.ev.charge == False or self.application.ev.reservation_id == None:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.NeedReplugging,), daemon= True).start()
                os.system("reboot")
        except Exception as e:
            print(datetime.now(),"after_reset Exception:",e)

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
            print(datetime.now(),"on_send_local_list Exception:",e)
            
    @after(Action.SendLocalList)
    def after_send_local_list(self,list_version: int, update_type: UpdateType, local_authorization_list: list):
        try :
            localList = []
            # print(f"SendLocalList: list_version {list_version} update_type {update_type} local_authorization_list {local_authorization_list}")
            for data in local_authorization_list:
                localList.append(data["id_tag"])
            # print("\n\n", localList, "\n\n")
            self.application.databaseModule.set_local_list(localList)
            self.application.databaseModule.get_local_list()
        except Exception as e:
            print(datetime.now(),"after_send_local_list Exception:",e)

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
            print(datetime.now(),"on_set_charging_profile Exception:",e)

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
            print(datetime.now(),"on_trigger_message Exception:",e)
        
    @after(Action.TriggerMessage)
    def after_trigger_message(self,requested_message,connector_id = None):
        try :
            if requested_message == MessageTrigger.bootNotification:
                pass
        except Exception as e:
            print(datetime.now(),"after_trigger_message Exception:",e)

    # 18. UNLOCK CONNECTOR 
    @on(Action.UnlockConnector)
    def on_unlock_connector(self, connector_id: int):
        try :
            request = call.UnlockConnectorPayload(
                connector_id = connector_id
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            if self.application.ev.charge:
                self.application.deviceState = DeviceState.STOPPED_BY_USER
                response = call_result.UnlockConnectorPayload(
                    status = UnlockStatus.unlocked
                )
            else:
                if self.application.process.unlock_connector():
                    response = call_result.UnlockConnectorPayload(
                        status = UnlockStatus.unlocked
                    )
                else:
                    response = call_result.UnlockConnectorPayload(
                        status = UnlockStatus.unlock_failed
                    )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print(datetime.now(),"on_unlock_connector Exception:",e)

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
            print(datetime.now(),"on_update_firmware Exception:",e)
            
    def download_firmware(self,location):
        print("Update firmware")
        asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.downloading),self.application.loop)
        # await self.send_firmware_status_notification(FirmwareStatus.downloading)
        filename = "/root/new_firmware.zip"
        exit_status = os.system(f"curl {location} --output {filename}")
        if exit_status == 0:
            print("Dosya başarıyla indirildi.")
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                # password = b'sifreniz' 
                # zip_ref.setpassword(password)
                zip_ref.extractall('/root')
            print("Dosya başarıyla unzip yapıldı.")
            subprocess.run(["/bin/bash", "/root/update.sh"])
            asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.downloaded),self.application.loop)
            # await self.send_firmware_status_notification(FirmwareStatus.downloaded)
        else:
            print("Hata: Dosya indirilirken bir sorun oluştu.")
            asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.download_failed),self.application.loop)
            # await self.send_firmware_status_notification(FirmwareStatus.download_failed)
            
    def update_firmware(self,location):
        try :
            if self.application.ev.charge == False:
                self.download_firmware(location)
            else:
                asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.downloading),self.application.loop)
                # await self.send_firmware_status_notification(FirmwareStatus.downloading)
                while True:
                    print("Firmware güncelleme için bekleniyor..............................................................")
                    if self.application.ev.charge == False:
                        self.download_firmware(location)
                        return
                    else:
                        time.sleep(1)
        except Exception as e:
            print(datetime.now(),"update_firmware Exception:",e)
            asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.download_failed),self.application.loop)
            # await self.send_firmware_status_notification(FirmwareStatus.download_failed)
            
    @after(Action.UpdateFirmware)
    async def after_update_firmware(self,location: str,retrieve_date: str, retries: int = None, retry_interval: int = None):
        try :
            Thread(target=self.update_firmware,args=(location,),daemon=True).start()
        except Exception as e:
            print(datetime.now(),"after_update_firmware Exception:",e)
        



    

    










# Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.NeedReplugging,), daemon= True).start()
# await self.send_firmware_status_notification(FirmwareStatus.downloading)
# result = subprocess.run(["git", "pull"], cwd="/root/acApp", stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

# if result.returncode == 0:
#     print("git pull başarıyla tamamlandı.")
#     print("Çıktı:", result.stdout)
#     await self.send_firmware_status_notification(FirmwareStatus.downloaded)
#     time.sleep(0.5)
#     os.system("reboot")
# else:
#     print("git pull başarısız oldu.")
#     print("Hata:", result.stderr)
#     await self.send_firmware_status_notification(FirmwareStatus.downloadFailed)
#     Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
#     time.sleep(1)
#     Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
    
# print("Update firmware")





