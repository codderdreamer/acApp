from src.enums import *
from threading import Thread
import time
import asyncio
from datetime import datetime
from ocpp.v16.datatypes import *
from ocpp.v16.enums import *
import os
from src.logger import ac_app_logger as logger

class EV():
    def __init__(self, application):
        self.application = application
        
        self.__control_pilot = ControlPlot.stateA.value             # A,B,C,D,E, F 
        self.__proximity_pilot = None           # ProximityPilot  : N, E, 1, 2, 3, 6
        self.proximity_pilot_current = None
        
        self.pid_cp_pwm = None                  # float
        self.pid_relay_control = None
        self.pid_led_control = None
        self.pid_locker_control = None
        
        self.current_L1 = 0
        self.current_L2 = 0
        self.current_L3 = 0
        self.voltage_L1 = 0
        self.voltage_L2 = 0
        self.voltage_L3 = 0
        self.power = 0
        self.energy = 0
        
        self.temperature = None
        
        self.start_date = None
        
        self.__charge = False
        self.__card_id = None
        self.__id_tag = None
        
        self.reservation_id = None
        self.reservation_id_tag =  None
        self.expiry_date = None
        
        self.send_message_thread_start = False
        
        self.start_stop_authorize = False
        
        Thread(target=self.control_error_list,daemon=True).start()
        logger.debug("EV instance created and control_error_list thread started")
        
    def control_error_list(self):
        time.sleep(5)
        counter = 0
        othererror = False
        rcdTripError = False
        
        rcd_init_error = False
        locker_init_error = False
        while True:
            othererror = False
            rcdTripError = False
            rcd_init_error = False
            locker_init_error = False
            
            logger.debug("Checking error list. Charge: %s, Control Pilot: %s, Charging Status: %s", 
                         self.charge, self.control_pilot, self.application.chargingStatus)
            
            if self.application.test_led:  # test uygulması çalışıyorken ledler sürekli değiştirilmemiş olsun diye
                pass
            else:
                print("****************************************************self.charge",self.charge)
                if self.charge:
                    print("if len(self.application.serialPort.error_list) > 0:**************************************************",self.application.serialPort.error_list)
                    if len(self.application.serialPort.error_list) > 0:
                        for value in self.application.serialPort.error_list:
                            if value == PidErrorList.RcdTripError:
                                rcdTripError = True
                            else:
                                othererror = True
                                print("othererror**********************************************************")
                    print("counter********************",counter)  
                    if rcdTripError:
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RcdError,), daemon=True).start()
                        self.application.deviceState = DeviceState.FAULT
                        logger.error("RCD Trip Error detected, setting device state to FAULT")
                    elif othererror and counter != 3:
                        print("elif othererror and counter != 3:")
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon=True).start()
                        counter += 1
                        self.application.deviceState = DeviceState.SUSPENDED_EVSE
                        logger.warning("Other errors detected, waiting 30 seconds before retrying. Attempt: %s", counter)
                        time.sleep(30)
                    elif othererror and counter == 3:
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.NeedReplugging,), daemon= True).start()
                        self.application.deviceState = DeviceState.FAULT
                        logger.error("Max retries reached, setting device state to FAULT")
                    elif othererror == False:
                        if self.control_pilot == ControlPlot.stateC.value:
                            self.application.deviceState = DeviceState.CHARGING
                        elif self.control_pilot == ControlPlot.stateB.value:
                            self.application.deviceState = DeviceState.CONNECTED
                    else:
                        counter = 0
                else:
                    if len(self.application.serialPort.error_list) > 0:
                        for value in self.application.serialPort.error_list:
                            if value == PidErrorList.RcdInitializeError:
                                rcd_init_error = True
                            elif value == PidErrorList.LockerInitializeError:
                                locker_init_error = True
                            else:
                                othererror = True
                        if othererror and counter == 3 and self.control_pilot != ControlPlot.stateA.value:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.NeedReplugging,), daemon= True).start()  
                        elif othererror:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
                    # Cihazda hata yok ise;
                    else:
                        counter = 0
                        
                        if self.control_pilot == ControlPlot.stateA.value and self.application.cardType != CardType.BillingCard and self.application.chargingStatus != ChargePointStatus.preparing:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
                            if self.application.availability == AvailabilityType.operative:
                                self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.available)
                            else:
                                self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.unavailable)
                        
                        if self.control_pilot == ControlPlot.stateA.value and self.application.cardType == CardType.BillingCard and self.application.ocppActive == True and self.application.chargingStatus != ChargePointStatus.preparing:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
                            if self.application.availability == AvailabilityType.operative:
                                self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.available)
                            else:
                                self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.unavailable)
                
                if self.application.ocppActive == False and self.application.cardType == CardType.BillingCard:
                    if self.application.chargingStatus == ChargePointStatus.charging:
                        pass
                    else:
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.DeviceOffline,), daemon=True).start()
                        self.application.change_status_notification(ChargePointErrorCode.other_error, ChargePointStatus.faulted)
            
            time.sleep(0.5)
                    
        
    def send_message(self):
        self.send_message_thread_start = True
        logger.debug("Message sending thread started")
        while self.send_message_thread_start:
            try:
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_charging())
            except Exception as e:
                logger.exception("send_message Exception: %s", e)
            time.sleep(3)
        logger.debug("Message sending thread stopped")
        
    @property
    def proximity_pilot(self):
        return self.__proximity_pilot

    @proximity_pilot.setter
    def proximity_pilot(self, value):
        self.__proximity_pilot = value
        
        if self.__proximity_pilot == ProximityPilot.CableNotPlugged.value:
            self.proximity_pilot_current = 0
        elif self.__proximity_pilot == ProximityPilot.Error.value:
            self.proximity_pilot_current = 0
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger13Amper.value:
            self.proximity_pilot_current = 13
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger20Amper.value:
            self.proximity_pilot_current = 20
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger32Amper.value:
            self.proximity_pilot_current = 32
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger63Amper.value:
            self.proximity_pilot_current = 63
        logger.debug("Proximity pilot set to %s, current: %s", self.__proximity_pilot, self.proximity_pilot_current)
        
    @property
    def control_pilot(self):
        return self.__control_pilot

    @control_pilot.setter
    def control_pilot(self, value):
        if self.__control_pilot != value:
            logger.info("Control pilot state changing from %s to %s", self.__control_pilot, value)
            self.__control_pilot = value
            if self.__control_pilot == ControlPlot.stateA.value:
                self.application.deviceState = DeviceState.IDLE
            elif self.__control_pilot == ControlPlot.stateB.value:
                self.application.deviceState = DeviceState.CONNECTED
            elif self.__control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING
            elif (self.__control_pilot == ControlPlot.stateD.value) or (self.__control_pilot == ControlPlot.stateE.value) or (self.__control_pilot == ControlPlot.stateF.value):
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon=True).start()
                self.application.deviceState = DeviceState.FAULT
                logger.error("Fault state detected in control pilot: %s", self.__control_pilot)
            else:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon=True).start()
                self.application.deviceState = DeviceState.FAULT
                logger.error("Unexpected control pilot state: %s", self.__control_pilot)
                
    @property
    def charge(self):
        return self.__charge

    @charge.setter
    def charge(self, value):
        self.__charge = value
        logger.debug("Charge state set to: %s", value)
        if value:
            Thread(target=self.send_message,daemon=True).start()
        else:
            self.send_message_thread_start = False
            self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_charging())
        
        
    @property
    def card_id(self):
        return self.__card_id

    @card_id.setter
    def card_id(self, value):
        if (value != None) and (value != ""):
            if self.application.masterCard == value:
                logger.info("Master card detected, resetting settings")
                os.system("rm -r /root/Settings.sqlite")
                os.system("cp /root/DefaultSettings.sqlite /root/Settings.sqlite")
                os.system("systemctl restart acapp.service")
            elif self.application.availability == AvailabilityType.inoperative:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
            elif (self.application.cardType == CardType.BillingCard):
                if self.charge:
                    if self.application.process.id_tag == value:
                        self.application.chargePoint.authorize = None
                        asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_authorize(id_tag = value),self.application.loop)
                    else:
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
                else:
                    self.application.chargePoint.authorize = None
                    asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_authorize(id_tag=value), self.application.loop)
            elif self.application.cardType == CardType.StartStopCard:
                # Local cardlarda var mı database bak...
                finded = False
                card_id_list = self.application.databaseModule.get_local_list()
                for id in card_id_list:
                    if value == id:
                        if self.application.deviceState == DeviceState.STOPPED_BY_EVSE or self.application.deviceState == DeviceState.STOPPED_BY_USER or self.application.deviceState == DeviceState.FAULT:
                            self.start_stop_authorize = False
                        else:
                            self.start_stop_authorize = True
                        finded = True
                        
                        if self.charge and (self.application.process.id_tag == value):
                            self.application.deviceState = DeviceState.STOPPED_BY_USER
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidVerified,), daemon= True).start()
                        elif self.charge == False:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidVerified,), daemon= True).start()
                            if self.__control_pilot != "B":
                                logger.debug("Vehicle not connected")
                                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.WaitingPluging,), daemon=True).start()
                        else:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
                            
                if finded == False:
                    self.start_stop_authorize = False
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
        self.__card_id = value
        
    @property
    def id_tag(self):
        return self.__id_tag

    @id_tag.setter
    def id_tag(self, value):
        self.__id_tag = value
        logger.debug("ID tag set to: %s", value)
