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
                    print("Lock connector bekleniyor...")
                    pass
                if time.time() - time_start > 10:
                    self.application.deviceState = DeviceState.FAULT
                    break
        elif self.application.socketType == SocketType.TetheredType:
            self.application.serialPort.set_command_pid_cp_pwm(self.application.max_current)
            self.application.deviceState = DeviceState.WAITING_STATE_C
        
    def connected(self):
        print("****************************************************************** connected")
        
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.get_command_pid_proximity_pilot()
            time.sleep(0.5)
            if self.application.ev.proximity_pilot_current == 0:
                self.application.deviceState = DeviceState.FAULT
                return 
            
        if self.application.control_C_B:
            print("Şarj C'den B'ye döndü Röle kapatıldı")
            self.application.serialPort.set_command_pid_relay_control(Relay.Off)
            time_start = time.time()
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
            while True:
                if self.application.ev.control_pilot == ControlPlot.stateB.value:
                    if time.time() - time_start > 60*5:
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
                    self.application.deviceState = DeviceState.WAITING_STATE_C
                else:
                    self.application.deviceState = DeviceState.WAITING_AUTH
            
    def waiting_auth(self):
        print("****************************************************************** waiting_auth")
        self.application.ev.charge = False
        if self.application.cardType == CardType.StartStopCard:
            time_start = time.time()
            while True:
                print("self.application.ev.start_stop_authorize", self.application.ev.start_stop_authorize)
                if self.application.ev.start_stop_authorize:
                    self.id_tag = self.application.ev.card_id
                    self._lock_connector_set_control_pilot()
                    break
                if self.application.deviceState != DeviceState.WAITING_AUTH:
                    return
                time.sleep(1)
        
        elif self.application.cardType == CardType.BillingCard:
            if self.application.ocppActive:
                time_start = time.time()
                print("\nAuthorization edilmesi bekleniyor...\n")
                
                while True:
                    if self.application.chargePoint.authorize != None:
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
            
            else:
                print("Ocpp Aktif değil Hata !!!")
                self.application.deviceState = DeviceState.FAULT
        

    def waiting_state_c(self):
        print("****************************************************************** waiting_state_c")
        
        self.application.ev.charge = False
        
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
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
        
        if self.application.ev.card_id != "" and self.application.ev.card_id != None:
            self.id_tag = self.application.ev.card_id
        if self.application.ev.id_tag != None:
            self.id_tag = self.application.ev.id_tag
        
        if self.application.cardType == CardType.LocalPnC:
            self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
            self.application.ev.charge = True
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
            print("Authorize edilmesine gerek yok şarj başlangıcı...")
            self.application.serialPort.set_command_pid_relay_control(Relay.On)
            while True:
                self.application.serialPort.get_command_pid_current()
                self.application.serialPort.get_command_pid_voltage()
                self.application.serialPort.get_command_pid_power(PowerType.kw)
                self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
                time.sleep(3)
                if self.application.deviceState != DeviceState.CHARGING:
                    break
            
        elif self.application.cardType == CardType.BillingCard:
            if self.application.ocppActive:
                
                if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                    self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                    self.application.ev.charge = True
                    
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
                    print("ocpp ile authorize edilmiş. ")
                    
                    
                    self.application.chargePoint.start_transaction_result = None
                    asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_start_transaction(connector_id=1,id_tag=self.id_tag,meter_start=0),self.application.loop)
                    time_start = time.time()
                    while True:
                        if self.application.chargePoint.start_transaction_result != None:
                            break
                        if self.application.deviceState != DeviceState.CHARGING:
                            return
                    if self.application.chargePoint.start_transaction_result == AuthorizationStatus.accepted:
                        pass
                    else:
                        # print("\nStart Transaction Cevabı Olumsuz !!! FAULT\n")
                        self.application.deviceState = DeviceState.FAULT
                        return
                    
                    if self.application.ev.control_pilot == ControlPlot.stateC.value:
                        self.application.serialPort.set_command_pid_relay_control(Relay.On)
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
            else:
                # Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
                print("authorize edilmemiş authorize edilmesi beklenecek...")
                self.application.deviceState = DeviceState.WAITING_AUTH
        
        elif self.application.cardType == CardType.StartStopCard:
            if self.application.ev.start_stop_authorize:
                self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                self.application.ev.charge = True
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
                print("rfid kart ile authorize edilmiş.")
                self.application.serialPort.set_command_pid_relay_control(Relay.On)
                while True:
                    self.application.serialPort.get_command_pid_current()
                    self.application.serialPort.get_command_pid_voltage()
                    self.application.serialPort.get_command_pid_power(PowerType.kw)
                    self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
                    time.sleep(3)
                    if self.application.deviceState != DeviceState.CHARGING:
                        break
            else:
                # Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
                print("authorize edilmemiş authorize edilmesi beklenecek...")
                self.application.deviceState = DeviceState.WAITING_AUTH
          
    def fault(self):
        print("****************************************************************** fault")
        self.application.ev.start_stop_authorize = False
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.faulted),self.application.loop)
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        # time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
            
        while True:
            if self.application.ev.control_pilot == ControlPlot.stateA.value:
                self.application.deviceState = DeviceState.IDLE
                break
            elif self.application.ev.control_pilot == ControlPlot.stateB.value:
                self.application.deviceState = DeviceState.CONNECTED
                break
            elif self.application.ev.control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING
                break
            else:
                print("fault !!!")
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
            time.sleep(1)
        
    def stopped_by_evse(self):
        print("****************************************************************** stopped_by_evse")
        self.application.ev.start_stop_authorize = False
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        if self.application.ocppActive:
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.finishing),self.application.loop)
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
            
    def idle(self):
        print("****************************************************************** idle")
        self.application.ev.start_stop_authorize = False
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
        if self.application.ocppActive:
            if self.application.chargePoint:
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.available),self.application.loop)
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        # time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        if self.application.ocppActive:
            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.available),self.application.loop)
            
    def stopped_by_user(self):
        self.application.ev.start_stop_authorize = False
        print("****************************************************************** stopped_by_user",self.application.ev.start_stop_authorize)
        
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        if self.application.ocppActive:
            if self.application.meter_values_on:
                self.application.meter_values_on = False
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.finishing),self.application.loop)
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=ChargePointErrorCode.noError,status=ChargePointStatus.preparing),self.application.loop)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        # time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        
        
