import serial
import time
from threading import Thread
from src.enums import *
from datetime import datetime
import os
import asyncio
from ocpp.v16.enums import *
import threading

class SerialPort():
    def __init__(self,application) -> None:
        self.application = application
        self.serial = serial.Serial("/dev/ttyS2", 115200, timeout=5)
        self.send_data_list = []
        self.error = False
        self.error_list = []

        self.time_20 = time.time()
        self.time_10 = time.time()

        self.stx = b'\x02'
        self.lf = b'\n'

        self.get_command    = 'G'           # Bilgisayar tarafından bir verinin okunması için gönderilecektir.
        self.get_response   = 'g'           # Bilgisayar tarafından bir verinin okunması için gönderilecektir.
        self.set_command    = 'S'           # Bilgisayar tarafından bir verinin değiştirilmesi için gönderilecektir.
        self.set_response   = 's'           # MCU tarafından ilgili veri set edildikten sonra cevap olarak dönecektir.

        self.pid_control_pilot      = "C"   # PID_CONTROL_PILOT	    ('C')
        self.pid_proximity_pilot    = "X"   # PID_PROXIMITY_PILOT   ('X')
        self.pid_relay_control      = "R"   # PID_RELAY_CONTROL	    ('R')
        self.pid_cp_pwm_control     = "G"   # PID_CP_PWM_CONTROL	('G')
        self.pid_locker_control     = "K"   # PID_LOCKER_CONTROL	('K')
        self.pid_led_control        = "L"   # PID_LED_CONTROL	    ('L')
        self.pid_current            = "I"   # PID_CURRENT		    ('I')
        self.pid_voltage            = "V"   # PID_VOLTAGE		    ('V')
        self.pid_power              = "P"   # PID_POWER		        ('P')
        self.pid_energy             = "E"   # PID_ENERGY		    ('E')
        self.pid_evse_temp          = "T"   # PID_EVSE_TEMP		    ('T')
        self.pid_rfid               = "N"   # PID_RFID              ('N')
        self.pid_error_list         = "H"   # PID_ERROR_LİST        ('H')
        
        self.current_L1 = 0
        self.current_L2 = 0
        self.current_L3 = 0
        self.voltage_L1 = 0
        self.voltage_L2 = 0
        self.voltage_L3 = 0
        self.power = 0
        self.energy = 0
        self.firstEnergy = 0
        
        self.parameter_data = "001"
        self.connector_id = "1"
        self.set_time_rfid = time.time()
        self.delete_time_rfid = time.time()

        self.connection = False

    def seri_port_reset(self):
        try:
            os.system("gpio-test.64 w e 10 1 > /dev/null 2>&1")
            time.sleep(0.5)
            os.system("gpio-test.64 w e 10 0 > /dev/null 2>&1")
            time.sleep(1)
        except Exception as e:
            print("seri_port_reset Exception:",e)

    def serial_port_thread(self):
        while True:
            try:
                self.get_command_PID_control_pilot()
                self.get_command_pid_error_list()
                self.get_command_pid_current()
                self.get_command_pid_voltage()
                self.get_command_pid_power(PowerType.kw)
                self.get_command_pid_energy(EnergyType.kwh)
                self.get_command_pid_proximity_pilot()
                self.get_command_pid_cp_pwm()
                self.get_command_pid_relay_control()
                self.get_command_pid_led_control()
                self.get_command_pid_locker_control()
                self.get_command_pid_evse_temp()
            except Exception as e:
                print("serial_port_thread Exception:",e)
            time.sleep(1)

    def write(self):
        while True:
            try:
                if len(self.send_data_list) > 0:
                    self.serial.write(self.send_data_list[0])
                    self.send_data_list.pop(0)
            except Exception as e:
                print("write Exception:",e)
            time.sleep(0.05)

    def read(self):
        while True:
            try:
                start_time = time.time()
                try:
                    incoming = self.serial.readline()
                    incoming = incoming.decode('utf-8')
                except:
                    pass
                finish_time = time.time()
                if finish_time - start_time > 3:
                    self.connection = False
                    self.send_data_list = []
                    print(Color.Red.value,"MCU not connected!")
                else:
                    self.connection = True
                if len(incoming) > 1:
                    incoming = list(incoming)
                    if incoming[1] == self.get_response:
                        self.get_response_control_pilot(incoming)
                        self.get_response_pid_proximity_pilot(incoming)
                        self.get_response_pid_relay_control(incoming)
                        self.get_response_pid_led_control(incoming)
                        self.get_response_pid_locker_control(incoming)
                        self.get_response_pid_current(incoming)
                        self.get_response_pid_power(incoming)
                        self.get_response_pid_voltage(incoming)
                        self.get_response_pid_energy(incoming)
                        self.get_response_pid_rfid(incoming)
                        self.get_response_pid_evse_temp(incoming)
                        self.get_response_pid_error_list(incoming)
                        self.get_response_pid_cp_pwm(incoming)
                    elif incoming[1] == self.set_response:
                        self.set_response_pid_cp_pwm(incoming)
                        self.set_response_pid_relay_control(incoming)
                        self.set_response_pid_led_control(incoming)
                        self.set_response_pid_locker_control(incoming)
                        self.set_response_pid_rfid(incoming)
            except Exception as e:
                print("read Exception",e)
            time.sleep(0.01)

    def calculate_checksum(self,data):
        try:
            checksum =  int.from_bytes(self.stx, "big")
            for i in data:
                checksum += ord(i)
            checksum = checksum%256
            checksum = str(checksum)
            lenght = len(checksum)
            if lenght < 3:
                for i in  range(0,3-lenght):
                    checksum = "0" + checksum
            return checksum
        except Exception as e:
            print("calculate_checksum Exception:",e)
    
    #   ************************ SEND GET COMMAND **********************************************

    def get_command_PID_control_pilot(self):
        '''
        Şarj kablosu ile araç arasında kablo bağlantısı yapıldıktan sonra kablo üzerindeki CP(Control Pilot) 
        iletkeni vasıtasıyla bir haberleşme gerçekleşmektedir.
        State A : Not Connected
        State B : EV connected, ready to charge
        State C : EV charging
        State D : EV charging, ventilation required
        State E : Error
        State F : Unknown error
        '''
        try:
            self.parameter_data = "001"
            self.connector_id = "1"
            data = self.get_command + self.pid_control_pilot + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_PID_control_pilot Exception:",e)

    def get_command_pid_proximity_pilot(self):
        '''
        Soketli Tip AC Şarj Cihazları'nda bu sorgulanmalıdır. (Kendi üzerinde şarj kablosu olmayan!)
        
        Şarj işlemi başlatılırken, tüm hata durumları kontrol edilir ve Control Pilot sinyalinden “State C” 
        alındıktan sonra kablonun takılı olup olmadığı Proximity Pilot sinyali okunarak kontrol edilir ve 
        takılı olan kablonun maximum akım taşıma kapasitesi algılandıktan sonra şarj işlemine devam edilir. 
        
        Örneğin, AC Şarj cihazı 32 Amper akım verme kapasitesine sahip olduğu halde, takılan kablo 
        13 Amperlik bir kablo ise bu durumda araçtan, kablonun maximum kapasitesi kadar(13A) akım çekilmesi 
        talep edilir. (Bu işlem Control Pilot ucundaki PWM duty genişliği ile ayarlanır. (Bknz:PID_CP_PWM)
        '''
        try:
            self.parameter_data = "001"
            self.connector_id = "1"
            data = self.get_command + self.pid_proximity_pilot + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_proximity_pilot Exception:",e)
      
    def get_command_pid_cp_pwm(self):
        try:
            self.parameter_data = "001"
            self.connector_id = "1"
            data = self.get_command + self.pid_cp_pwm_control + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_cp_pwm Exception:",e)
        
    def get_command_pid_relay_control(self):
        '''
        Rölenin 1 yada 0 olduğunu döner.
        '''
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_relay_control + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_relay_control Exception:",e)

    def get_command_pid_led_control(self):
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_led_control + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_led_control Exception:",e)

    def get_command_pid_locker_control(self): 
        '''
        Soketli tip Şarj Cihazlarında soket içerisindeki kilit mekanizmasının kontrolü 
        '''
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_locker_control + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_locker_control Exception:",e)

    def get_command_pid_current(self):
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_current + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_current Exception:",e)
        
    def get_command_pid_voltage(self):
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_voltage + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_voltage Exception:",e)

    def get_command_pid_power(self, power_type: PowerType):
        try:
            self.parameter_data = "002"
            data = self.get_command + self.pid_power + self.parameter_data + self.connector_id + power_type.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_power Exception:",e)

    def get_command_pid_energy(self, energy_type: EnergyType):
        try:
            self.parameter_data = "002"
            data = self.get_command + self.pid_energy + self.parameter_data + self.connector_id + energy_type.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_energy Exception:",e)

    def get_command_pid_rfid(self):
        time.sleep(10)
        while True:
            try:
                self.parameter_data = "001"
                data = self.get_command + self.pid_rfid + self.parameter_data + self.connector_id
                checksum = self.calculate_checksum(data)
                send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
                self.send_data_list.append(send_data)
            except Exception as e:
                print("get_command_pid_rfid Exception:",e)
            time.sleep(0.5)

    def get_command_pid_evse_temp(self):
        try:
            self.parameter_data = "002"
            data = self.get_command + self.pid_evse_temp + self.parameter_data + self.connector_id + "R"
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_evse_temp Exception:",e)
            
    def get_command_pid_error_list(self):
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_error_list + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_error_list Exception:",e)
        
    #   ************************ SEND SET COMMAND **********************************************
    def set_command_pid_cp_pwm(self,max_current):
        '''
        Control Pilot PWM sinyalini set edebilmek(kontrol etmek) için aşağıdaki paket gönderilir
        '''
        try:
            print(Color.Yellow.value,f"Pid CP PWM : {max_current} ")
            max_current = float(max_current)
            digit_100 = int(max_current // 100) % 10
            digit_10 = int(max_current // 10) % 10
            digit_1 = int(max_current) % 10
            digit_01 = int(max_current * 10) % 10 
            max_current = f"{digit_100}{digit_10}{digit_1}{digit_01}"
            
            self.parameter_data = "005"
            self.connector_id = "1"
            data = self.set_command + self.pid_cp_pwm_control + self.parameter_data + self.connector_id + max_current
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_proximity_pilot Exception:",e)
       
    def set_command_pid_relay_control(self,relay:Relay):
        '''
        Röleyi kontrol etmek için (‘1’ veya ‘0’) paket gönderilir.
        A durumunda gönderilmez. B yada C durumunda olmalı
        '''
        try:
            print(Color.Yellow.value,"Röle:",relay)
            self.parameter_data = "002"
            data = self.set_command + self.pid_relay_control + self.parameter_data + self.connector_id + relay.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("set_command_pid_relay_control Exception:",e)

    def set_command_pid_led_control(self, led_state: LedState):
        try:
            self.parameter_data = "002"
            data = self.set_command + self.pid_led_control + self.parameter_data + self.connector_id + led_state.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("set_command_pid_led_control Exception:",e)

    def set_command_pid_locker_control(self,locker_state:LockerState):
        '''
        Soketli tip Şarj Cihazlarında soket içerisindeki kilit mekanizmasının kontrolü 
        '''
        try:
            print(Color.Green.value,"MCU'ya gönderilen komut:",locker_state)
            self.parameter_data = "002"
            data = self.set_command + self.pid_locker_control + self.parameter_data + self.connector_id + locker_state.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("set_command_pid_locker_control Exception:",e)

    def set_command_pid_rfid(self):
        '''
        Yeni bir okuma işleminden önce Linux tarafından MCU Board’a bir kez SET komutu gönderilerek, hafızasındaki UniqID ‘nin silinmesi talep edilir
        '''
        try:
            self.parameter_data = "002"
            data = self.set_command + self.pid_rfid + self.parameter_data + self.connector_id + "R"
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("set_command_pid_rfid Exception:",e)

    #   ************************ RESPONSE  *****************************************************

    def get_response_control_pilot(self,data):
        '''
        State A : Not Connected
        State B : EV connected, ready to charge
        State C : EV charging
        State D : EV charging, ventilation required
        State E : Error
        State F : Unknown error
        '''
        try:
            if data[2] == self.pid_control_pilot:
                if data[7] == ControlPlot.stateA.value:
                    self.application.deviceStateModule.control_pilot = ControlPlot.stateA
                elif data[7] == ControlPlot.stateB.value:
                    self.application.deviceStateModule.control_pilot = ControlPlot.stateB
                elif data[7] == ControlPlot.stateC.value:
                    self.application.deviceStateModule.control_pilot = ControlPlot.stateC
                elif data[7] == ControlPlot.stateD.value:
                    self.application.deviceStateModule.control_pilot = ControlPlot.stateD
                elif data[7] == ControlPlot.stateE.value:
                    self.application.deviceStateModule.control_pilot = ControlPlot.stateE
                elif data[7] == ControlPlot.stateF.value:
                    self.application.deviceStateModule.control_pilot = ControlPlot.stateF
        except Exception as e:
            print("get_response_control_pilot Exception:",e)

    def get_response_pid_proximity_pilot(self, data):
        try:
            if data[2] == self.pid_proximity_pilot:
                if data[7] == ProximityPilot.CableNotPlugged.value:
                    self.application.deviceStateModule.proximity_plot = ProximityPilot.CableNotPlugged
                    self.application.deviceStateModule.proximity_pilot_current = 0
                elif data[7] == ProximityPilot.Error.value:
                    self.application.deviceStateModule.proximity_plot = ProximityPilot.Error
                    self.application.deviceStateModule.proximity_pilot_current = 0
                elif data[7] == ProximityPilot.CablePluggedIntoCharger13Amper.value:
                    self.application.deviceStateModule.proximity_plot = ProximityPilot.CablePluggedIntoCharger13Amper
                    self.application.deviceStateModule.proximity_pilot_current = 13
                elif data[7] == ProximityPilot.CablePluggedIntoCharger20Amper.value:
                    self.application.deviceStateModule.proximity_plot = ProximityPilot.CablePluggedIntoCharger20Amper
                    self.application.deviceStateModule.proximity_pilot_current = 20
                elif data[7] == ProximityPilot.CablePluggedIntoCharger32Amper.value:
                    self.application.deviceStateModule.proximity_plot = ProximityPilot.CablePluggedIntoCharger32Amper
                    self.application.deviceStateModule.proximity_pilot_current = 32
                elif data[7] == ProximityPilot.CablePluggedIntoCharger63Amper.value:
                    self.application.deviceStateModule.proximity_plot = ProximityPilot.CablePluggedIntoCharger63Amper
                    self.application.deviceStateModule.proximity_pilot_current = 63
        except Exception as e:
            print("get_response_pid_proximity_pilot Exception:",e)
            
    def set_response_pid_cp_pwm(self, data):
        try:
            if data[2] == self.pid_cp_pwm_control:
                print("set response:", data)
                digit_100 = int(data[7]) * 100
                digit_10 = int(data[8]) * 10
                digit_1 = int(data[9])
                digit_01 = int(data[10]) / 10
                original_number = digit_100 + digit_10 + digit_1 + digit_01
                pid_cp_pwm = original_number
        except Exception as e:
            print("set_response_pid_cp_pwm Exception:",e)
            
    def get_response_pid_cp_pwm(self, data):
        try:
            if data[2] == self.pid_cp_pwm_control:
                digit_100 = int(data[7]) * 100
                digit_10 = int(data[8]) * 10
                digit_1 = int(data[9])
                digit_01 = int(data[10]) / 10
                original_number = digit_100 + digit_10 + digit_1 + digit_01
                self.application.deviceStateModule.pid_cp_pwm = original_number
        except Exception as e:
            print("get_response_pid_cp_pwm Exception:",e)

    def set_response_pid_relay_control(self, data):
        try:
            if data[2] == self.pid_relay_control:
                result = data[7]
        except Exception as e:
            print("set_response_pid_relay_control Exception:",e)

    def get_response_pid_relay_control(self, data):
        try:
            if data[2] == self.pid_relay_control:
                if data[7] == Relay.On.value:
                    self.application.deviceStateModule.relay = Relay.On
                elif data[7] == Relay.Off.value:
                    self.application.deviceStateModule.relay = Relay.Off
        except Exception as e:
            print("get_response_pid_relay_control Exception:",e)

    def set_response_pid_led_control(self, data):
        try:
            if data[2] == self.pid_led_control:
                result = data[7]
        except Exception as e:
            print("set_response_pid_led_control Exception:",e)

    def get_response_pid_led_control(self,data):
        try:
            if data[2] == self.pid_led_control:
                if data[7] == LedState.StandBy.value:
                    self.application.deviceStateModule.led_control = LedState.StandBy
                elif data[7] == LedState.Connecting.value:
                    self.application.deviceStateModule.led_control = LedState.Connecting
                elif data[7] == LedState.RfidVerified.value:
                    self.application.deviceStateModule.led_control = LedState.RfidVerified
                elif data[7] == LedState.Charging.value:
                    self.application.deviceStateModule.led_control = LedState.Charging
                elif data[7] == LedState.RfidFailed.value:
                    self.application.deviceStateModule.led_control = LedState.RfidFailed
                elif data[7] == LedState.NeedReplugging.value:
                    self.application.deviceStateModule.led_control = LedState.NeedReplugging
                elif data[7] == LedState.Fault.value:
                    self.application.deviceStateModule.led_control = LedState.Fault
                elif data[7] == LedState.ChargingStopped.value:
                    self.application.deviceStateModule.led_control = LedState.ChargingStopped
                elif data[7] == LedState.WaitingPluging.value:
                    self.application.deviceStateModule.led_control = LedState.WaitingPluging
                elif data[7] == LedState.DeviceOffline.value:
                    self.application.deviceStateModule.led_control = LedState.DeviceOffline
                elif data[7] == LedState.FirmwareUpdate.value:
                    self.application.deviceStateModule.led_control = LedState.FirmwareUpdate
                elif data[7] == LedState.RcdError.value:
                    self.application.deviceStateModule.led_control = LedState.RcdError
                elif data[7] == LedState.LockerError.value:
                    self.application.deviceStateModule.led_control = LedState.LockerError
                elif data[7] == LedState.DeviceInoperative.value:
                    self.application.deviceStateModule.led_control = LedState.DeviceInoperative
                elif data[7] == LedState.MCUNotConnected.value:
                    self.application.deviceStateModule.led_control = LedState.MCUNotConnected
        except Exception as e:
            print("get_response_pid_led_control Exception:",e)

    def set_response_pid_locker_control(self,data):
        try:
            if data[2] == self.pid_locker_control:
                result = data[7]
        except Exception as e:
            print("set_response_pid_locker_control Exception:",e)

    def get_response_pid_locker_control(self, data):
        try:
            if data[2] == self.pid_locker_control:
                if data[7] == LockerState.Unlock.value:
                    self.application.deviceStateModule.locker_control = LockerState.Unlock
                elif data[7] == LockerState.Lock.value:
                    self.application.deviceStateModule.locker_control = LockerState.Lock
        except Exception as e:
            print("get_response_pid_locker_control Exception:",e)

    def get_response_pid_current(self, data):
        try:
            if data[2] == self.pid_current:
                self.current_L1 = round(int(data[8])*100 + int(data[9])*10 + int(data[10])*1 + int(data[11])*0.1 + int(data[12])*0.01 + int(data[13])*0.001 , 3)
                self.current_L2 = round(int(data[15])*100 + int(data[16])*10 + int(data[17])*1 + int(data[18])*0.1 + int(data[19])*0.01 + int(data[20])*0.001 , 3)
                self.current_L3 = round(int(data[22])*100 + int(data[23])*10 + int(data[24])*1 + int(data[25])*0.1 + int(data[26])*0.01 + int(data[27])*0.001 , 3)
                # print(f"Current L1: {self.current_L1}, L2: {self.current_L2}, L3: {self.current_L3}")
        except Exception as e:
            print("get_response_pid_current Exception:",e)

    def get_response_pid_voltage(self, data):
        try:
            if data[2] == self.pid_voltage:
                self.voltage_L1 = round(int(data[8])*1000 + int(data[9])*100 + int(data[10])*10 + int(data[11])*1 + int(data[12])*0.1 + int(data[13])*0.01 , 3)
                self.voltage_L2 = round(int(data[15])*1000 + int(data[16])*100 + int(data[17])*10 + int(data[18])*1 + int(data[19])*0.1 + int(data[20])*0.01 , 3)
                self.voltage_L3 = round(int(data[22])*1000 + int(data[23])*100 + int(data[24])*10 + int(data[25])*1 + int(data[26])*0.1 + int(data[27])*0.01 , 3)
                # print(f"Voltage L1: {self.voltage_L1}, L2: {self.voltage_L2}, L3: {self.voltage_L3}")
        except Exception as e:
            print("get_response_pid_voltage Exception:",e)

    def get_response_pid_power(self,data):
        try:
            if data[2] == self.pid_power:
                self.power = round(int(data[8]) * 100 + int(data[9]) * 10 + int(data[10]) * 1 + int(data[11]) * 0.1 + int(data[12]) * 0.01 + int(data[13]) * 0.001, 3)
                # print(f"Power: {self.power}")
        except Exception as e:
            print("get_response_pid_power Exception:",e)

    def get_response_pid_energy(self, data):
        try:
            if data[2] == self.pid_energy:
                # print(f"Device state: {self.application.deviceState}")
                if self.application.deviceStateModule.control_pilot == ControlPlot.stateA:
                    self.firstEnergy = round(int(data[8])*1000000 + int(data[9])*100000 + int(data[10])*10000 + int(data[11])*1000 + int(data[12])*100 + int(data[13])*10 + int(data[14])*1 + int(data[15])*0.1 + int(data[16])*0.01 + int(data[17])*0.001 , 3)
                self.energy = round(int(data[8])*1000000 + int(data[9])*100000 + int(data[10])*10000 + int(data[11])*1000 + int(data[12])*100 + int(data[13])*10 + int(data[14])*1 + int(data[15])*0.1 + int(data[16])*0.01 + int(data[17])*0.001 , 3) - self.firstEnergy
                # print(f"Energy: {self.energy}")
        except Exception as e:
            print("get_response_pid_energy Exception:",e)

    def set_response_pid_rfid(self, data):
        try:
            if data[2] == self.pid_rfid:
                result = data[7]
        except Exception as e:
            print("set_response_pid_rfid Exception:",e)

    def get_response_pid_rfid(self, data):
        try:
            if data[2] == self.pid_rfid:
                card_id = ""
                card_id_length = int(data[7] + data[8])
                if card_id_length > 0:
                    for i in range(9,9+card_id_length):
                        card_id += data[i]
                if card_id != "":
                    print(Color.Blue.value,"Readed card id",card_id)
                if time.time() - self.delete_time_rfid > 2:
                    self.set_command_pid_rfid()
                    self.delete_time_rfid = time.time()
                if card_id != "":
                    if time.time() - self.set_time_rfid > 5:
                        print(Color.Yellow.value,"Card id set edildi",card_id)
                        self.set_time_rfid = time.time()
                        self.application.ev.card_id = card_id
        except Exception as e:
            print("get_response_pid_rfid Exception:",e)
                    
    def get_response_pid_evse_temp(self, data):
        try:
            if data[2] == self.pid_evse_temp:
                temp_sign = data[8]
                temp = round(int(data[9])*100 + int(data[10])*10 + int(data[11])*1 + int(data[12])*0.1 , 1)
                self.application.deviceStateModule.temperature = temp_sign + str(temp)
        except Exception as e:
            print("get_response_pid_rfid Exception:",e)

    def get_response_pid_error_list(self, data):
        try:
            error_list = []
            if data[2] == self.pid_error_list:
                if (int(data[7]) == 1):
                    error_list.append(PidErrorList.LockerInitializeError)
                if (int(data[8]) == 1):
                    error_list.append(PidErrorList.EVCommunicationPortError)
                if (int(data[9]) == 1):
                    error_list.append(PidErrorList.EarthDisconnectFailure)
                if (int(data[10]) == 1):
                    error_list.append(PidErrorList.RcdInitializeError)
                if (int(data[11]) == 1):
                    error_list.append(PidErrorList.RcdTripError)
                if (int(data[12]) == 1):
                    error_list.append(PidErrorList.HighTemperatureFailure)
                if (int(data[13]) == 1):
                    error_list.append(PidErrorList.OverCurrentFailure)
                if (int(data[14]) == 1):
                    error_list.append(PidErrorList.OverVoltageFailure)
                if (int(data[15]) == 1):
                    error_list.append(PidErrorList.InternalEnergyMeterFailure)
                if (int(data[16]) == 1):
                    error_list.append(PidErrorList.PowerSwitchFailure)
                if (int(data[17]) == 1):
                    error_list.append(PidErrorList.RFIDReaderFailure)
                if (int(data[18]) == 1):
                    error_list.append(PidErrorList.UnderVoltageFailure)
                if (int(data[19]) == 1):
                    error_list.append(PidErrorList.FrequencyFailure)
                if (int(data[20]) == 1):
                    error_list.append(PidErrorList.PhaseSequenceFailure)
                if (int(data[21]) == 1):
                    error_list.append(PidErrorList.OverPowerFailure)

                if len(error_list) > 0:
                    print(Color.Red.value,error_list)
                    self.error = True
                
                self.error_list = error_list
        except Exception as e:
            print("get_response_pid_error_list Exception:",e)

