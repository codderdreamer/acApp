import time
from src.enums import *
import asyncio
from ocpp.v16.enums import *
from threading import Thread
from datetime import datetime

class Process():
    def __init__(self,application) -> None:
        self.application = application
        self.id_tag = None
        
        
    def _lock_connector_set_control_pilot(self):
        print("************************************************ _lock_connector_set_control_pilot")
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
            time_start = time.time()
            while True:
                self.application.serialPort.get_command_pid_locker_control()
                time.sleep(0.3)
                if self.application.ev.pid_locker_control == LockerState.Lock.value:
                    self.application.serialPort.set_command_pid_cp_pwm(self.application.ev.proximity_pilot_current)
                    self.application.deviceState = DeviceState.WAITING_STATE_C
                    break
                else:
                    print("Hata Lock Connector Çalışmadı !!!")
                    pass
                if time.time() - time_start > 10:
                    self.application.deviceState = DeviceState.FAULT
                    break
        elif self.application.socketType == SocketType.TetheredType:
            self.application.serialPort.set_command_pid_cp_pwm(self.application.max_current)
            self.application.deviceState = DeviceState.WAITING_STATE_C
        
    def connected(self):
        print("****************************************************************** connected")
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Connecting,), daemon= True).start()
        if self.application.ocppActive:
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        time.sleep(1)
        if self.application.control_C_B:
            self.application.serialPort.set_command_pid_relay_control(Relay.Off)
            return
        if self.application.deviceState != DeviceState.CONNECTED:
            return
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.get_command_pid_proximity_pilot()
            time.sleep(0.5)
            if self.application.ev.proximity_pilot_current == 0:
                self.application.deviceState = DeviceState.FAULT
                return 
        if self.application.cardType == CardType.LocalPnC:
            self._lock_connector_set_control_pilot()
        elif self.application.cardType == CardType.BillingCard:
            self.application.deviceState = DeviceState.WAITING_AUTH
        elif self.application.cardType == CardType.StartStopCard:
            self.application.deviceState = DeviceState.WAITING_AUTH
            
    def waiting_auth(self):
        print("****************************************************************** waiting_auth")
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        self.application.ev.charge = False
        if self.application.cardType == CardType.BillingCard:
            if self.application.ocppActive:
                # ya rfid kart ile auth edecek yada remote start ile auth edecek..
                time_start = time.time()
                print("\nAuthorization edilmesi bekleniyor...\n")
                while True:
                    if self.application.chargePoint.id_tag:
                        self.id_tag = self.application.chargePoint.id_tag
                        self._lock_connector_set_control_pilot()
                        return
                    elif self.application.ev.card_id:
                        self.id_tag = self.application.ev.card_id
                        time_start = time.time()
                        while True:
                            if self.application.chargePoint.authorize != None:
                                break
                            if time.time() - time_start > 20:
                                print("\nAuthorization yapılmadı 20 saniye doldu !!! FAULT\n")
                                self.application.deviceState = DeviceState.FAULT
                                return
                            if self.application.deviceState != DeviceState.WAITING_AUTH:
                                return
                        if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                            self._lock_connector_set_control_pilot()
                        else:
                            print("Authorizatinon kabul edilmedi !!! FAULT")
                            self.application.deviceState = DeviceState.FAULT
                        return
                    if time.time() - time_start > 20:
                        self.application.deviceState = DeviceState.FAULT
                        return
                    if self.application.deviceState != DeviceState.WAITING_AUTH:
                        return
                    time.sleep(1)
            else:
                print("Ocpp Aktif değil Hata !!!")
                self.application.deviceState = DeviceState.FAULT
        elif self.application.cardType == CardType.StartStopCard:
            time_start = time.time()
            while True:
                print("self.application.ev.start_stop_authorize", self.application.ev.start_stop_authorize)
                if self.application.ev.start_stop_authorize:
                    self.id_tag = self.application.ev.card_id
                    self._lock_connector_set_control_pilot()
                    break
                if time.time() - time_start > 20:
                    print("20 saniye doldu")
                    self.application.deviceState = DeviceState.FAULT
                    break
                if self.application.deviceState != DeviceState.WAITING_AUTH:
                    return
                time.sleep(1)
                              
    def waiting_state_c(self):
        print("****************************************************************** waiting_state_c")
        self.application.ev.charge = False
        
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        time.sleep(1)
        
        if self.application.deviceState != DeviceState.WAITING_STATE_C:
            return
        
        time_start = time.time()
        while True:
            if self.application.ev.control_pilot == ControlPlot.stateB.value:
                if time.time() - time_start > 60*5:
                    self.application.deviceState = DeviceState.STOPPED_BY_EVSE
                    break
            elif self.application.ev.control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING
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
            
    def charging(self):
        print("****************************************************************** charging")
        self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
        self.application.ev.charge = True
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
        
        if self.application.ocppActive:
            self.application.chargePoint.start_transaction_result = None
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_start_transaction(connector_id=1,id_tag=self.id_tag,meter_start=0),self.application.loop)
            time_start = time.time()
            while True:
                if self.application.chargePoint.start_transaction_result != None:
                    break
                if time.time() - time_start > 20:
                    # print("\nStart Transaction Cevabı Gelmedi !!! FAULT\n")
                    self.application.deviceState = DeviceState.FAULT
                    return
                if self.application.deviceState != DeviceState.CHARGING:
                    return
            if self.application.chargePoint.start_transaction_result == AuthorizationStatus.accepted:
                pass
            else:
                # print("\nStart Transaction Cevabı Olumsuz !!! FAULT\n")
                self.application.deviceState = DeviceState.FAULT
                return
                
        time.sleep(1)
        
        if self.application.control_A_B_C != True:                               # Adan Cye geçen için
            # print("Adan Cye geçen için !!! CONNECTED")
            self.application.deviceState = DeviceState.CONNECTED
            return
        
        if self.application.ev.control_pilot == ControlPlot.stateC.value:
            self.application.serialPort.set_command_pid_relay_control(Relay.On)
            # time.sleep(4)
            if self.application.ocppActive:
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.charging),self.application.loop)
                time.sleep(1)
                self.application.meter_values_on = True
                Thread(target=self.meter_values_thread,daemon=True).start()
            while True:
                self.application.serialPort.get_command_pid_current()
                self.application.serialPort.get_command_pid_voltage()
                self.application.serialPort.get_command_pid_power(PowerType.kw)
                self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
                time.sleep(3)
                if self.application.deviceState != DeviceState.CHARGING:
                    break
          
    def fault(self):
        print("****************************************************************** fault")
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.faulted),self.application.loop)
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        # time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        self.application.deviceState = DeviceState.IDLE
        
    def stopped_by_evse(self):
        print("****************************************************************** stopped_by_evse")
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.finishing),self.application.loop)
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
            
    def idle(self):
        print("****************************************************************** idle")
        self.application.ev.start_stop_authorize = False
        self.application.ev.card_id = ""
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
        if self.application.ocppActive:
            if self.application.chargePoint:
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.available),self.application.loop)
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        # time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
            
    def stopped_by_user(self):
        print("****************************************************************** stopped_by_user")
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.finishing),self.application.loop)
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        # time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        
        
