import time
from src.enums import *
import asyncio
from ocpp.v16.enums import *
from threading import Thread
from datetime import datetime
from src.logger import ac_app_logger as logger

class Process:
    def __init__(self, application) -> None:
        self.application = application
        self.id_tag = None
        self.transaction_id = None
        logger.info("Process initialized")

    def unlock(self):
        time_start = time.time()
        while True:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
            time.sleep(0.5)
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
            time.sleep(0.3)
            self.application.serialPort.get_command_pid_locker_control()
            logger.debug("Locker control state: %s", self.application.ev.pid_locker_control)
            if self.application.ev.pid_locker_control == LockerState.Unlock.value:
                logger.info("Connector unlocked successfully")
                break
            else:
                logger.warning("Failed to unlock connector, retrying...")
                time.sleep(1)
                if time.time() - time_start > 20:
                    logger.error("Failed to unlock connector after 20 seconds")
                    break

    def unlock_connector(self):
        self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
        time.sleep(0.7)
        self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        time_start = time.time()
        while True:
            self.application.serialPort.get_command_pid_locker_control()
            time.sleep(0.3)
            if self.application.ev.pid_locker_control == LockerState.Unlock.value:
                logger.info("Connector unlocked successfully")
                return True
            else:
                logger.warning("Waiting for connector to unlock...")
                if time.time() - time_start > 2:
                    logger.error("Failed to unlock connector after 2 seconds")
                    return False

    def set_max_current(self):
        if self.application.socketType == SocketType.Type2:
            logger.debug("Proximity pilot current: %s, Max current: %s", self.application.ev.proximity_pilot_current, self.application.max_current)
            if int(self.application.max_current) > int(self.application.ev.proximity_pilot_current):
                self.application.serialPort.set_command_pid_cp_pwm(int(self.application.ev.proximity_pilot_current))
                logger.info("Set max current to proximity pilot current: %s", self.application.ev.proximity_pilot_current)
            else:
                self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
                logger.info("Set max current to max current setting: %s", self.application.max_current)
        elif self.application.socketType == SocketType.TetheredType:
            self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
            logger.info("Set max current to max current setting: %s", self.application.max_current)

    def lock_control(self):
        self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        time.sleep(0.7)
        self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
        time_start = time.time()
        while True:
            self.application.serialPort.get_command_pid_locker_control()
            time.sleep(0.3)
            if self.application.ev.pid_locker_control == LockerState.Lock.value:
                self.set_max_current()
                self.application.deviceState = DeviceState.WAITING_STATE_C
                logger.info("Connector locked successfully")
                return True
            else:
                logger.warning("Waiting for connector to lock...")
                if time.time() - time_start > 2:
                    logger.error("Failed to lock connector after 2 seconds")
                    return False

    def _lock_connector_set_control_pilot(self):
        logger.info("Setting control pilot after locking connector")
        self.application.testWebSocket.send_socket_type(self.application.socketType.value)
        if self.application.socketType == SocketType.Type2:
            result = self.lock_control()
            control_counter = 0
            if not result:
                while control_counter < 2 and not result:
                    logger.warning("Lock failed, retrying... Attempt %d", control_counter + 1)
                    result = self.lock_control()
                    control_counter += 1
                if not result:
                    logger.error("Failed to lock after multiple attempts")
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.LockerError,), daemon=True).start()
                    self.application.deviceState = DeviceState.FAULT
            self.application.testWebSocket.send_locker_state_lock(result)
        elif self.application.socketType == SocketType.TetheredType:
            self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
            self.application.deviceState = DeviceState.WAITING_STATE_C

    def connected(self):
        logger.info("Process connected")
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    logger.error("Cannot start charging! Locker Initialize Error")
                    return
                if value == PidErrorList.RcdInitializeError:
                    logger.error("Cannot start charging! Rcd Initialize Error")
                    return

        if self.application.chargingStatus == ChargePointStatus.faulted:
            return

        if self.application.control_C_B:
            self.application.change_status_notification(ChargePointErrorCode.noError, ChargePointStatus.suspended_ev)
        else:
            self.application.change_status_notification(ChargePointErrorCode.noError, ChargePointStatus.preparing)

        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.get_command_pid_proximity_pilot()
            time.sleep(0.5)
            if self.application.ev.proximity_pilot_current == 0:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
                self.application.deviceState = DeviceState.FAULT
                return

        logger.debug("Control pilot state: %s", self.application.ev.control_pilot)
        if self.application.ev.control_pilot == ControlPlot.stateC.value:
            self.application.ev.charge = False
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Connecting,), daemon= True).start()

            logger.debug("Card type: %s", self.application.cardType)
            if self.application.cardType == CardType.LocalPnC:
                self._lock_connector_set_control_pilot()
                self.application.deviceState = DeviceState.WAITING_STATE_C

            elif self.application.cardType == CardType.BillingCard:
                if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                    self._lock_connector_set_control_pilot()
                    self.application.deviceState = DeviceState.WAITING_STATE_C
                else:
                    self.application.deviceState = DeviceState.WAITING_AUTH

            elif self.application.cardType == CardType.StartStopCard:
                if self.application.ev.start_stop_authorize:
                    self._lock_connector_set_control_pilot()
                    self.application.deviceState = DeviceState.WAITING_STATE_C
                else:
                    self.application.deviceState = DeviceState.WAITING_AUTH
            return

        if self.application.control_C_B:
            logger.info("Charging stopped, control pilot changed from C to B")
            self.application.serialPort.set_command_pid_relay_control(Relay.Off)
            time_start = time.time()
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon=True).start()
            while True:
                if self.application.chargingStatus == ChargePointStatus.faulted:
                    self.application.deviceState = DeviceState.FAULT
                    break
                if self.application.ev.control_pilot == ControlPlot.stateB.value:
                    if time.time() - time_start > 60 * 5:
                        self.application.deviceState = DeviceState.STOPPED_BY_EVSE
                        break
                else:
                    break
                time.sleep(0.3)
        
        else:
            self.application.ev.charge = False
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Connecting,), daemon= True).start()
        
            if self.application.cardType == CardType.LocalPnC:
                self._lock_connector_set_control_pilot()
                self.application.deviceState = DeviceState.WAITING_STATE_C
            
            elif self.application.cardType == CardType.BillingCard:
                if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                    self._lock_connector_set_control_pilot()
                    self.application.deviceState = DeviceState.WAITING_STATE_C
                else:
                    self.application.deviceState = DeviceState.WAITING_AUTH
            
            elif self.application.cardType == CardType.StartStopCard:
                if self.application.ev.start_stop_authorize:
                    self._lock_connector_set_control_pilot()
                    self.application.deviceState = DeviceState.WAITING_STATE_C
                else:
                    self.application.deviceState = DeviceState.WAITING_AUTH
            
    def waiting_auth(self):
        logger.info("Waiting for authorization")
        self.application.ev.charge = False
        if self.application.cardType == CardType.StartStopCard:
            time_start = time.time()
            while True:
                logger.debug("Start/stop authorization status: %s", self.application.ev.start_stop_authorize)
                if self.application.ev.start_stop_authorize:
                    self.id_tag = self.application.ev.card_id
                    self._lock_connector_set_control_pilot()
                    break
                if self.application.deviceState != DeviceState.WAITING_AUTH:
                    return
                time.sleep(1)
        
        elif self.application.cardType == CardType.BillingCard and self.application.ocppActive:
                time_start = time.time()
                print("\nAuthorization edilmesi bekleniyor...\n")
                
                while True:
                    if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                        if self.application.ev.card_id != "" and self.application.ev.card_id != None:
                            self.id_tag = self.application.ev.card_id
                            self._lock_connector_set_control_pilot()
                            break
                        if self.application.ev.id_tag != None:
                            self.id_tag = self.application.ev.id_tag
                            self._lock_connector_set_control_pilot()
                            break
                    if self.application.deviceState != DeviceState.WAITING_AUTH:
                        return
                    time.sleep(1)  

    def waiting_state_c(self):
        logger.info("Waiting for state C")
        self.application.ev.charge = False
        self.application.change_status_notification(ChargePointErrorCode.noError, ChargePointStatus.preparing)
        time.sleep(1)
        
        time_start = time.time()
        while True:
            if self.application.ev.control_pilot == ControlPlot.stateB.value:
                if time.time() - time_start > 60*5:
                    self.application.deviceState = DeviceState.STOPPED_BY_EVSE
                    break
            elif self.application.ev.control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING
                break
            elif self.application.ev.control_pilot == ControlPlot.stateA.value:
                self.application.deviceState = DeviceState.IDLE
                break
            else:
                break
            if self.application.deviceState != DeviceState.WAITING_STATE_C:
                return
            time.sleep(0.3)
            
    def meter_values_thread(self):
        while self.application.meter_values_on:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_meter_values(),self.application.loop)
            time.sleep(10)
            
    def charge_while(self):
        time_start = time.time()
        self.application.databaseModule.set_charge("True", str(self.id_tag), str(self.transaction_id))
        self.application.testWebSocket.send_there_is_mid_meter(self.application.settings.deviceSettings.mid_meter)
        self.application.serialPort.get_command_pid_relay_control()
        time.sleep(1)
        logger.debug("Relay control state: %s", self.application.ev.pid_relay_control)
        self.application.testWebSocket.send_relay_control_on(self.application.ev.pid_relay_control)

        if not self.application.ev.pid_relay_control:
            logger.error("Relay is not engaged")
            self.application.deviceState = DeviceState.FAULT
            self.application.change_status_notification(ChargePointErrorCode.noError, ChargePointStatus.faulted)
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon=True).start()
            return

        while True:
            logger.info("Charging in progress...")
            self.application.change_status_notification(ChargePointErrorCode.noError, ChargePointStatus.charging)
            if self.application.deviceState != DeviceState.CHARGING:
                return
            if (self.application.settings.deviceSettings.mid_meter or self.application.settings.deviceSettings.externalMidMeter) and not self.application.modbusModule.connection:
                logger.warning("Waiting for mid meter connection...")
                if self.application.ev.control_pilot == ControlPlot.stateC.value:
                    if time.time() - time_start > 6:
                        logger.error("Failed to connect to mid meter")
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon=True).start()
                        self.application.deviceState = DeviceState.FAULT
                        self.application.testWebSocket.send_mid_meter_state(False)
                        break
                else:
                    logger.debug("Control pilot state: %s", self.application.ev.control_pilot)
                    return
            elif self.application.settings.deviceSettings.mid_meter == False and self.application.settings.deviceSettings.externalMidMeter == False:
                self.application.meter_values_on = True
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.charging)
                self.application.serialPort.get_command_pid_current()
                self.application.serialPort.get_command_pid_voltage()
                self.application.serialPort.get_command_pid_power(PowerType.kw)
                self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
            elif self.application.modbusModule.connection == True:
                logger.info("Mid meter connected: port=%s, slave_address=%s, baudrate=%s", 
            self.application.modbusModule.port, 
            self.application.modbusModule.slave_address, 
            self.application.modbusModule.baudrate)


            time.sleep(1)

    def charging(self):
        logger.info("Charging started")
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    logger.error("Cannot start charging! Locker Initialize Error")
                    return
                if value == PidErrorList.RcdInitializeError:
                    logger.error("Cannot start charging! Rcd Initialize Error")
                    return
                
        if self.application.control_A_B_C != True: # A'dan C'ye geçmiş ise
            self.application.deviceState = DeviceState.CONNECTED
            return
        if self.application.ev.card_id != "" and self.application.ev.card_id != None:
            self.id_tag = self.application.ev.card_id
        if self.application.ev.id_tag != None:
            self.id_tag = self.application.ev.id_tag
        logger.debug("Card type: %s",self.application.cardType)
        if self.application.cardType == CardType.LocalPnC:
            self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
            self.application.ev.charge = True
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
            logger.info("Charging started without authorization")
            self.application.serialPort.set_command_pid_relay_control(Relay.On)
            self.charge_while()
                
        elif self.application.cardType == CardType.BillingCard and self.application.ocppActive:
            if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                if self.application.ev.charge == False:
                    self.application.ev.charge = True
                    self.application.chargePoint.start_transaction_result = None
                    if self.application.ev.reservation_id != None:
                        logger.debug("Reservation ID: %s, Reservation ID Tag: %s", self.application.ev.reservation_id, self.application.ev.reservation_id_tag)
                        if self.application.ev.reservation_id_tag == self.id_tag or self.application.ev.reservation_id_tag == self.application.ev.card_id:    # rezerve eden kişinin id_tagimi
                            self.id_tag = self.application.ev.reservation_id_tag
                            date_object = datetime.strptime(self.application.ev.expiry_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                            timestamp = time.mktime(date_object.timetuple())
                            if timestamp - time.time() > 0:
                                logger.info("Starting charging with reservation")
                                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_start_transaction(connector_id=1,id_tag=self.id_tag,meter_start=0,reservation_id=self.application.ev.reservation_id),self.application.loop)
                                self.application.ev.reservation_id = None
                                self.application.ev.reservation_id_tag = None
                                self.application.ev.expiry_date = None
                            else:
                                logger.error("Reservation time expired")
                                self.application.ev.reservation_id = None
                                self.application.ev.reservation_id_tag = None
                                self.application.ev.expiry_date = None
                                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
                                self.application.deviceState = DeviceState.FAULT
                                return
                        else:
                            logger.error("Reservation ID tag does not match")
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon=True).start()
                            self.application.deviceState = DeviceState.FAULT
                            return
                    else:
                        asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_start_transaction(connector_id=1,id_tag=self.id_tag,meter_start=0,reservation_id=self.application.ev.reservation_id),self.application.loop)
                
                    
                    time_start = time.time()
                    while True:
                        if self.application.chargePoint.start_transaction_result != None:
                            break
                        if self.application.deviceState != DeviceState.CHARGING:
                            return
                
                
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
                logger.info("Charging authorized by OCPP")
                if self.application.chargePoint.start_transaction_result == AuthorizationStatus.accepted:
                    pass
                else:
                    logger.error("Start Transaction response rejected, entering FAULT state")
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
                    self.application.deviceState = DeviceState.FAULT
                    return
                if self.application.ev.control_pilot == ControlPlot.stateC.value:
                    self.application.serialPort.set_command_pid_relay_control(Relay.On)
                    self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.charging)
                    if self.application.settings.deviceSettings.mid_meter == False and self.application.settings.deviceSettings.externalMidMeter == False:
                        self.application.serialPort.get_command_pid_current()
                        self.application.serialPort.get_command_pid_voltage()
                        self.application.serialPort.get_command_pid_power(PowerType.kw)
                        self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
                        
                        
                    self.application.meter_values_on = True
                    Thread(target=self.meter_values_thread,daemon=True).start()
                    self.charge_while()
            else:
                logger.info("Waiting for authorization")
                self.application.deviceState = DeviceState.WAITING_AUTH
        
        elif self.application.cardType == CardType.StartStopCard:
            if self.application.ev.start_stop_authorize:
                self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                self.application.ev.charge = True
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
                logger.info("Charging authorized by RFID card")
                self.application.serialPort.set_command_pid_relay_control(Relay.On)
                time_start = time.time()
                self.charge_while()
            else:
                logger.info("Waiting for authorization")
                self.application.deviceState = DeviceState.WAITING_AUTH

    def fault(self):
        logger.error("Entering FAULT state")
        self.application.databaseModule.set_charge("False", "", "")
        self.application.ev.start_stop_authorize = False
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.faulted)
        if (self.application.cardType == CardType.BillingCard) and self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        if self.application.socketType == SocketType.Type2:
            self.unlock()
                
        while True:
            if self.application.ev.control_pilot != ControlPlot.stateA.value:
                time.sleep(1)
            else:
                break
            
    def suspended_evse(self):
        logger.warning("Entering SUSPENDED_EVSE state")
        self.application.change_status_notification(ChargePointErrorCode.noError, ChargePointStatus.suspended_evse)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        if self.application.socketType == SocketType.Type2:
            self.unlock()
             
    def stopped_by_evse(self):
        logger.info("Stopping by EVSE")
        self.application.databaseModule.set_charge("False", "", "")
        self.application.ev.start_stop_authorize = False
        if self.application.cardType == CardType.BillingCard and self.application.ocppActive:
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.finishing)
        logger.debug("Card type: %s, Meter values on: %s", self.application.cardType, self.application.meter_values_on)
        if (self.application.cardType == CardType.BillingCard) and self.application.meter_values_on:
            self.application.meter_values_on = False
            try:
                future = asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(), self.application.loop)
                result = future.result()  # Blocking call to get the result
                logger.info("Stop transaction sent successfully, result: %s", result)
            except Exception as e:
                logger.error("Error sending stop transaction: %s", e)

        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        if self.application.socketType == SocketType.Type2:
            self.unlock()
            
    def idle(self):
        logger.info("Entering IDLE state")
        self.application.databaseModule.set_charge("False","","")
        self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
        if self.application.ev.reservation_id != None:
            logger.info("Reservation exists")
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
            return
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    logger.error("Cannot start charging! Locker Initialize Error")
                    return
                if value == PidErrorList.RcdInitializeError:
                    logger.error("Cannot start charging! Rcd Initialize Error")
                    return
                
        if (self.application.cardType == CardType.BillingCard) and self.application.meter_values_on:
            self.application.meter_values_on = False
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.finishing)
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
        else:
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
                
        self.application.ev.start_stop_authorize = False
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
        
        
        
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        if self.application.socketType == SocketType.Type2:
            self.unlock()
                             
    def stopped_by_user(self):
        logger.info("Stopping by user")
        self.application.databaseModule.set_charge("False", "", "")
        self.application.ev.start_stop_authorize = False
        
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        
        if (self.application.cardType == CardType.BillingCard) and self.application.meter_values_on:
            self.application.meter_values_on = False
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.finishing)
            
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        if self.application.socketType == SocketType.Type2:
            self.unlock()
