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
from ocpp.v16.enums import DiagnosticsStatus

import os
from threading import Thread
import time
import requests
import subprocess
import zipfile

from src.logger import ac_app_logger as logger
from src.logger import LOGGER_CHARGE_POINT, LOGGER_CENTRAL_SYSTEM


class ChargePoint16(cp):
    def __init__(self, application, id, connection, loop, response_timeout=5):
        super().__init__(id, connection, response_timeout)
        self.application = application
        self.loop = loop
        self.authorize = None
        self.logger = logger
        self.start_transaction_result = None

    def reboot(self):
        time.sleep(7)
        os.system("reboot")
        

    async def send_data(self,request):
        try:
            print("************************************************** SEND DATA ******************************************* ")
            LOGGER_CHARGE_POINT.info("\n???????????????????????????????? Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("\n????????????????????????????????Response:%s", response)
            return response
        except Exception as e:
            print("******************************************************************************************send_data Exception:",e)
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
            if self.application.ocppActive == True:
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
            else:
                self.application.request_list.append(request)
                
                if self.application.ev.card_id == self.application.process.id_tag:
                    self.authorize = AuthorizationStatus.accepted
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidVerified,), daemon= True).start()
                    if (self.application.ev.control_pilot == "A" and self.application.ev.charge == False) :
                        print("-------------------------------------------------------------------  Araç bağlı değil")
                        self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.preparing)
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.WaitingPluging,), daemon= True).start()
                    if  self.application.ev.charge:
                        self.application.deviceState = DeviceState.STOPPED_BY_USER
                else:
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
        
        except Exception as e:
            print("send_authorize Exception:",e)

    def handle_authorization_accepted(self):
        """
        Yetkilendirme kabul edildiğinde yapılacak işlemler.
        """
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidVerified,), daemon=True).start()
        if self.application.ev.control_pilot == "A" and not self.application.ev.charge:
            print("-------------------------------------------------------------------  Araç bağlı değil")
            self.application.change_status_notification(ChargePointErrorCode.no_error, ChargePointStatus.preparing)
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.WaitingPluging,), daemon=True).start()
        if self.application.ev.charge:
            self.application.deviceState = DeviceState.STOPPED_BY_USER


    def handle_authorization_failed(self):
        """
        Yetkilendirme başarısız olduğunda yapılacak işlemler.
        """
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon=True).start()
        
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

                await self.send_heartbeat()
            return response
        except Exception as e:
            print("send_boot_notification Exception:",e)

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
            print("send_data_transfer Exception:",e)

    # 4. DIAGNOSTICS STATUS NOTIFICATION
    async def send_diagnostics_status_notification(self, status: DiagnosticsStatus):
        """
        status: DiagnosticsStatus
        """
        try:
            # Diagnostics status bildirimi gönder
            request = call.DiagnosticsStatusNotificationPayload(status)
            LOGGER_CHARGE_POINT.info("Request:%s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
            return response
        except Exception as e:
            print("send_diagnostics_status_notification Exception:", e)

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
            print("send_firmware_status_notification Exception:",e)

    # 6. HEARTBEAT
    async def send_heartbeat(self):
        """
        interval: int
        """
        try :
            if self.application.databaseModule.get_charge()["charge"] == "True" and self.application.cardType == CardType.BillingCard:
                self.application.process.transaction_id = self.application.databaseModule.get_charge()["transaction_id"]
                self.application.process.id_tag = self.application.databaseModule.get_charge()["id_tag"]
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(Reason.power_loss),self.application.loop)
                time.sleep(1)
                self.application.process.transaction_id = None
                self.application.process.id_tag = None
            if self.application.cardType == CardType.BillingCard:
                for request in self.application.request_list:
                    print("Requested List")
                    print("\n\n???????????????????????????????????????????? request",request)
                    asyncio.run_coroutine_threadsafe(self.send_data(request),self.loop)
                self.application.request_list = []
                print("\n \n--------------------------------------------------run_coroutine_threadsafe finish ---------------------------\n")
                
            request = call.HeartbeatPayload()
            while self.application.cardType == CardType.BillingCard:
                if self.application.settings.change_ocpp:
                    self.application.settings.change_ocpp = False
                    break
                LOGGER_CHARGE_POINT.info("Request:%s", request)
                response = await self.call(request)
                LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
                self.application.ocppActive = True
                interval = int(self.application.settings.configuration.HeartbeatInterval)
                await asyncio.sleep(interval)

        except Exception as e:
            print("send_heartbeat Exception:",e)
            self.application.ocppActive = False

    async def send_heartbeat_once(self):
        try:
            request = call.HeartbeatPayload()
            LOGGER_CHARGE_POINT.info("Sending Heartbeat: %s", request)
            response = await self.call(request)
            LOGGER_CENTRAL_SYSTEM.info("Received Heartbeat Response: %s", response)
            return response
        except Exception as e:
            print("send_heartbeat_once Exception:", e)
            self.application.ocppActive = False    

    # 7. METER VALUES
    async def send_meter_values(self):
        try:
            # Configurations
            sampled_data = []
            measurands = self.application.settings.configuration.MeterValuesSampledData.split(",")
            print("measurands:",measurands)
            max_length = int(self.application.settings.configuration.MeterValuesSampledDataMaxLength)
            print("max_length:",max_length)
            # Map the measurand strings to actual data
            measurand_mapping = {
                "Energy.Active.Import.Register": {
                    "value": str(self.application.ev.energy),
                    "measurand": Measurand.energy_active_import_register,
                    "unit": UnitOfMeasure.kwh
                },
                "Voltage.L1": {
                    "value": str(self.application.ev.voltage_L1),
                    "measurand": Measurand.voltage,
                    "phase": Phase.l1,
                    "unit": UnitOfMeasure.v
                },
                "Voltage.L2": {
                    "value": str(self.application.ev.voltage_L2),
                    "measurand": Measurand.voltage,
                    "phase": Phase.l2,
                    "unit": UnitOfMeasure.v
                },
                "Voltage.L3": {
                    "value": str(self.application.ev.voltage_L3),
                    "measurand": Measurand.voltage,
                    "phase": Phase.l3,
                    "unit": UnitOfMeasure.v
                },
                "Current.Import.L1": {
                    "value": str(self.application.ev.current_L1),
                    "measurand": Measurand.current_import,
                    "phase": Phase.l1,
                    "unit": UnitOfMeasure.a
                },
                "Current.Import.L2": {
                    "value": str(self.application.ev.current_L2),
                    "measurand": Measurand.current_import,
                    "phase": Phase.l2,
                    "unit": UnitOfMeasure.a
                },
                "Current.Import.L3": {
                    "value": str(self.application.ev.current_L3),
                    "measurand": Measurand.current_import,
                    "phase": Phase.l3,
                    "unit": UnitOfMeasure.a
                },
                "Power.Active.Import": {
                    "value": str(self.application.ev.power),
                    "measurand": Measurand.power_active_import,
                    "unit": UnitOfMeasure.kw
                },
                "Temperature": {
                    "value": str(self.application.ev.temperature),
                    "measurand": Measurand.temperature,
                    "unit": UnitOfMeasure.celsius
                }
            }

            # Add measurands to the sampled data list according to the configuration
            for measurand in measurands:
                if measurand in measurand_mapping and len(sampled_data) < max_length:
                    sampled_data.append({
                        "value": measurand_mapping[measurand]["value"],
                        "context": ReadingContext.sample_periodic,
                        "format": ValueFormat.raw,
                        "measurand": measurand_mapping[measurand]["measurand"],
                        "phase": measurand_mapping[measurand].get("phase", None),
                        "location": Location.cable,
                        "unit": measurand_mapping[measurand]["unit"]
                    })

            # Prepare and send the MeterValues request
            request = call.MeterValuesPayload(
                connector_id=1,
                transaction_id=self.application.process.transaction_id,
                meter_value=[{
                    "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z",
                    "sampledValue": sampled_data
                }]
            )

            if self.application.ocppActive:
                LOGGER_CHARGE_POINT.info("Request: %s", request)
                response = await self.call(request)
                LOGGER_CENTRAL_SYSTEM.info("Response: %s", response)
                return response
            else:
                self.application.request_list.append(request)

        except Exception as e:
            print("send_meter_values Exception:", e)

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
            self.application.process.transaction_id = response.transaction_id
            self.start_transaction_result = response.id_tag_info['status']
            return response
        except Exception as e:
            print("send_start_transaction Exception:",e)

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
            if self.application.ocppActive == True:
                LOGGER_CHARGE_POINT.info("Request:%s", request)
                response = await self.call(request)
                LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
                return response
            else:
                self.application.request_list.append(request)
        except Exception as e:
            print("send_status_notification Exception:",e)

    # 10. STOP TTANSACTION
    async def send_stop_transaction(
                                    self, reason = None
                                    ):
        """
        meter_stop: int,
        timestamp: str,
        transaction_id: int,
        reason: Reason | None = None,
        id_tag: str | None = None,
        transaction_data: List | None = None
        """
        print("send_stop_transaction")
        meter_stop = int(self.application.ev.energy*1000)
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        transaction_id = self.application.process.transaction_id
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
            if self.application.ocppActive == True:
                LOGGER_CHARGE_POINT.info("Request:%s", request)
                response = await self.call(request)
                LOGGER_CENTRAL_SYSTEM.info("Response:%s", response)
                return response
            else:
                self.application.request_list.append(request)
        except Exception as e:
            print("send_stop_transaction Exception:",e)


    # --------------------------------------------- OPERATIONS INITIATED BY CENTRAL SYSTEM ---------------------------------------------

    # 1. CANCEL RESERVATION
    @on(Action.CancelReservation)
    def on_cancel_reservation(self,reservation_id: int):
        try :
            request = call.CancelReservationPayload(
                reservation_id
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            if reservation_id == self.application.ev.reservation_id:
                self.application.ev.reservation_id = None
                self.application.ev.reservation_id_tag = None
                self.application.ev.expiry_date = None
                if self.application.ev.control_pilot == ControlPlot.stateA.value:
                    self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
                elif self.application.ev.control_pilot == ControlPlot.stateB.value:
                    self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
            response = call_result.CancelReservationPayload(
                status = CancelReservationStatus.accepted
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print("on_cancel_reservation Exception:",e)
            

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
            print("on_change_availability Exception:",e)
            
    @after(Action.ChangeAvailability)
    def after_change_availability(self,connector_id: int, type: AvailabilityType):
        try :
            if type == AvailabilityType.operative:
                self.application.availability = AvailabilityType.operative
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
                self.application.databaseModule.set_availability(AvailabilityType.operative.value)
            elif type == AvailabilityType.inoperative:
                self.application.availability = AvailabilityType.inoperative
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.unavailable)
                self.application.databaseModule.set_availability(AvailabilityType.inoperative.value)
        except Exception as e:
            print("after_change_availability Exception:",e)

    # 3. CHANGE CONFIGRATION
    @on(Action.ChangeConfiguration)
    def on_change_configration(self,key:str,value):
        try :
            request = call.ChangeConfigurationPayload(
                key,
                value
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)

            avaibility = self.application.databaseModule.configuration_change(key, value)

            response = call_result.ChangeConfigurationPayload(
                status= avaibility
            )

            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
               
        except Exception as e:
            print("on_change_configration Exception:",e)
                  
    # 4. CLEAR CACHE
    @on(Action.ClearCache)
    def on_clear_cache(self):
        try :
            request = call.ClearCachePayload()
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            cache_status  = self.application.databaseModule.clear_auth_cache()
            response = call_result.ClearCachePayload(
                status= cache_status
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print("on_clear_cache Exception:",e)

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
            print("on_clear_charging_profile Exception:",e)

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
            print("on_data_transfer Exception:",e)

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
            print("on_get_composite_schedule Exception:",e)

    # 8. GET CONFIGRATION
    @on(Action.GetConfiguration)
    def on_get_configration(self,key:list=None):
        try :
            request = call.GetConfigurationPayload(
                key
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)

            full_configuration = self.application.databaseModule.full_configuration

            if key:
                filtered_configuration = [config for config in full_configuration if config["key"] in key]
                response_payload = call_result.GetConfigurationPayload(
                    configuration_key=filtered_configuration,
                    unknown_key=[k for k in key if k not in [conf["key"] for conf in full_configuration]]
                )
            else:
                response_payload = call_result.GetConfigurationPayload(
                    configuration_key=full_configuration,
                    unknown_key=None
                )

            LOGGER_CHARGE_POINT.info("Response:%s", response_payload)
            return response_payload
        except Exception as e:
            print("on_get_configration Exception:",e)

    # 9. GET DIAGNOSTICS
    @on(Action.GetDiagnostics)
    def on_get_diagnostics(self, location: str, retries: int = None, retry_interval: int = None, start_time: str = None, stop_time: str = None):
        try:
            # Return diagnostics payload
            request = call.GetDiagnosticsPayload(
                location=location,
                retries=retries,
                retry_interval=retry_interval,
                start_time=start_time,
                stop_time=stop_time
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            
            response = call_result.GetDiagnosticsPayload(
                file_name=None 
            )
            

            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print("on_get_diagnostics Exception:", e)

    @after(Action.GetDiagnostics)
    def after_get_diagnostics(self, location: str, retries: int = None, retry_interval: int = None, start_time: str = None, stop_time: str = None):
        try:
            diagnostics_status = self.application.databaseModule.get_diagnostics_status()
            if diagnostics_status and diagnostics_status.get('status') == DiagnosticsStatus.uploading.value:
                print("Diagnostics process is already running with status: Uploading.")
                asyncio.run_coroutine_threadsafe(
                self.send_diagnostics_status_notification(DiagnosticsStatus.uploading),
                self.application.loop
                )
                return
            # Create a new thread to run the diagnostics upload process
            Thread(target=self.run_diagnostics_thread, args=(location, retries, retry_interval, start_time, stop_time), daemon=True).start()
        except Exception as e:
            print("after_get_diagnostics Exception:", e)

    def run_diagnostics_thread(self, location: str, retries: int = None, retry_interval: int = None, start_time: str = None, stop_time: str = None):
        try:

            #set database diagnostics status to uploading
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
            self.application.databaseModule.set_diagnostics_status(DiagnosticsStatus.uploading.value, current_time)
            #send diagnostics status notification
            asyncio.run_coroutine_threadsafe(
                self.send_diagnostics_status_notification(DiagnosticsStatus.uploading),
                self.application.loop
            )

            # Diagnostic dosyalarını zip dosyasına ekleme işlemi
            log_files = [
                '/root/output.txt',
                '/tmp/acApp/logs/central_system.log',
                '/tmp/acApp/logs/charge_point.log'
            ]

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            zip_file_name = f"/root/diagnostics_{timestamp}.zip"

            with zipfile.ZipFile(zip_file_name, 'w') as diagnostics_zip:
                for log_file in log_files:
                    if os.path.exists(log_file):
                        diagnostics_zip.write(log_file, os.path.basename(log_file))

            # Diagnostic dosyasını gönderme işlemi
            with open(zip_file_name, 'rb') as file_to_upload:
                response = None
                for attempt in range(retries if retries else 1):
                    try:
                        response = requests.post(location, files={'file': file_to_upload})
                        if response.status_code == 200:
                            break
                        else:
                            print(f"Upload attempt {attempt + 1} failed with status code: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"Upload attempt {attempt + 1} failed with error: {e}")
                    time.sleep(retry_interval if retry_interval else 0)

            # Diagnostic status'u güncelleme
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
            new_status = DiagnosticsStatus.uploaded if response and response.status_code == 200 else DiagnosticsStatus.upload_failed
            self.application.databaseModule.set_diagnostics_status(new_status.value, current_time)

            # Send DiagnosticsStatusNotification with the final status
            asyncio.run_coroutine_threadsafe(
                self.send_diagnostics_status_notification(new_status),
                self.application.loop
            )

        except Exception as e:
            print("run_diagnostics_thread Exception:", e)
            current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
            self.application.databaseModule.set_diagnostics_status(DiagnosticsStatus.upload_failed.value, current_time)
            asyncio.run_coroutine_threadsafe(
                self.send_diagnostics_status_notification(DiagnosticsStatus.upload_failed),
                self.application.loop
            )
        finally:
            # Dosyayı silme işlemi
            if os.path.exists(zip_file_name):
                os.remove(zip_file_name)
                print(f"Diagnostic file {zip_file_name} has been deleted.")
    # 10. GET LOCAL LIST VERSION
    @on(Action.GetLocalListVersion)
    def on_get_local_list_version(self):
        try:
            request = call.GetLocalListVersionPayload()
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            
            # Veritabanından current local list version'ı al
            current_list_version = self.application.databaseModule.get_current_list_version()     
                   
            # Eğer current_list_version None veya -1 ise, default olarak -1 döner
            if current_list_version is None:
                current_list_version = -1
            
            response = call_result.GetLocalListVersionPayload(
                list_version=current_list_version
            )
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response

        except Exception as e:
            print("on_get_local_list_version Exception:", e)
    # 11. REMOTE START TRANSACTION
    @on(Action.RemoteStartTransaction)
    def on_remote_start_transaction(self,id_tag: str, connector_id: int = None, charging_profile:dict = None):
        try :
            request = call.RemoteStartTransactionPayload(
                id_tag,
                connector_id,
                charging_profile
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)

            if self.application.settings.configuration.AuthorizeRemoteTxRequests == "false":
                print("AuthorizeRemoteTxRequests : false, Autorize olmadan direk başlayacak.")
                self.application.ev.id_tag = id_tag
                
                # charger uygun değilse izin verme
                if self.application.availability == AvailabilityType.inoperative:
                    response = call_result.RemoteStartTransactionPayload(
                                status= RemoteStartStopStatus.rejected
                            )
                    return response
                
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
            else:
                print("AuthorizeRemoteTxRequests : true, Autorize olduktan sonra başlayacak.")
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_authorize(id_tag = value),self.application.loop)

            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print("on_remote_start_transaction Exception:",e)
            
    def remote_start_thread(self):
        # Eğer kablo bağlı değilse
        # Waiting plug led yak
        # ConnectionTimeOut saniye içinde kablo bağlanmazsa idle
        connection_timeout = int(self.application.settings.configuration.ConnectionTimeOut)
        time_start = time.time()
        if self.application.ev.control_pilot != "B":
            print("self.application.ev.control_pilot", self.application.ev.control_pilot)
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.WaitingPluging,), daemon=True).start()
            while True:
                print(f"{connection_timeout} sn içinde kablo bağlantısı bekleniyor! control pilot:", self.application.ev.control_pilot)
                if self.application.ev.control_pilot == "B" or self.application.ev.control_pilot == "C":
                    print("Kablo bağlantısı sağlandı.")
                    break
                elif time.time() - time_start > connection_timeout:
                    print(f"Kablo bağlantısı sağlanamadı {connection_timeout} saniye süre doldu!")
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon=True).start()
                    self.application.change_status_notification(ChargePointErrorCode.noError, ChargePointStatus.available)
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
            print("after_remote_start_transaction Exception:",e)
            
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
            print("on_remote_stop_transaction Exception:",e)
            
    @after(Action.RemoteStopTransaction)
    def after_remote_stop_transaction(self,transaction_id:int):
        try :
            self.application.deviceState = DeviceState.STOPPED_BY_EVSE
        except Exception as e:
            print("after_remote_stop_transaction Exception:",e)
            
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
            if self.application.ev.reservation_id == None and self.application.availability == AvailabilityType.operative and self.application.chargePointStatus == ChargePointStatus.available:
                self.application.ev.reservation_id_tag = id_tag
                self.application.ev.expiry_date = expiry_date
                self.application.ev.reservation_id = reservation_id
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.accepted
                )
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            elif self.application.ev.reservation_id == reservation_id and self.application.availability == AvailabilityType.operative:
                self.application.ev.reservation_id_tag = id_tag
                self.application.ev.expiry_date = expiry_date
                self.application.ev.reservation_id = reservation_id
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.accepted
                )
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
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
            elif self.application.chargePointStatus == ChargePointStatus.faulted:
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.faulted
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            elif self.application.chargePointStatus != ChargePointStatus.available:
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
                response = call_result.ReserveNowPayload(
                    status = ReservationStatus.rejected
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print("on_reserve_now Exception:",e)
            
    # 13. RESERVE NOW
    @after(Action.ReserveNow)
    def after_reserve_now(self,connector_id:int, expiry_date:str, id_tag: str, reservation_id: int, parent_id_tag: str = None):
        try :
            # central_system - INFO - Request:ReserveNowPayload(connector_id=1, expiry_date='2024-05-04T23:00:00.000Z', id_tag='0485A54A007480', reservation_id=7, parent_id_tag=None)
            pass
                
                
        except Exception as e:
            print("on_reserve_now Exception:",e)

    # 14. RESET
    @on(Action.Reset)
    def on_reset(self,type: ResetType):
        try :
            request = call.ResetPayload(
                type
            )
            LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)
            # Şarj Noktasında bir reservasyon yok ise ve bir şarj yok ise resetlenebilir
            
            response = call_result.ResetPayload(
                    status = ResetStatus.accepted
                )
            
            
            LOGGER_CHARGE_POINT.info("Response:%s", response)
            return response
        except Exception as e:
            print("on_reset Exception:",e)
            
    @after(Action.Reset)
    def after_reset(self,type: ResetType):
        try :
            if (self.application.cardType == CardType.BillingCard) and self.application.meter_values_on:
                print("Şarj var durduruluyor")
                self.application.deviceState = DeviceState.STOPPED_BY_EVSE
                Thread(target=self.reboot,daemon=True).start()
            else:
                Thread(target=self.reboot,daemon=True).start()
            # os.system("reboot")
        except Exception as e:
            print("after_reset Exception:",e)

    # 15. SEND LOCAL LIST
    @on(Action.SendLocalList)
    def on_send_local_list(self, list_version: int, update_type: UpdateType, local_authorization_list: list):
        try:
            # Mevcut liste sürümünü kontrol et
            current_list_version = self.application.databaseModule.get_current_list_version()

            if list_version > current_list_version:
                # Gelen isteği güncelle
                request = call.SendLocalListPayload(
                    list_version,
                    update_type,
                    local_authorization_list
                )
                LOGGER_CENTRAL_SYSTEM.info("Request:%s", request)

                # Liste sürümünü güncelle
                self.application.databaseModule.update_local_auth_list_version(list_version)

                # Yanıtı gönder
                response = call_result.SendLocalListPayload(
                    status=UpdateStatus.accepted 
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
                return response
            else:
                # Liste sürümü güncellenmemişse hata döndür
                response = call_result.SendLocalListPayload(
                    status=UpdateStatus.version_mismatch
                )
                LOGGER_CHARGE_POINT.info("Response:%s", response)
                return response

        except Exception as e:
            print("on_send_local_list Exception:", e)
            response = call_result.SendLocalListPayload(
                status=UpdateStatus.failed
            )
            return response
        
    @after(Action.SendLocalList)
    def after_send_local_list(self, list_version: int, update_type: UpdateType, local_authorization_list: list):
        try:
            if update_type == UpdateType.full:
                self.application.databaseModule.clear_local_auth_list()
                LOGGER_CHARGE_POINT.info("Full update: Cleared existing local authorization list.")

            for data in local_authorization_list:
                ocpp_tag = data["id_tag"]
                id_tag_info = data.get("id_tag_info", {})  # id_tag_info alanını alın, eğer yoksa boş bir sözlük döndür
                status = id_tag_info.get("status", "Accepted")  # Varsayılan olarak Accepted
                expiry_date = id_tag_info.get("expiry_date", None)  # expiry_date alanını alın
                parent_id_tag = id_tag_info.get("parent_id_tag", None)  # parent_id_tag alanını alın

                self.application.databaseModule.update_local_auth_list(ocpp_tag, status, expiry_date, parent_id_tag)

            LOGGER_CHARGE_POINT.info("Local authorization list updated in database.")

            conflict_detected = self.check_local_list_conflict(local_authorization_list)
            if conflict_detected:
                self.send_status_notification(
                    connector_id=0,
                    error_code=ChargePointErrorCode.local_list_conflict
                )
                LOGGER_CENTRAL_SYSTEM.warning("Local list conflict detected and reported.")

        except Exception as e:
            print("after_send_local_list Exception:", e)

    def check_local_list_conflict(self, local_list):
        """
        Yerel yetkilendirme listesi ile StartTransaction.conf'daki geçerlilik arasında bir çakışma olup olmadığını kontrol eder.
        """
        # try:
        #     settings_database = sqlite3.connect('/root/Settings.sqlite')
        #     cursor = settings_database.cursor()

        #     # Çakışma kontrolü
        #     for entry in local_list:
        #         ocpp_tag = entry.get('id_tag')
        #         parent_id_tag = entry.get('id_tag_info', {}).get('parent_id_tag')

        #         if parent_id_tag:
        #             # Eğer parent_id_tag varsa, child-parent ilişkisini kontrol edin
        #             check_query = "SELECT status FROM local_auth_list WHERE ocpp_tag = ? AND parent_id = ?"
        #             cursor.execute(check_query, (ocpp_tag, parent_id_tag))
        #             result = cursor.fetchone()

        #             if not result:
        #                 # Parent-child ilişkisinde bir tutarsızlık veya eksiklik varsa, çakışma var demektir
        #                 return True

        #     settings_database.close()
        #     return False  # Varsayılan olarak çakışma olmadığını döner

        # except sqlite3.Error as e:
        #     print(f"Error checking local list conflict: {e}")
        return False

  
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
            print("on_set_charging_profile Exception:",e)

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
            print("on_trigger_message Exception:",e)
        
    @after(Action.TriggerMessage)
    def after_trigger_message(self, requested_message, connector_id=None):
        try:
            if requested_message == MessageTrigger.boot_notification:
                asyncio.run_coroutine_threadsafe(
                    self.send_boot_notification(
                        charge_point_model="ChargePack Smart", 
                        charge_point_vendor="Hera Charge"
                    ),
                    self.application.loop
                )
            elif requested_message == MessageTrigger.status_notification:
                asyncio.run_coroutine_threadsafe(
                    self.send_status_notification(
                        connector_id=connector_id or 1,
                        error_code=ChargePointErrorCode.noError,
                        status=self.application.chargePointStatus
                    ),
                    self.application.loop
                )
            elif requested_message == MessageTrigger.heartbeat:
                asyncio.run_coroutine_threadsafe(
                    self.send_heartbeat_once(),
                    self.application.loop
                )
            elif requested_message == MessageTrigger.meter_values:
                asyncio.run_coroutine_threadsafe(
                    self.send_meter_values(),
                    self.application.loop
                )
            elif requested_message == MessageTrigger.diagnostics_status_notification:
                diagnostics_status = self.application.databaseModule.get_diagnostics_status()['status']
                print("diagnostics_status:",diagnostics_status)
                if diagnostics_status:
                    asyncio.run_coroutine_threadsafe(
                        self.send_diagnostics_status_notification(
                            DiagnosticsStatus(diagnostics_status)
                        ),
                        self.application.loop
                    )
            elif requested_message == MessageTrigger.firmware_status_notification:
                firmware_status = self.application.databaseModule.get_firmware_status()
                if firmware_status:
                    asyncio.run_coroutine_threadsafe(
                        self.send_firmware_status_notification(
                            FirmwareStatus(firmware_status['status'])
                        ),
                        self.application.loop
                    )
            else :
                print("requested_message not found")
        except Exception as e:
            print("after_trigger_message Exception:", e)
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
            print("on_unlock_connector Exception:",e)

    # 19. UPDATE FIRMWARE
    @on(Action.UpdateFirmware)
    def on_update_firmware(self, location: str, retrieve_date: str, retries: int = None, retry_interval: int = None):
        try:
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
            print("on_update_firmware Exception:", e)

    def download_firmware(self, location):
        print("Update firmware")
        # Set status to 'downloading'
        self.application.databaseModule.set_firmware_status(FirmwareStatus.downloading.value, str(datetime.now()))
        
        asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.downloading), self.application.loop)
        filename = "/root/new_firmware.zip"
        exit_status = os.system(f"curl {location} --output {filename}")
        if exit_status == 0:
            print("Dosya başarıyla indirildi.")
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall('/root')
            print("Dosya başarıyla unzip yapıldı.")
            subprocess.run(["/bin/bash", "/root/update.sh"])
            
            # Set status to 'downloaded'
            self.application.databaseModule.set_firmware_status(FirmwareStatus.downloaded.value, str(datetime.now()))
            asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.downloaded), self.application.loop)
        else:
            print("Hata: Dosya indirilirken bir sorun oluştu.")
            
            # Set status to 'download_failed'
            self.application.databaseModule.set_firmware_status(FirmwareStatus.download_failed.value, str(datetime.now()))
            asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.download_failed), self.application.loop)

    def update_firmware(self, location):
        try:
            if self.application.ev.charge == False:
                self.download_firmware(location)
            else:
                # Set status to 'downloading'
                self.application.databaseModule.set_firmware_status(FirmwareStatus.downloading.value, str(datetime.now()))
                asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.downloading), self.application.loop)
                while True:
                    print("Firmware güncelleme için bekleniyor..............................................................")
                    if self.application.ev.charge == False:
                        self.download_firmware(location)
                        return
                    else:
                        time.sleep(1)
        except Exception as e:
            print("update_firmware Exception:", e)
            
            # Set status to 'download_failed'
            self.application.databaseModule.set_firmware_status(FirmwareStatus.download_failed.value, str(datetime.now()))
            asyncio.run_coroutine_threadsafe(self.send_firmware_status_notification(FirmwareStatus.download_failed), self.application.loop)

    @after(Action.UpdateFirmware)
    async def after_update_firmware(self, location: str, retrieve_date: str, retries: int = None, retry_interval: int = None):
        try:
            Thread(target=self.update_firmware, args=(location,), daemon=True).start()
        except Exception as e:
            print("after_update_firmware Exception:", e)

