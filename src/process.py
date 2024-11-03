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
        self.there_is_transaction = False
        self.id_tag = None
        self.transaction_id = None
        self.locker_error = False
        self.charge_try_counter = 0
        self.try_charge = False
        self.wait_fault = False
        self.rcd_trip_error = False
        self.locker_initialize_error = False
        db_idtag = self.application.databaseModule.get_charge()["id_tag"]
        db_tansactionid = self.application.databaseModule.get_charge()["transaction_id"]
        self.waiting_auth_value = False
        self.rfid_verified = None
        if db_idtag != None and db_idtag != "" and db_idtag != "None":
            self.id_tag = db_idtag

        if db_tansactionid != None and db_tansactionid != "" and db_tansactionid != "None":
            print("db_tansactionid",db_tansactionid)
            self.transaction_id = int(db_tansactionid)

        self.initially_charge = self.application.databaseModule.get_charge()["charge"] == "True"
        print("********************************** self.initially_charge",self.initially_charge,"self.transaction_id",self.transaction_id,"self.id_tag",self.id_tag)

    def relay_control(self,relay:Relay):
        counter = 0
        while True:
            if self.application.ev.pid_relay_control == relay:
                return True
            print(Color.Yellow.value,"relay komut verildi:",relay)
            self.application.serialPort.set_command_pid_relay_control(relay)
            time.sleep(0.5)
            self.application.serialPort.get_command_pid_relay_control()
            time.sleep(0.5)
            print(Color.Yellow.value,"relay okundu:",relay)
            if self.application.ev.pid_relay_control == relay:
                return True
            else:
                counter += 1
            if counter == 4:
                return False


    def unlock(self):
        time_start = time.time()
        while True:
            print("Kilit açılıyor...")
            self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
            time.sleep(0.5)
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
            time.sleep(0.5)
            self.application.serialPort.get_command_pid_locker_control()
            time.sleep(1)
            if self.application.ev.pid_locker_control == LockerState.Unlock:
                print(Color.Green.value,"Kilit açıldı.")
                break
            else:
                time.sleep(1)
                if time.time() - time_start > 10:
                    print(Color.Red.value,"10 saniyede kilit açılamadı!")
                    break

    def set_max_current(self):
        try:
            if self.application.socketType == SocketType.Type2:
                if self.application.max_current==None or self.application.ev.proximity_pilot_current==None:
                    print(Color.Yellow.value,"self.application.max_current",self.application.max_current)
                    print(Color.Yellow.value,"self.application.ev.proximity_pilot_current",self.application.ev.proximity_pilot_current)
                else:
                    if int(self.application.max_current) > int(self.application.ev.proximity_pilot_current):
                        self.application.serialPort.set_command_pid_cp_pwm(int(self.application.ev.proximity_pilot_current))
                    else:
                        self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
            elif self.application.socketType == SocketType.TetheredType:
                self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
        except Exception as e:
            print(Color.Red.value,"set_max_current process Exception:",e )

    def lock_control(self):
        print("Kilit kitleniyor...")
        self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        time.sleep(0.7)
        self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
        time_start = time.time()
        while True:
            self.application.serialPort.get_command_pid_locker_control()
            time.sleep(0.3)
            if self.application.ev.pid_locker_control == LockerState.Lock:
                print(Color.Yellow.value,"Kilit kitlendi.")
                self.set_max_current()
                self.application.deviceState = DeviceState.WAITING_STATE_C
                return True
            else:
                if time.time() - time_start > 3:
                    print(Color.Red.value,"3 saniyede kilit kitlenmedi!")
                    return False

    def _lock_connector_set_control_pilot(self):
        self.application.testWebSocket.send_socket_type(self.application.socketType.value)
        if self.application.socketType == SocketType.Type2:
            result = self.lock_control()
            control_counter = 0
            if not result:
                while control_counter < 2 and not result:
                    result = self.lock_control()
                    control_counter += 1
                if not result:
                    print(Color.Red.value, "Locker Error")
                    self.locker_error = True
                    self.application.deviceState = DeviceState.FAULT
                    self.application.change_status_notification(ChargePointErrorCode.connector_lock_failure,ChargePointStatus.faulted,"LockerInitializeError")
            self.application.testWebSocket.send_locker_state_lock(result)
        elif self.application.socketType == SocketType.TetheredType:
            self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
            self.application.deviceState = DeviceState.WAITING_STATE_C

    def connected(self):
        if len(self.application.serialPort.error_list) > 0:
            print("mcu hata var!")
            return
        if self.application.availability == AvailabilityType.inoperative:
            print("Cihaz inoperative durumda!")
            return
            # for value in self.application.serialPort.error_list:
            #     if value == PidErrorList.LockerInitializeError:
            #         return
            #     if value == PidErrorList.RcdInitializeError:
            #         return

        # if self.application.chargePointStatus == ChargePointStatus.faulted:
        #     return

        # if self.application.control_C_B and self.application.ev.control_pilot == ControlPlot.stateB.value and self.charge_try_counter != 0:
        # if self.application.control_C_B and self.application.ev.control_pilot == ControlPlot.stateB.value:
        #     self.application.deviceState = DeviceState.SUSPENDED_EV
        #     return

        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.get_command_pid_proximity_pilot()
            time.sleep(1)
            if self.application.ev.proximity_pilot_current == 0:
                print(Color.Red.value,"proximity_pilot_current : 0 hata")
                self.application.deviceState = DeviceState.FAULT
                return

        self.application.change_status_notification(ChargePointErrorCode.no_error, ChargePointStatus.preparing)
        self.application.ev.charge = False

        if self.application.cardType == CardType.LocalPnC:
            self._lock_connector_set_control_pilot()
            if self.application.control_C_B and self.application.ev.control_pilot == ControlPlot.stateB.value:
                self.application.deviceState = DeviceState.SUSPENDED_EV
                return
            else:
                self.application.deviceState = DeviceState.WAITING_STATE_C

        elif self.application.cardType == CardType.BillingCard:
            if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                self._lock_connector_set_control_pilot()
                if self.application.control_C_B and self.application.ev.control_pilot == ControlPlot.stateB.value:
                    self.application.deviceState = DeviceState.SUSPENDED_EV
                    return
                else:
                    self.application.deviceState = DeviceState.WAITING_STATE_C
            else:
                self.application.deviceState = DeviceState.WAITING_AUTH

        elif self.application.cardType == CardType.StartStopCard:
            if self.application.ev.start_stop_authorize:
                self._lock_connector_set_control_pilot()
                if self.application.control_C_B and self.application.ev.control_pilot == ControlPlot.stateB.value:
                    self.application.deviceState = DeviceState.SUSPENDED_EV
                    return
                else:
                    self.application.deviceState = DeviceState.WAITING_STATE_C
            else:
                self.application.deviceState = DeviceState.WAITING_AUTH
        return
        
    def waiting_auth(self):
        self.waiting_auth_value = True
        print(Color.Yellow.value,"Cihazın Authorize olması bekleniyor...")
        self.application.ev.charge = False
        if self.application.cardType == CardType.StartStopCard:
            time_start = time.time()
            while True:
                print(Color.Yellow.value,"Cihazın Authorize olması bekleniyor...")
                if self.application.ev.start_stop_authorize:
                    self.id_tag = self.application.ev.card_id
                    self._lock_connector_set_control_pilot()
                    break
                if self.application.deviceState != DeviceState.WAITING_AUTH:
                    break
                time.sleep(1)
        elif self.application.cardType == CardType.BillingCard and self.application.ocppActive:
                time_start = time.time()
                while True:
                    print(Color.Yellow.value,"Cihazın Authorize olması bekleniyor...")
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
                        break
                    time.sleep(1)  
        self.waiting_auth_value = False

    def waiting_state_c(self):
        print(Color.Yellow.value,"Cihazın şarja geçmesi bekleniyor... Şarja geçmezse 5 dk sonra sonlanacak...")
        self.application.ev.charge = False
        self.application.change_status_notification(ChargePointErrorCode.no_error, ChargePointStatus.preparing)
        time.sleep(1)
        
        time_start = time.time()
        while True:
            if self.application.ev.control_pilot == ControlPlot.stateB.value:
                if time.time() - time_start > 60*5:
                    self.application.deviceState = DeviceState.STOPPED_BY_EVSE
                    print(Color.Red.value,"Cihaz 5 dk boyunca şarja geçmediği için sonlandı!")
                    break
            elif self.application.ev.control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING
            else:
                break
            if self.application.deviceState != DeviceState.WAITING_STATE_C:
                return
            time.sleep(0.3)
            
    def meter_values_thread(self):
        interval = int(self.application.settings.configuration.MeterValueSampleInterval)
        while self.application.meter_values_on:
            try:
                asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_meter_values(), self.application.loop)
                time.sleep(interval)
            except Exception as e:
                print("meter_values_thread Exception:", e)

    def charge_while(self):
        print(Color.Yellow.value,"Cihaz şarja başlıyor... *************************************************************")
        if self.application.deviceState != DeviceState.CHARGING:
            return
        time_start = time.time()
        self.application.databaseModule.set_charge("True", str(self.id_tag), str(self.transaction_id))
        # self.application.serialPort.get_command_pid_relay_control()
        # time.sleep(1)

        if self.application.deviceState != DeviceState.CHARGING:
            return
        

        if self.relay_control(Relay.On) == False:
            print("if not self.application.ev.pid_relay_control self.application.ev.control_pilot",self.application.ev.control_pilot)
            self.application.deviceState = DeviceState.FAULT
            return
        
        while True:
            try:
                if self.application.deviceState != DeviceState.CHARGING or self.application.ev.charge == False or self.application.serialPort.error:
                    print(self.application.deviceState != DeviceState.CHARGING)
                    print(self.application.ev.charge == False)
                    print(self.application.serialPort.error)
                    print("Charging break!")
                    break
                if self.application.settings.deviceSettings.externalMidMeter:
                    print(Color.Blue.value,"External Mid Meter aktif.")
                elif self.application.settings.deviceSettings.mid_meter:
                    print(Color.Blue.value,"Mid Meter aktif.")
                if (self.application.settings.deviceSettings.mid_meter or self.application.settings.deviceSettings.externalMidMeter) and not self.application.modbusModule.connection:
                    if self.application.ev.control_pilot == ControlPlot.stateC.value:
                        if time.time() - time_start > 10:
                            if self.application.settings.deviceSettings.externalMidMeter:
                                print(Color.Red.value,"External Mid Meter bağlanamadı!")
                            elif self.application.settings.deviceSettings.mid_meter:
                                print(Color.Red.value,"Mid Meter bağlanamadı!")
                            self.application.deviceState = DeviceState.FAULT
                            self.application.testWebSocket.send_mid_meter_state(False)
                            break
                    else:
                        break
                elif self.application.settings.deviceSettings.mid_meter == False and self.application.settings.deviceSettings.externalMidMeter == False:
                    self.application.meter_values_on = True
                    self.application.serialPort.get_command_pid_current()
                    self.application.serialPort.get_command_pid_voltage()
                    self.application.serialPort.get_command_pid_power(PowerType.kw)
                    self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
                elif self.application.modbusModule.connection == True:
                    pass
                self.application.change_status_notification(ChargePointErrorCode.no_error, ChargePointStatus.charging)
                print("Cihaz şarjda...")
                self.application.ev.charge = True
            except Exception as e:
                print("**************************************************** charge_while Exception", e)
            time.sleep(1)

    def charging(self):
        if len(self.application.serialPort.error_list) > 0:
            print("Hata var!")
            return
        
        print(Color.Yellow.value,"Cihaz şarja başlayacak...")
        self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.preparing)
                
        if self.application.control_A_B_C != True: # A'dan C'ye geçmiş ise
            print("Cihaz A state'inden C statine geçmiş.")
            self.application.deviceState = DeviceState.CONNECTED
            return
        
        # if self.id_tag and self.application.cardType == CardType.BillingCard and self.application.ocppActive:
        #     if self.application.ev.control_pilot == ControlPlot.stateC.value:
        #         self.set_max_current()
        #         self.relay_control(Relay.On)
        #         self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.charging)
        #         if self.application.settings.deviceSettings.mid_meter == False and self.application.settings.deviceSettings.externalMidMeter == False:
        #             self.application.serialPort.get_command_pid_current()
        #             self.application.serialPort.get_command_pid_voltage()
        #             self.application.serialPort.get_command_pid_power(PowerType.kw)
        #             self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
        #         self.application.meter_values_on = True
        #         Thread(target=self.meter_values_thread,daemon=True).start()
        #         self.application.ev.charge = True
        #         self.charge_while()
        #         return

        if self.application.ev.card_id != "" and self.application.ev.card_id != None:
            self.id_tag = self.application.ev.card_id
        if self.application.ev.id_tag != None:
            self.id_tag = self.application.ev.id_tag
        if self.application.cardType == CardType.LocalPnC:
            self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
            self.application.ev.charge = True
            self.relay_control(Relay.On)
            self.set_max_current()
            self.charge_while()   
        elif self.application.cardType == CardType.BillingCard and self.application.ocppActive:
            if self.application.chargePoint.authorize == AuthorizationStatus.accepted:
                self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                if self.application.ev.charge == False:
                    self.application.ev.charge = True
                    # self.application.chargePoint.start_transaction_result = None
                    if self.application.ev.reservation_id != None:
                        if self.application.ev.reservation_id_tag == self.id_tag or self.application.ev.reservation_id_tag == self.application.ev.card_id:    # rezerve eden kişinin id_tagimi
                            self.id_tag = self.application.ev.reservation_id_tag
                            if not self.application.ev.is_reservation_expired():
                                future = asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_start_transaction(connector_id=1,id_tag=self.id_tag,meter_start=0,reservation_id=self.application.ev.reservation_id),self.application.loop)
                                result = future.result()
                                self.application.ev.clear_reservation()
                            else:
                                self.application.ev.clear_reservation()
                                self.application.deviceState = DeviceState.FAULT
                                return
                        else:
                            self.application.deviceState = DeviceState.FAULT
                            return
                    elif self.application.chargePoint.start_transaction_result == None:
                        future = asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_start_transaction(connector_id=1,id_tag=self.id_tag,meter_start=0,reservation_id=self.application.ev.reservation_id),self.application.loop)
                        result = future.result()
                    

                if self.application.chargePoint.start_transaction_result != AuthorizationStatus.accepted:
                    print("start_transaction_result:",self.application.chargePoint.start_transaction_result)
                    self.application.deviceState = DeviceState.FAULT
                    return
                
                if self.application.ev.control_pilot == ControlPlot.stateC.value:
                    self.application.ev.charge = True
                    self.set_max_current()
                    self.relay_control(Relay.On)
                    self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.charging)
                    if self.application.settings.deviceSettings.mid_meter == False and self.application.settings.deviceSettings.externalMidMeter == False:
                        self.application.serialPort.get_command_pid_current()
                        self.application.serialPort.get_command_pid_voltage()
                        self.application.serialPort.get_command_pid_power(PowerType.kw)
                        self.application.serialPort.get_command_pid_energy(EnergyType.kwh)
                    self.application.meter_values_on = True
                    Thread(target=self.meter_values_thread,daemon=True).start()
                    self.charge_while()
            else:
                self.application.deviceState = DeviceState.WAITING_AUTH
        
        elif self.application.cardType == CardType.StartStopCard:
            if self.application.ev.start_stop_authorize:
                self.application.ev.start_date = datetime.now().strftime("%d-%m-%Y %H:%M")
                self.application.ev.charge = True
                self.relay_control(Relay.On)
                self.set_max_current()
                time_start = time.time()
                self.charge_while()
            else:
                self.application.deviceState = DeviceState.WAITING_AUTH

    def fault(self):
        print("Fauld Process")
        self.application.ev.stop_pwm_off_relay()

        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    self.application.change_status_notification(ChargePointErrorCode.connector_lock_failure,ChargePointStatus.faulted,"LockerInitializeError")
                elif value == PidErrorList.EVCommunicationPortError:
                    self.application.change_status_notification(ChargePointErrorCode.ev_communication_error,ChargePointStatus.faulted,"EVCommunicationPortError")
                elif value == PidErrorList.EarthDisconnectFailure:
                    self.application.change_status_notification(ChargePointErrorCode.ground_failure,ChargePointStatus.faulted,"EarthDisconnectFailure")
                elif value == PidErrorList.RcdInitializeError:
                    self.application.change_status_notification(ChargePointErrorCode.ground_failure,ChargePointStatus.faulted,"RcdInitializeError")
                elif value == PidErrorList.RcdTripError:
                    self.application.change_status_notification(ChargePointErrorCode.ground_failure,ChargePointStatus.faulted,"RcdTripError")
                elif value == PidErrorList.HighTemperatureFailure:
                    self.application.change_status_notification(ChargePointErrorCode.high_temperature,ChargePointStatus.faulted,"HighTemperatureFailure")
                elif value == PidErrorList.OverCurrentFailure:
                    self.application.change_status_notification(ChargePointErrorCode.over_current_failure,ChargePointStatus.faulted,"OverCurrentFailure")
                elif value == PidErrorList.OverVoltageFailure:
                    self.application.change_status_notification(ChargePointErrorCode.over_voltage,ChargePointStatus.faulted,"OverVoltageFailure")
                elif value == PidErrorList.InternalEnergyMeterFailure:
                    self.application.change_status_notification(ChargePointErrorCode.power_meter_failure,ChargePointStatus.faulted,"InternalEnergyMeterFailure")
                elif value == PidErrorList.PowerSwitchFailure:
                    self.application.change_status_notification(ChargePointErrorCode.power_switch_failure,ChargePointStatus.faulted,"PowerSwitchFailure")
                elif value == PidErrorList.RFIDReaderFailure:
                    self.application.change_status_notification(ChargePointErrorCode.reader_failure,ChargePointStatus.faulted,"RFIDReaderFailure")
                elif value == PidErrorList.UnderVoltageFailure:
                    self.application.change_status_notification(ChargePointErrorCode.under_voltage,ChargePointStatus.faulted,"UnderVoltageFailure")
                elif value == PidErrorList.FrequencyFailure:
                    self.application.change_status_notification(ChargePointErrorCode.under_voltage,ChargePointStatus.faulted,"FrequencyFailure")
                elif value == PidErrorList.PhaseSequenceFailure:
                    self.application.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.faulted,"PhaseSequenceFailure")
                elif value == PidErrorList.OverPowerFailure:
                    self.application.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.faulted,"OverPowerFailure")
                elif value == PidErrorList.OverVoltageFailure:
                    self.application.change_status_notification(ChargePointErrorCode.over_voltage,ChargePointStatus.faulted,"OverVoltageFailure")
        elif self.locker_error:
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.faulted,"LockerError")
        elif (self.application.ev.control_pilot == ControlPlot.stateB.value or self.application.ev.control_pilot == ControlPlot.stateC.value):
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.faulted,"NeedReplugging")
        elif self.application.ev.proximity_pilot_current == 0:
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.faulted,"proximity_pilot_current = 0")
        else:
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.faulted)
        
        if (self.application.cardType != CardType.BillingCard):
            self.application.ev.clean_charge_variables()
        else:
            if self.application.info != "Offline":
                self.application.ev.clean_charge_variables()

        while True:
            self.wait_fault = True
            if self.application.ev.control_pilot != ControlPlot.stateA.value:
                time.sleep(1)
            elif len(self.application.serialPort.error_list) > 0:
                time.sleep(1)
            elif self.application.ev.control_pilot == ControlPlot.stateA.value:
                self.wait_fault = False
                break
            else:
                if self.application.availability == AvailabilityType.operative:
                    self.wait_fault = False
                    self.application.deviceState = DeviceState.IDLE
                    break
            
    def suspended_evse(self):
        print("Suspended evse function")
        if self.try_charge:
            return
        self.try_charge = True
        self.application.ev.stop_pwm_off_relay()
        self.charge_try_counter += 1
        self.application.meter_values_on = False
        if self.charge_try_counter == 4:
            self.application.deviceState = DeviceState.FAULT
            return
        print(Color.Yellow.value,"30 saniye sonra şarja geçmeyi deneyecek. Counter:",self.charge_try_counter)
        for value in self.application.serialPort.error_list:
            self.application.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.suspended_evse,value.name)
        time_start = time.time()
        while True:
            time.sleep(1)
            if time.time() - time_start > 30:
                print(Color.Yellow.value,"30 saniye doldu.")
                self.try_charge = False
                break
            if self.application.ev.control_pilot == ControlPlot.stateA.value:
                self.try_charge = False
                return
        if self.application.deviceState == DeviceState.SUSPENDED_EVSE:
            if self.application.ev.control_pilot == ControlPlot.stateB.value:
                self.application.deviceState = DeviceState.CONNECTED
            elif self.application.ev.control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING

    def suspended_ev(self):
        print("Şarj durduruldu. Beklemeye alındı. 5 dk içinde şarja geçmezse hataya düşecek...")
        self.application.change_status_notification(ChargePointErrorCode.no_error, ChargePointStatus.suspended_ev)
        self.relay_control(Relay.Off)
        self.application.meter_values_on = False
        time_start = time.time()
        self.application.serialPort.set_command_pid_cp_pwm(int(self.application.max_current))
        while True:
            print("Şarj durduruldu. Beklemeye alındı. 5 dk içinde şarja geçmezse hataya düşecek...")
            if self.application.chargePointStatus == ChargePointStatus.faulted:
                self.application.deviceState = DeviceState.FAULT
                break
            if self.application.ev.control_pilot == ControlPlot.stateB.value:
                if time.time() - time_start > 60 * 5:
                    self.application.deviceState = DeviceState.STOPPED_BY_EVSE
                    break
            else:
                break
            if self.application.deviceState != DeviceState.SUSPENDED_EV:
                break
            time.sleep(0.3)
       
    def stopped_by_evse(self):
        self.application.ev.stop_pwm_off_relay()
        self.application.ev.clean_charge_variables()
        self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.finishing)
     
    def idle(self):
        self.try_charge = False
        self.waiting_auth_value = False
        self.wait_fault = False
        self.rcd_trip_error = False
        self.locker_initialize_error = False
        self.charge_try_counter = 0
        self.locker_error = False
        self.application.ev.stop_pwm_off_relay()
        self.application.ev.clean_charge_variables()
        if self.application.cardType == CardType.BillingCard and self.application.ocppActive:
            self.application.chargePoint.start_transaction_result = None
    
        self.application.serialPort.get_command_pid_energy(EnergyType.kwh)

        if self.application.ev.reservation_id != None:
            print(Color.Green.value,"Bir reservasyon var. reservation_id:", self.application.ev.reservation_id)
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.preparing)
            return
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value == PidErrorList.LockerInitializeError:
                    return
                if value == PidErrorList.RcdInitializeError:
                    return
        if len(self.application.serialPort.error_list) == 0:
            if self.application.availability == AvailabilityType.operative:
                self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.available)
                             
    def stopped_by_user(self):
        self.application.ev.stop_pwm_off_relay()
        self.application.ev.clean_charge_variables()

