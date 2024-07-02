import serial
import time
from threading import Thread
from src.enums import *
from datetime import datetime
import os
import asyncio
from ocpp.v16.enums import *

class SerialPort():
    def __init__(self,application) -> None:
        self.application = application
        self.serial = serial.Serial("/dev/ttyS2",115200 ,timeout=1)
        # print("Serial connection...")
        self.send_data_list = []
        
        self.error_list = []

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
        self.pid_error_list          = "H"   # PID_ERROR_LİST        ('H')
        
        self.current_L1 = 0
        self.current_L2 = 0
        self.current_L3 = 0
        self.voltage_L1 = 0
        self.voltage_L2 = 0
        self.voltage_L3 = 0
        self.power = 0
        self.energy = 0
        
        self.parameter_data = "001"
        self.connector_id = "1"
        
        self.led_state = LedState.StandBy
        
        os.system("gpio-test.64 w e 10 1 > /dev/null 2>&1")
        time.sleep(0.5)
        os.system("gpio-test.64 w e 10 0 > /dev/null 2>&1")

        Thread(target=self.read,daemon=True).start()
        Thread(target=self.write,daemon=True).start()
        Thread(target=self.get_command_PID_control_pilot,daemon=True).start()
        Thread(target=self.get_command_pid_rfid,daemon=True).start()
        Thread(target=self.get_command_pid_error_list,daemon=True).start()
        Thread(target=self.get_command_pid_error_list_init,daemon=True).start()
        Thread(target=self.get_command_pid_evse_temp,daemon=True).start()
        
        self.set_command_pid_rfid()
        
        
        # Thread(target=self.read_meter,daemon=True).start()
        
    def read_meter(self):
        while True:
            print("------------------ MCU ----------------")
            print("self.current_L1",self.current_L1)
            print("self.current_L2",self.current_L2)
            print("self.current_L3",self.current_L3)
            print("self.voltage_L1",self.voltage_L1)
            print("self.voltage_L2",self.voltage_L2)
            print("self.voltage_L3",self.voltage_L3)
            print("self.power",self.power)
            print("self.energy",self.energy)
            time.sleep(1)

    def write(self):
        # counter = 0
        while True:
            try:
                if len(self.send_data_list)>0:
                    self.serial.write(self.send_data_list[0])
                    # print("Gönderilen",self.send_data_list[0],"counter:",counter)
                    # counter +=1
                    self.send_data_list.pop(0)
            except Exception as e:
                print(datetime.now(),"write Exception:",e)
            time.sleep(0.1)

    def calculate_checksum(self,data):
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
        time.sleep(10)
        while True:
            self.parameter_data = "001"
            self.connector_id = "1"
            data = self.get_command + self.pid_control_pilot + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            # print("Send get_command_PID_control_pilot -->", send_data)
            self.send_data_list.append(send_data)
            time.sleep(1)

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
        self.parameter_data = "001"
        self.connector_id = "1"
        data = self.get_command + self.pid_proximity_pilot + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("Send get_command_pid_proximity_pilot -->", send_data)
        self.send_data_list.append(send_data)
            
    def set_command_pid_cp_pwm(self,max_current):
        '''
        Control Pilot PWM sinyalini set edebilmek(kontrol etmek) için aşağıdaki paket gönderilir
        '''
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
        print("Send set_command_pid_cp_pwm -->", send_data)
        self.send_data_list.append(send_data)
        
    def get_command_pid_cp_pwm(self):
        self.parameter_data = "001"
        self.connector_id = "1"
        data = self.get_command + self.pid_cp_pwm_control + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send get_command_pid_cp_pwm -->", send_data)
        self.send_data_list.append(send_data)
        
    def set_command_pid_relay_control(self,relay:Relay):
        '''
        Röleyi kontrol etmek için (‘1’ veya ‘0’) paket gönderilir.
        A durumunda gönderilmez. B yada C durumunda olmalı
        '''
        self.parameter_data = "002"
        data = self.set_command + self.pid_relay_control + self.parameter_data + self.connector_id + relay.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("Send set_command_pid_relay_control",send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_relay_control(self):
        '''
        Rölenin 1 yada 0 olduğunu döner.
        '''
        self.parameter_data = "001"
        data = self.get_command + self.pid_relay_control + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send get_command_pid_relay",send_data)
        self.send_data_list.append(send_data)

    def set_command_pid_led_control(self,led_state:LedState):
        self.parameter_data = "002"
        data = self.set_command + self.pid_led_control + self.parameter_data + self.connector_id + led_state.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("************************* led_state -->", led_state)
        self.send_data_list.append(send_data)
        if led_state != LedState.RfidVerified and led_state != LedState.RfidFailed:
            # print("********** önceki led setlendi",self.led_state)
            self.led_state = led_state
        else:
            time.sleep(2)
            self.parameter_data = "002"
            data = self.set_command + self.pid_led_control + self.parameter_data + self.connector_id + self.led_state.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            print("1 sn sonra set_command_pid_led_control -->", self.led_state)
            self.send_data_list.append(send_data)

    def get_command_pid_led_control(self):
        self.parameter_data = "001"
        data = self.get_command + self.pid_led_control + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("Send get_command_pid_led_control -->", send_data)
        self.send_data_list.append(send_data)

    def set_command_pid_locker_control(self,locker_state:LockerState):
        '''
        Soketli tip Şarj Cihazlarında soket içerisindeki kilit mekanizmasının kontrolü 
        '''
        self.parameter_data = "002"
        data = self.set_command + self.pid_locker_control + self.parameter_data + self.connector_id + locker_state.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("Send set_command_pid_locker_control -->", send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_locker_control(self): 
        '''
        Soketli tip Şarj Cihazlarında soket içerisindeki kilit mekanizmasının kontrolü 
        '''
        self.parameter_data = "001"
        data = self.get_command + self.pid_locker_control + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send get_command_pid_locker_control -->", send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_current(self):
        self.parameter_data = "001"
        data = self.get_command + self.pid_current + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send get_command_pid_current -->", send_data)
        self.send_data_list.append(send_data)
        
    def get_command_pid_voltage(self):
        self.parameter_data = "001"
        data = self.get_command + self.pid_voltage + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send get_command_pid_voltage -->", send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_power(self,power_type:PowerType):
        self.parameter_data = "002"
        data = self.get_command + self.pid_power + self.parameter_data + self.connector_id + power_type.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send get_command_pid_power -->", send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_energy(self,energy_type:EnergyType):
        self.parameter_data = "002"
        data = self.get_command + self.pid_energy + self.parameter_data + self.connector_id + energy_type.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send get_command_pid_energy -->", send_data)
        self.send_data_list.append(send_data)

    def set_command_pid_rfid(self):
        '''
        Yeni bir okuma işleminden önce Linux tarafından MCU Board’a bir kez SET komutu gönderilerek, hafızasındaki UniqID ‘nin silinmesi talep edilir
        '''
        self.parameter_data = "002"
        data = self.set_command + self.pid_rfid + self.parameter_data + self.connector_id + "R"
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        # print("Send set_command_pid_rfid -->", send_data)
        self.send_data_list.append(send_data)
        
    def get_command_pid_rfid(self):
        time.sleep(10)
        while True:
            self.parameter_data = "001"
            data = self.get_command + self.pid_rfid + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            # print("Send get_command_pid_rfid -->", send_data)
            self.send_data_list.append(send_data)
            time.sleep(0.5)
            
    def get_command_pid_evse_temp(self):
        time.sleep(10)
        while True:
            self.parameter_data = "002"
            data = self.get_command + self.pid_evse_temp + self.parameter_data + self.connector_id + "R"
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            # print("Send get_command_pid_evse_temp -->", send_data)
            self.send_data_list.append(send_data)
            time.sleep(15)
            
    def get_command_pid_error_list_init(self):
        time.sleep(15)
        # print("Başlangıçta error durumu kontrol ediliyor..")
        # print("pid_error_list",self.error_list)
        if len(self.error_list)>0:
            for value in self.error_list:
                if value == PidErrorList.LockerInitializeError:
                    # print("LockerInitializeError")
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.LockerError,), daemon= True).start()
                elif value == PidErrorList.RcdInitializeError:
                    # print("RcdInitializeError")
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RcdError,), daemon= True).start()
            
    def get_command_pid_error_list(self):
        time.sleep(10)
        while True:
            self.parameter_data = "001"
            data = self.get_command + self.pid_error_list + self.parameter_data + self.connector_id
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            self.send_data_list.append(send_data)
            time.sleep(1)
        

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
        if data[2] == self.pid_control_pilot:
            self.application.ev.control_pilot = data[7]
            # print("self.application.ev.control_pilot------>",self.application.ev.control_pilot)
            
    def get_response_pid_proximity_pilot(self,data):
        if data[2] == self.pid_proximity_pilot:
            self.application.ev.proximity_pilot = data[7]
            print("self.application.ev.proximity_pilot------>",self.application.ev.proximity_pilot)
      
    def set_response_pid_cp_pwm(self,data):
        if data[2] == self.pid_cp_pwm_control:
            digit_100 = int(data[7]) * 100
            digit_10 = int(data[8]) * 10
            digit_1 = int(data[9])
            digit_01 = int(data[10]) / 10
            
            original_number = digit_100 + digit_10 + digit_1 + digit_01
            pid_cp_pwm = int(original_number) if original_number.is_integer() else original_number
            # print("pid_cp_pwm------>",pid_cp_pwm)
    
    def get_response_pid_cp_pwm(self,data):
        if data[2] == self.pid_cp_pwm_control:
            digit_100 = int(data[7]) * 100
            digit_10 = int(data[8]) * 10
            digit_1 = int(data[9])
            digit_01 = int(data[10]) / 10
            
            original_number = digit_100 + digit_10 + digit_1 + digit_01
            self.application.ev.pid_cp_pwm = int(original_number) if original_number.is_integer() else original_number
            # print("self.application.ev.pid_cp_pwm------>",self.application.ev.pid_cp_pwm)
            
    def set_response_pid_relay_control(self,data):
        if data[2] == self.pid_relay_control:
            result = data[7]
            print("set_response_pid_relay_control------>",result)

    def get_response_pid_relay_control(self,data):
        if data[2] == self.pid_relay_control:
            self.application.ev.pid_relay_control = bool(int(data[7]))
            print("self.application.ev.pid_relay_control------>",self.application.ev.pid_relay_control)

    def set_response_pid_led_control(self,data):
        if data[2] == self.pid_led_control:
            result = data[7]
            # if result == LedState.StandBy.value:
            #     print("set_response_pid_led_control --> ",LedState.StandBy.name)
            # elif result == LedState.Connecting.value:
            #     print("set_response_pid_led_control --> ",LedState.Connecting.name)
            # elif result == LedState.RfidVerified.value:
            #     print("set_response_pid_led_control --> ",LedState.RfidVerified.name)
            # elif result == LedState.Charging.value:
            #     print("set_response_pid_led_control --> ",LedState.Charging.name)
            # elif result == LedState.RfidFailed.value:
            #     print("set_response_pid_led_control --> ",LedState.RfidFailed.name)
            # elif result == LedState.NeedReplugging.value:
            #     print("set_response_pid_led_control --> ",LedState.NeedReplugging.name)
            # elif result == LedState.Fault.value:
            #     print("set_response_pid_led_control --> ",LedState.Fault.name)
            # elif result == LedState.ChargingStopped.value:
            #     print("set_response_pid_led_control --> ",LedState.ChargingStopped.name)

    def get_response_pid_led_control(self,data):
        if data[2] == self.pid_led_control:
            self.application.ev.pid_led_control = data[7]
            result = data[7]
            # if result == LedState.StandBy.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.StandBy.name)
            # elif result == LedState.Connecting.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.Connecting.name)
            # elif result == LedState.RfidVerified.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.RfidVerified.name)
            # elif result == LedState.Charging.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.Charging.name)
            # elif result == LedState.RfidFailed.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.RfidFailed.name)
            # elif result == LedState.NeedReplugging.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.NeedReplugging.name)
            # elif result == LedState.Fault.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.Fault.name)
            # elif result == LedState.ChargingStopped.value:
            #     print("self.application.ev.pid_led_control --> ",LedState.ChargingStopped.name)

    def set_response_pid_locker_control(self,data):
        if data[2] == self.pid_locker_control:
            result = data[7]
            if result == LockerState.Lock.value:
                print("set_response_pid_locker_control",LockerState.Lock.name)
            elif result == LockerState.Unlock.value:
                print("set_response_pid_locker_control",LockerState.Unlock.name)

    def get_response_pid_locker_control(self,data):
        if data[2] == self.pid_locker_control:
            self.application.ev.pid_locker_control = data[7]
            result = data[7]
            # if result == LockerState.Lock.value:
            #     print("self.application.ev.pid_locker_control-->",LockerState.Lock.name)
            # elif result == LockerState.Unlock.value:
            #     print("self.application.ev.pid_locker_control-->",LockerState.Unlock.name)

    def get_response_pid_current(self,data):
        if data[2] == self.pid_current:
            self.current_L1 = round(int(data[8])*100 + int(data[9])*10 + int(data[10])*1 + int(data[11])*0.1 + int(data[12])*0.01 + int(data[13])*0.001 , 3)
            self.current_L2 = round(int(data[15])*100 + int(data[16])*10 + int(data[17])*1 + int(data[18])*0.1 + int(data[19])*0.01 + int(data[20])*0.001 , 3)
            self.current_L3 = round(int(data[22])*100 + int(data[23])*10 + int(data[24])*1 + int(data[25])*0.1 + int(data[26])*0.01 + int(data[27])*0.001 , 3)

            
    def get_response_pid_voltage(self,data):
        if data[2] == self.pid_voltage:
            self.voltage_L1 = round(int(data[8])*1000 + int(data[9])*100 + int(data[10])*10 + int(data[11])*1 + int(data[12])*0.1 + int(data[13])*0.01 , 3)
            self.voltage_L2 = round(int(data[15])*1000 + int(data[16])*100 + int(data[17])*10 + int(data[18])*1 + int(data[19])*0.1 + int(data[20])*0.01 , 3)
            self.voltage_L3 = round(int(data[22])*1000 + int(data[23])*100 + int(data[24])*10 + int(data[25])*1 + int(data[26])*0.1 + int(data[27])*0.01 , 3)
            
    def get_response_pid_power(self,data):
        if data[2] == self.pid_power:
            self.power = round(int(data[8])*100 + int(data[9])*10 + int(data[10])*1 + int(data[11])*0.1 + int(data[12])*0.01 + int(data[13])*0.001 , 3)

    def get_response_pid_energy(self,data):
        if data[2] == self.pid_energy:
            self.energy = round(int(data[8])*1000000 + int(data[9])*100000 + int(data[10])*10000 + int(data[11])*1000 + int(data[12])*100 + int(data[13])*10 + int(data[14])*1 + int(data[15])*0.1 + int(data[16])*0.01 + int(data[17])*0.001 , 3)

    def set_response_pid_rfid(self,data):
        if data[2] == self.pid_rfid:
            result = data[7]
            # print("Rfid Reset -->",result)
            
    def get_response_pid_rfid(self,data):
        if data[2] == self.pid_rfid:
            card_id = ""
            card_id_length = int(data[7] + data[8])
            if card_id_length > 0:
                for i in range(9,9+card_id_length):
                    card_id += data[i]
            if card_id != "":
                self.application.ev.card_id = card_id
                print(card_id)
                self.set_command_pid_rfid()
                
    def get_response_pid_evse_temp(self,data):
        if data[2] == self.pid_evse_temp:
            temp_sign = data[8]
            temp = round(int(data[9])*100 + int(data[10])*10 + int(data[11])*1 + int(data[12])*0.1 , 1)
            self.application.ev.temperature = temp_sign + str(temp)
            # print("temp:", self.application.ev.temperature)
            
    def get_response_pid_error_list(self,data):
        error_list = []
        if data[2] == self.pid_error_list:
            # print("data:", data)
            if (int(data[7]) == 1):
                error_list.append(PidErrorList.LockerInitializeError)
                self.application.change_status_notification(ChargePointErrorCode.connector_lock_failure,ChargePointStatus.faulted)
            if (int(data[8]) == 1):
                error_list.append(PidErrorList.EVCommunicationPortError)
                self.application.change_status_notification(ChargePointErrorCode.evCommunicationError,ChargePointStatus.faulted)
            if (int(data[9]) == 1):
                error_list.append(PidErrorList.EarthDisconnectFailure)
                self.application.change_status_notification(ChargePointErrorCode.ground_failure,ChargePointStatus.faulted)
            if (int(data[10]) == 1):
                error_list.append(PidErrorList.RcdInitializeError)
                self.application.change_status_notification(ChargePointErrorCode.ground_failure,ChargePointStatus.faulted)
            if (int(data[11]) == 1):
                error_list.append(PidErrorList.RcdTripError)
                self.application.change_status_notification(ChargePointErrorCode.ground_failure,ChargePointStatus.faulted)
            if (int(data[12]) == 1):
                error_list.append(PidErrorList.HighTemperatureFailure)
                self.application.change_status_notification(ChargePointErrorCode.highTemperature,ChargePointStatus.faulted)
            if (int(data[13]) == 1):
                error_list.append(PidErrorList.OverCurrentFailure)
                self.application.change_status_notification(ChargePointErrorCode.overCurrentFailure,ChargePointStatus.faulted)
            if (int(data[14]) == 1):
                error_list.append(PidErrorList.OverVoltageFailure)
                self.application.change_status_notification(ChargePointErrorCode.overVoltage,ChargePointStatus.faulted)
            if (int(data[15]) == 1):
                error_list.append(PidErrorList.InternalEnergyMeterFailure)
                self.application.change_status_notification(ChargePointErrorCode.power_meter_failure,ChargePointStatus.faulted)
            if (int(data[16]) == 1):
                error_list.append(PidErrorList.PowerSwitchFailure)
                self.application.change_status_notification(ChargePointErrorCode.power_switch_failure,ChargePointStatus.faulted)
            if (int(data[17]) == 1):
                error_list.append(PidErrorList.RFIDReaderFailure)
                self.application.change_status_notification(ChargePointErrorCode.readerFailure,ChargePointStatus.faulted)
            if (int(data[18]) == 1):
                error_list.append(PidErrorList.UnderVoltageFailure)
                self.application.change_status_notification(ChargePointErrorCode.underVoltage,ChargePointStatus.faulted)
            if (int(data[19]) == 1):
                error_list.append(PidErrorList.FrequencyFailure)
                self.application.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.faulted)
            if (int(data[20]) == 1):
                error_list.append(PidErrorList.PhaseSequenceFailure)
                self.application.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.faulted)
            if (int(data[21]) == 1):
                error_list.append(PidErrorList.OverPowerFailure)
                self.application.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.faulted)
            if len(error_list) > 0:
                print(" $$$$$$$$$$$$$$$$ self.error_list",self.error_list)

            if error_list != self.error_list:
                if len(error_list) > 0:
                    for error in error_list:
                        self.application.testWebSocket.send_error(error.value)
                else:
                    self.application.testWebSocket.send_error("")
            
            self.error_list = error_list
            # print("self.error_list get_response_pid_error_list",self.error_list)

    def read(self):
        # counter = 0
        while True:
            try:
                incoming = self.serial.readline()
                incoming = incoming.decode('utf-8')
                if len(incoming) > 0:
                    # print("incoming data",incoming,"counter:", counter)
                    # counter +=1
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
                    elif incoming[1] == self.set_response:
                        self.set_response_pid_cp_pwm(incoming)
                        self.set_response_pid_relay_control(incoming)
                        self.set_response_pid_led_control(incoming)
                        self.set_response_pid_locker_control(incoming)
                        self.set_response_pid_rfid(incoming)
            except Exception as e:
                print(datetime.now(),"read Exception:",e)
            time.sleep(0.1)
            
# 04E2D04A0074801
# 0485A54A0074801
            


		
