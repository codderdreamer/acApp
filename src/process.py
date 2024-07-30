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
        self.transaction_id = None
        
    def unlock(self):
        time_start = time.time()
        while True:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
            time.sleep(0.5)
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
            time.sleep(0.3)
            self.application.serialPort.get_command_pid_locker_control()
            print("---------------------self.application.ev.pid_locker_control",self.application.ev.pid_locker_control)
            if self.application.ev.pid_locker_control == LockerState.Unlock.value:
                print(" ------------------------------------------------------------------- Unlock")
                break
            else:
                print("pid_locker_control Unlock Olamadı! Tekrar deneniyor...")
                time.sleep(1)
                if time.time() - time_start > 20:
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
                return True
            else:
                print("Lock connector bekleniyor...")
                if time.time() - time_start > 2:
                    print("Lock 2 saniyeyi geçti...")
                    return False
        
    def set_max_current(self):
        if self.application.socketType == SocketType.Type2:
            print("self.application.ev.proximity_pilot",self.application.ev.proximity_pilot_current)
            print("self.application.max_current",self.application.ev.proximity_pilot_current)
            if int(self.application.max_current) > int(self.application.ev.proximity_pilot_current):
                print("set_command_pid_cp_pwm",self.application.ev.proximity_pilot_current)
                self.application.serialPort.set_command_pid_cp_pwm(int(self.application.ev.proximity_pilot_current))
            else:
                print("set_command_pid_cp_pwm",self.application.max_current)
                self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
        elif self.application.socketType == SocketType.TetheredType:
            self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
    
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
                return True
            else:
                print("Lock connector bekleniyor...")
                if time.time() - time_start > 2:
                    print("Lock 2 saniyeyi geçti...")
                    return False
        
    def _lock_connector_set_control_pilot(self):
        print("************************************************ _lock_connector_set_control_pilot")
        self.application.testWebSocket.send_socket_type(self.application.socketType.value)
        if self.application.socketType == SocketType.Type2:
                result = self.lock_control()
                control_counter = 0
                if result == False:
                    while control_counter < 2 and result == False:
                        print(f"Lock Hatalı Tekrar Deneniyor {control_counter}...")
                        result = self.lock_control()
                        control_counter += 1
                    if result == False:
                        print("Deneme bitti Lock Çalışmadı.")
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.LockerError,), daemon= True).start()
                        self.application.deviceState = DeviceState.FAULT
                self.application.testWebSocket.send_locker_state_lock(result)
        elif self.application.socketType == SocketType.TetheredType:
            self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
            self.application.deviceState = DeviceState.WAITING_STATE_C
        
    def connected(self):
        print("****************************************************************** connected")
        # print("istasyon durumu:",self.application.chargingStatus)
        # “Locker Initialize Error”  ve   “Rcd Initialize Error” hataları varsa şarja izin verme
        # self.application.testWebSocket.send_socket_connected()

        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    print("Şarja başlanamaz! PidErrorList.LockerInitializeError")
                    return
                if value == PidErrorList.RcdInitializeError:
                    print("Şarja başlanamaz! PidErrorList.RcdInitializeError")
                    return
                
        if self.application.chargingStatus == ChargePointStatus.faulted:
            return
        

        if self.application.control_C_B:
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.suspended_ev)
        else:
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
        
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.get_command_pid_proximity_pilot()
            time.sleep(0.5)
            if self.application.ev.proximity_pilot_current == 0:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
                self.application.deviceState = DeviceState.FAULT
                return 
        print("self.application.ev.control_pilot",self.application.ev.control_pilot)
        if self.application.ev.control_pilot == ControlPlot.stateC.value:
            self.application.ev.charge = False
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Connecting,), daemon= True).start()
        
            print("self.application.cardType",self.application.cardType)
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
            print("Şarj C'den B'ye döndü Röle kapatıldı")
            self.application.serialPort.set_command_pid_relay_control(Relay.Off)
            time_start = time.time()
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
            while True:
                if self.application.chargingStatus == ChargePointStatus.faulted:
                    self.application.deviceState = DeviceState.FAULT
                    break
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
                    self._lock_connector_set_control_pilot()
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
        print("****************************************************************** waiting_state_c")
        
        self.application.ev.charge = False
        self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
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
        self.application.databaseModule.set_charge("True",str(self.id_tag),str(self.transaction_id))
        
        # test uygulmasına mid meter bağlıp bağlanmayacağı bilgisini gönder.
        self.application.testWebSocket.send_there_is_mid_meter(self.application.settings.deviceSettings.mid_meter)
        
        # Röle kontrol ediliyor ... (Açılmazsa hata)
        self.application.serialPort.get_command_pid_relay_control()
        time.sleep(1)
        print("self.application.ev.pid_relay_control",self.application.ev.pid_relay_control)

        self.application.testWebSocket.send_relay_control_on(self.application.ev.pid_relay_control)

        if self.application.ev.pid_relay_control == False:
            print("Röle devrede değil !!!!!!!!!!")
            self.application.deviceState = DeviceState.FAULT
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.faulted)
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
            return
        
        while True:
            print("Charge wile .................")
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.charging)
            if self.application.deviceState != DeviceState.CHARGING:
                return
            if (self.application.settings.deviceSettings.mid_meter == True or self.application.settings.deviceSettings.externalMidMeter == True) and self.application.modbusModule.connection == False:
                
                print(" ??????????????????????????????????????????????????????????????? Mid meter bağlantısı bekleniyor...", "self.application.modbusModule.port",self.application.modbusModule.port,"self.application.modbusModule.slave_address",self.application.modbusModule.slave_address, "self.application.modbusModule.baudrate",self.application.modbusModule.baudrate)

                if self.application.ev.control_pilot == ControlPlot.stateC.value:
                    if time.time() - time_start > 6:
                        print("Mid meter bağlanamadı")
                        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
                        self.application.deviceState = DeviceState.FAULT
                        self.application.testWebSocket.send_mid_meter_state(False)
                        break
                else:
                    print("self.application.ev.control_pilot",self.application.ev.control_pilot)
                    return
            elif self.application.settings.deviceSettings.mid_meter == False and self.application.settings.deviceSettings.externalMidMeter == False:
                self.application.meter_values_on = True
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.charging)
                self.application.serialPort.get_command_pid_current()
                self.application.serialPort.get_command_pid_voltage()
                self.application.serialPort.get_command_pid_power(PowerType.kw)
                self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
                
            time.sleep(1)
            
    def charging(self):
        print("****************************************************************** charging")
        # “Locker Initialize Error”  ve   “Rcd Initialize Error” hataları varsa şarja izin verme
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    print("Şarja başlanamaz! PidErrorList.LockerInitializeError")
                    return
                if value == PidErrorList.RcdInitializeError:
                    print("Şarja başlanamaz! PidErrorList.RcdInitializeError")
                    return
                
        if self.application.control_A_B_C != True: # A'dan C'ye geçmiş ise
            self.application.deviceState = DeviceState.CONNECTED
            return
        if self.application.ev.card_id != "" and self.application.ev.card_id != None:
            self.id_tag = self.application.ev.card_id
        if self.application.ev.id_tag != None:
            self.id_tag = self.application.ev.id_tag
        print("self.application.cardType",self.application.cardType)
        
        if self.application.cardType == CardType.LocalPnC:
            self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
            self.application.ev.charge = True
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
            print("Authorize edilmesine gerek yok şarj başlangıcı...")
            self.application.serialPort.set_command_pid_relay_control(Relay.On)
            self.charge_while()
                
        elif self.application.cardType == CardType.BillingCard and self.application.ocppActive:
            if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                if self.application.ev.charge == False:
                    self.application.ev.charge = True
                    self.application.chargePoint.start_transaction_result = None
                    
                    
                    if self.application.ev.reservation_id != None:
                        print("self.application.ev.reservation_id_tag",self.application.ev.reservation_id_tag)
                        print("self.id_tag",self.id_tag)
                        if self.application.ev.reservation_id_tag == self.id_tag or self.application.ev.reservation_id_tag == self.application.ev.card_id:    # rezerve eden kişinin id_tagimi
                            self.id_tag = self.application.ev.reservation_id_tag
                            date_object = datetime.strptime(self.application.ev.expiry_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                            timestamp = time.mktime(date_object.timetuple())
                            if timestamp - time.time() > 0: # hala şarj etmek için zamanı varsa
                                print("Rezervasyonla şarj başlatılıyor")
                                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_start_transaction(connector_id=1,id_tag=self.id_tag,meter_start=0,reservation_id=self.application.ev.reservation_id),self.application.loop)
                                self.application.ev.reservation_id = None
                                self.application.ev.reservation_id_tag = None
                                self.application.ev.expiry_date = None
                            else:
                                print("Şarj etmek için süre dolmuş")
                                self.application.ev.reservation_id = None
                                self.application.ev.reservation_id_tag = None
                                self.application.ev.expiry_date = None
                                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
                                self.application.deviceState = DeviceState.FAULT
                                return
                        else:
                            print("Reserve eden kişinin id tagi değil")
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Fault,), daemon= True).start()
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
                print("ocpp ile authorize edilmiş. ")
                if self.application.chargePoint.start_transaction_result == AuthorizationStatus.accepted:
                    pass
                else:
                    print("\nStart Transaction Cevabı Olumsuz !!! FAULT\n")
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
                print("authorize edilmemiş authorize edilmesi beklenecek...")
                self.application.deviceState = DeviceState.WAITING_AUTH
        
        elif self.application.cardType == CardType.StartStopCard:
            if self.application.ev.start_stop_authorize:
                self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                self.application.ev.charge = True
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
                print("rfid kart ile authorize edilmiş.")
                self.application.serialPort.set_command_pid_relay_control(Relay.On)
                time_start = time.time()
                self.charge_while()
            else:
                print("authorize edilmemiş authorize edilmesi beklenecek...")
                self.application.deviceState = DeviceState.WAITING_AUTH
          
    def fault(self):
        print("****************************************************************** fault")
        self.application.databaseModule.set_charge("False","","")
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
        print("****************************************************************** suspended_evse")
        self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.suspended_evse)
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        # time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.unlock()
             
    def stopped_by_evse(self):
        print("****************************************************************** stopped_by_evse")
        self.application.databaseModule.set_charge("False","","")
        self.application.ev.start_stop_authorize = False
        if (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive):
            self.application.chargePoint.authorize = None
        self.application.ev.card_id = ""
        self.application.ev.id_tag = None
        self.application.ev.charge = False
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.ChargingStopped,), daemon= True).start()
        self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.finishing)
        print("************************* cardType", self.application.cardType, "meter_values_on",self.application.meter_values_on)
        if (self.application.cardType == CardType.BillingCard) and self.application.meter_values_on:
            self.application.meter_values_on = False
            try:
                print("Attempting to send stop transaction...")
                future = asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(), self.application.loop)
                result = future.result()  # Blocking call to get the result
                print("Stop transaction sent successfully, result:", result)
            except Exception as e:
                print("Error sending stop transaction:", e)

            # asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
            
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        if self.application.socketType == SocketType.Type2:
            self.unlock()
            
    def idle(self):
        print("****************************************************************** idle")
        self.application.databaseModule.set_charge("False","","")
        self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
        if self.application.ev.reservation_id != None:
            print("Reservation var")
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
            self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.preparing)
            return
        
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    print("Şarja başlanamaz! PidErrorList.LockerInitializeError")
                    return
                if value == PidErrorList.RcdInitializeError:
                    print("Şarja başlanamaz! PidErrorList.RcdInitializeError")
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
        self.application.databaseModule.set_charge("False","","")
        self.application.ev.start_stop_authorize = False
        print("****************************************************************** stopped_by_user",self.application.ev.start_stop_authorize)
        
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
        
        
