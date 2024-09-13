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
    def __init__(self, application, logger) -> None:
        self.application = application
        self.logger = logger
        self.serial = serial.Serial("/dev/ttyS2", 115200, timeout=1)
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
        self.import_energy_register_kwh = 0
        
        self.parameter_data = "001"
        self.connector_id = "1"
        self.set_time_rfid = time.time()
        self.delete_time_rfid = time.time()
        self.led_state = LedState.StandBy

        self.time_start = time.time()
        
        os.system("gpio-test.64 w e 11 0 > /dev/null 2>&1")
        time.sleep(0.5)

        os.system("gpio-test.64 w e 10 1 > /dev/null 2>&1")
        time.sleep(0.5)
        
        os.system("gpio-test.64 w e 10 0 > /dev/null 2>&1")

        Thread(target=self.read,daemon=True).start()
        Thread(target=self.write,daemon=True).start()

        Thread(target=self.serial_port_thread,daemon=True).start()
        Thread(target=self.get_command_pid_rfid,daemon=True).start()

        Thread(target=self.test,daemon=True).start()

    def test(self):
        while True:
            try:
                if time.time() - self.time_start > 10:
                    print(Color.Red.value,"Seri port iletişimi kesildi!!!!!!!!!!!!!!!!!!!!!!!!!")
            except Exception as e:
                pass
            time.sleep(1)

    def serial_port_thread(self):
        while True:
            if time.time() - self.time_20 > 20:
                if self.application.led_state != LedState.RfidVerified and self.application.led_state != LedState.RfidFailed:
                    self.time_20 = time.time()
                    print("Led güncelleme -> ",self.application.led_state)
                    self.set_command_pid_led_control(self.application.led_state)
                self.get_command_pid_evse_temp()
            self.get_command_PID_control_pilot()
            self.get_command_pid_error_list()
            if time.time() - self.time_10 > 10:
                self.time_10 = time.time()
                self.get_command_pid_energy(EnergyType.kwh)
                self.get_command_pid_proximity_pilot()
            time.sleep(1)

    def write(self):
        self.time_start = time.time()
        while True:
            try:
                if len(self.send_data_list) > 0:
                    self.serial.write(self.send_data_list[0])
                    self.time_start = time.time()
                    self.send_data_list.pop(0)
            except Exception as e:
                print("write Exception:",e)
            time.sleep(0.1)

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
            print("calculate_checksum",e)
        
    #   ************************ SEND *****************************************************
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
            print("get_command_PID_control_pilot",e)

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
            print("get_command_pid_proximity_pilot",e)
            
            
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
            print("set_command_pid_cp_pwm",e)
        

    def get_command_pid_cp_pwm(self):
        try:
            self.parameter_data = "001"
            self.connector_id = "1"
            data = self.get_command + self.pid_cp_pwm_control + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_cp_pwm",e)
        
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
            print("set_command_pid_relay_control",e)

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
            print("get_command_pid_relay_control",e)

        
    def set_command_pid_led_control(self, led_state: LedState):
        try: 
            self.parameter_data = "002"
            data = self.set_command + self.pid_led_control + self.parameter_data + self.connector_id + led_state.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
            if led_state == LedState.RfidVerified or led_state == LedState.RfidFailed:
                time.sleep(2)
            else:
                self.led_state = led_state

            if led_state == LedState.RfidVerified or led_state == LedState.RfidFailed:
                self.parameter_data = "002"
                data = self.set_command + self.pid_led_control + self.parameter_data + self.connector_id + self.led_state.value
                checksum = self.calculate_checksum(data)
                send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
                self.send_data_list.append(send_data)
                self.application.led_state = self.led_state
        except Exception as e:
            print("set_command_pid_led_control",e)
        

    def get_command_pid_led_control(self):
        try: 
            self.parameter_data = "001"
            data = self.get_command + self.pid_led_control + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_led_control",e)
        

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
            print("set_command_pid_locker_control",e)
       

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
            print("get_command_pid_locker_control",e)
        

    def get_command_pid_current(self):
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_current + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_current",e)
        
        
    def get_command_pid_voltage(self):
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_voltage + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_voltage",e)

    def get_command_pid_power(self, power_type: PowerType):
        try:
            self.parameter_data = "002"
            data = self.get_command + self.pid_power + self.parameter_data + self.connector_id + power_type.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_power",e)
        

    def get_command_pid_energy(self, energy_type: EnergyType):
        try:
            self.parameter_data = "002"
            data = self.get_command + self.pid_energy + self.parameter_data + self.connector_id + energy_type.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_energy",e)
        

    def set_command_pid_rfid(self):
        try: 
            '''
            Yeni bir okuma işleminden önce Linux tarafından MCU Board’a bir kez SET komutu gönderilerek, hafızasındaki UniqID ‘nin silinmesi talep edilir
            '''
            self.parameter_data = "002"
            data = self.set_command + self.pid_rfid + self.parameter_data + self.connector_id + "R"
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("set_command_pid_rfid",e)

    def get_command_pid_rfid(self):
        try:
            time.sleep(10)
            while True:
                self.parameter_data = "001"
                data = self.get_command + self.pid_rfid + self.parameter_data + self.connector_id
                checksum = self.calculate_checksum(data)
                send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
                self.send_data_list.append(send_data)
                time.sleep(0.5)
        except Exception as e:
            print("get_command_pid_rfid",e)


    def get_command_pid_evse_temp(self):
        try:
            self.parameter_data = "002"
            data = self.get_command + self.pid_evse_temp + self.parameter_data + self.connector_id + "R"
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_evse_temp",e)
        
            
    def get_command_pid_error_list(self):
        try:
            self.parameter_data = "001"
            data = self.get_command + self.pid_error_list + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
        except Exception as e:
            print("get_command_pid_error_list",e)
        

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
                self.application.ev.control_pilot = data[7]
        except Exception as e:
            print("get_response_control_pilot",e)


    def get_response_pid_proximity_pilot(self, data):
        try:
            if data[2] == self.pid_proximity_pilot:
                self.application.ev.proximity_pilot = data[7]
        except Exception as e:
            print("get_response_pid_proximity_pilot",e)
            
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
            print("set_response_pid_cp_pwm",e)
            

    def get_response_pid_cp_pwm(self, data):
        try:
            if data[2] == self.pid_cp_pwm_control:
                digit_100 = int(data[7]) * 100
                digit_10 = int(data[8]) * 10
                digit_1 = int(data[9])
                digit_01 = int(data[10]) / 10
                original_number = digit_100 + digit_10 + digit_1 + digit_01
                self.application.ev.pid_cp_pwm = original_number
                print("self.application.ev.pid_cp_pwm",self.application.ev.pid_cp_pwm)
        except Exception as e:
            print("get_response_pid_cp_pwm",e)

    def set_response_pid_relay_control(self, data):
        try:
            if data[2] == self.pid_relay_control:
                result = data[7]
        except Exception as e:
            print("set_response_pid_relay_control",e)
       

    def get_response_pid_relay_control(self, data):
        try:
            if data[2] == self.pid_relay_control:
                if data[7] == "1":
                    self.application.ev.pid_relay_control = Relay.On
                elif data[7] == "0":
                    self.application.ev.pid_relay_control = Relay.Off
                print(Color.Macenta.value,"*********************** get response relay",self.application.ev.pid_relay_control)
        except Exception as e:
            print("get_response_pid_relay_control",e)

    def set_response_pid_led_control(self, data):
        try:
            if data[2] == self.pid_led_control:
                result = data[7]
        except Exception as e:
            print("set_response_pid_led_control",e)

    def get_response_pid_led_control(self,data):
        try:
            if data[2] == self.pid_led_control:
                self.application.ev.pid_led_control = data[7]
                result = data[7]
        except Exception as e:
            print("get_response_pid_led_control",e)

    def set_response_pid_locker_control(self,data):
        try:
            if data[2] == self.pid_locker_control:
                result = data[7]
        except Exception as e:
            print("set_response_pid_locker_control",e)

    def get_response_pid_locker_control(self, data):
        try:
            if data[2] == self.pid_locker_control:
                if data[7] == LockerState.Unlock.value:
                    self.application.ev.pid_locker_control = LockerState.Unlock
                elif data[7] == LockerState.Lock.value:
                    self.application.ev.pid_locker_control = LockerState.Lock
        except Exception as e:  
            print("get_response_pid_locker_control",e)

    def get_response_pid_current(self, data):
        try:
            if data[2] == self.pid_current:
                self.current_L1 = round(int(data[8])*100 + int(data[9])*10 + int(data[10])*1 + int(data[11])*0.1 + int(data[12])*0.01 + int(data[13])*0.001 , 3)
                self.current_L2 = round(int(data[15])*100 + int(data[16])*10 + int(data[17])*1 + int(data[18])*0.1 + int(data[19])*0.01 + int(data[20])*0.001 , 3)
                self.current_L3 = round(int(data[22])*100 + int(data[23])*10 + int(data[24])*1 + int(data[25])*0.1 + int(data[26])*0.01 + int(data[27])*0.001 , 3)
                # print(f"Current L1: {self.current_L1}, L2: {self.current_L2}, L3: {self.current_L3}")
        except Exception as e:
            print("get_response_pid_current",e)


    def get_response_pid_voltage(self, data):
        try:
            if data[2] == self.pid_voltage:
                self.voltage_L1 = round(int(data[8])*1000 + int(data[9])*100 + int(data[10])*10 + int(data[11])*1 + int(data[12])*0.1 + int(data[13])*0.01 , 3)
                self.voltage_L2 = round(int(data[15])*1000 + int(data[16])*100 + int(data[17])*10 + int(data[18])*1 + int(data[19])*0.1 + int(data[20])*0.01 , 3)
                self.voltage_L3 = round(int(data[22])*1000 + int(data[23])*100 + int(data[24])*10 + int(data[25])*1 + int(data[26])*0.1 + int(data[27])*0.01 , 3)
                # print(f"Voltage L1: {self.voltage_L1}, L2: {self.voltage_L2}, L3: {self.voltage_L3}")
        except Exception as e:
            print("get_response_pid_voltage",e)

    def get_response_pid_power(self,data):
        try:
            if data[2] == self.pid_power:
                self.power = round(int(data[8]) * 100 + int(data[9]) * 10 + int(data[10]) * 1 + int(data[11]) * 0.1 + int(data[12]) * 0.01 + int(data[13]) * 0.001, 3)
                # print(f"Power: {self.power}")
        except Exception as e:
            print("get_response_pid_power",e)

    def get_response_pid_energy(self, data):
        try:
            if data[2] == self.pid_energy:
                # print(f"Device state: {self.application.deviceState}")
                self.import_energy_register_kwh = int(data[8])*1000000 + int(data[9])*100000 + int(data[10])*10000 + int(data[11])*1000 + int(data[12])*100 + int(data[13])*10 + int(data[14])*1 + int(data[15])*0.1 + int(data[16])*0.01 + int(data[17])*0.001
                if self.application.deviceState == DeviceState.IDLE:
                    self.firstEnergy = round(self.import_energy_register_kwh, 3)
                self.energy = round(self.import_energy_register_kwh - self.firstEnergy, 3)
        except Exception as e:
            print("get_response_pid_energy",e)

    def set_response_pid_rfid(self, data):
        try:
            if data[2] == self.pid_rfid:
                result = data[7]
        except Exception as e:
            print("set_response_pid_rfid",e)


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
            print("get_response_pid_rfid",e)
                    
    def get_response_pid_evse_temp(self, data):
        try: 
            if data[2] == self.pid_evse_temp:
                temp_sign = data[8]
                temp = round(int(data[9])*100 + int(data[10])*10 + int(data[11])*1 + int(data[12])*0.1 , 1)
                self.application.ev.temperature = temp_sign + str(temp)
        except Exception as e:
            print("get_response_pid_evse_temp",e)

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
            print("get_response_pid_error_list",e)
            
    def read(self):
        incoming = ""
        while True:
            try:
                try:
                    incoming = self.serial.readline()
                    incoming = incoming.decode('utf-8')
                except:
                    print(Color.Red.value,"Seri port data bozuk geldi")
                if len(incoming) > 0:
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
            time.sleep(0.1)
