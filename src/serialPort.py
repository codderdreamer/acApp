import serial
import time
from threading import Thread
from src.enums import *

# GET_COMMAND 	    :   "G" 	Bilgisayar tarafından bir verinin okunması için gönderilecektir.
# GET_RESPONSE	    :   "g"	    MCU  tarafından, ilgili veri cevap olarak gönderilecektir.
# SET_COMMAND	    :   "S"	    Bilgisayar tarafından bir verinin değiştirilmesi için gönderilecektir.
# SET_RESPONSE		:   "s"	    (decimal 115)

class SerialPort():
    def __init__(self,application) -> None:
        self.application = application
        self.serial = serial.Serial("/dev/ttyS2",115200 ,timeout=1)
        print("Serial connection...")
        self.send_data_list = []

        self.stx = b'\x02'
        self.lf = b'\n'

        self.get_command = 'G'
        self.get_response = 'g'
        self.set_command = 'S'
        self.set_response = 's'

        self.control_pilot = "C"
        self.pid_relay_control = "R"
        self.pid_led_control = "L"
        self.pid_locker_control = "K"
        self.pid_current = "I"

        self.parameter_data = "001"
        self.connector_id = "1"

        Thread(target=self.read,daemon=True).start()
        Thread(target=self.write,daemon=True).start()

        self.seri_port_test()
        
        

    def seri_port_test(self):
        self.get_command_pid_current()

        # self.set_command_pid_locker_control(LockerState.Lock)
        # time.sleep(1)
        # self.get_command_pid_locker_control()

        # Thread(target=self.get_command_PID_control_pilot,daemon=True).start()

        #  ************* Relay Test ***************
        # self.set_command_pid_relay_control(Relay.On)
        # time.sleep(5)
        # self.get_command_pid_relay()
        # time.sleep(5)
        # self.set_command_pid_relay_control(Relay.Off)
        # time.sleep(5)
        # self.get_command_pid_relay()

        # self.set_command_pid_led_control(LedState.NeedReplugging)

        # self.get_command_pid_led_control()

        pass


    def write(self):
        while True:
            try:
                if len(self.send_data_list)>0:
                    # start_time = time.time()
                    self.serial.write(self.send_data_list[0])
                    # finish_time = time.time()
                    # print(finish_time-start_time)
                    self.send_data_list.pop(0)
            except Exception as e:
                print("serial port write exception:",e)
            time.sleep(0.3)

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
        while True:
            self.parameter_data = "001"
            self.connector_id = "1"
            data = self.get_command + self.control_pilot + self.parameter_data + self.connector_id
            
            checksum = self.calculate_checksum(data)

            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
            print("send data",send_data)
            self.send_data_list.append(send_data)
            time.sleep(5)

    def set_command_pid_relay_control(self,relay:Relay):
        self.parameter_data = "002"
        data = self.set_command + self.pid_relay_control + self.parameter_data + self.connector_id + relay.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_relay(self):
        self.parameter_data = "001"
        data = self.get_command + self.pid_relay_control + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)

    def set_command_pid_led_control(self,led_state):
        self.parameter_data = "002"
        data = self.set_command + self.pid_led_control + self.parameter_data + self.connector_id + led_state.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_led_control(self):
        self.parameter_data = "001"
        data = self.get_command + self.pid_led_control + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)

    def set_command_pid_locker_control(self,locker_state):
        self.parameter_data = "002"
        data = self.set_command + self.pid_locker_control + self.parameter_data + self.connector_id + locker_state.value
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_locker_control(self): 
         # bunun cevabı dönmüyor bakılacak, pid locker control L yazıyor get için
        self.parameter_data = "001"
        data = self.get_command + self.pid_locker_control + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)

    def get_command_pid_current(self):
        self.parameter_data = "001"
        data = self.get_command + self.pid_current + self.parameter_data + self.connector_id
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)




    #   ************************ RESPONSE  *****************************************************

    def get_response_control_pilot(self,data):
        if data[2] == self.control_pilot:
            self.application.ev.control_pilot = data[7]
            print("self.application.ev.control_pilot------>",self.application.ev.control_pilot)

    def set_response_ralay_control(self,data):
        if data[2] == self.pid_relay_control:
            result = data[7]
            print("pid response result",result)

    def get_response_pid_relay(self,data):
        if data[2] == self.pid_relay_control:
            result = data[7]
            if result == Relay.On.value:
                print("Röle Açık")
            else:
                print("Röle kapalı")

    def set_response_pid_led_control(self,data):
        if data[2] == self.pid_led_control:
            result = data[7]
            if result == LedState.StandBy.value:
                print(LedState.StandBy.name)
            elif result == LedState.Connecting.value:
                print(LedState.Connecting.name)
            elif result == LedState.RfidVerified.value:
                print(LedState.RfidVerified.name)
            elif result == LedState.Charging.value:
                print(LedState.Charging.name)
            elif result == LedState.RfidFailed.value:
                print(LedState.RfidFailed.name)
            elif result == LedState.NeedReplugging.value:
                print(LedState.NeedReplugging.name)
            elif result == LedState.Fault.value:
                print(LedState.Fault.name)
            elif result == LedState.ChargingStopped.value:
                print(LedState.ChargingStopped.name)

    def get_response_pid_led_control(self,data):
        if data[2] == self.pid_led_control:
            result = data[7]
            if result == LedState.StandBy.value:
                print(LedState.StandBy.name)
            elif result == LedState.Connecting.value:
                print(LedState.Connecting.name)
            elif result == LedState.RfidVerified.value:
                print(LedState.RfidVerified.name)
            elif result == LedState.Charging.value:
                print(LedState.Charging.name)
            elif result == LedState.RfidFailed.value:
                print(LedState.RfidFailed.name)
            elif result == LedState.NeedReplugging.value:
                print(LedState.NeedReplugging.name)
            elif result == LedState.Fault.value:
                print(LedState.Fault.name)
            elif result == LedState.ChargingStopped.value:
                print(LedState.ChargingStopped.name)

    def set_response_pid_locker_control(self,data):
        if data[2] == self.pid_locker_control:
            result = data[7]
            if result == LockerState.Lock.value:
                print(LockerState.Lock.name)
            elif result == LockerState.Unlock.value:
                print(LockerState.Unlock.name)

    def get_response_pid_locker_control(self,data):
        if data[2] == self.pid_locker_control:
            result = data[7]
            if result == LockerState.Lock.value:
                print(LockerState.Lock.name)
            elif result == LockerState.Unlock.value:
                print(LockerState.Unlock.name)

    def get_response_pid_current(self,data):
        current_L1 = data[8] + data[9] + data[10] + data[11] + data[12] + data[13]
        self.application.ev.current_L1 = int(current_L1)/1000
        print("current_L1",self.application.ev.current_L1)
        current_L2 = data[15] + data[16] + data[17] + data[18] + data[19] + data[20]
        self.application.ev.current_L2 = int(current_L2)/1000
        print("current_L2",self.application.ev.current_L2)
        current_L3 = data[22] + data[23] + data[24] + data[25] + data[26] + data[27]
        self.application.ev.current_L3 = int(current_L3)/1000
        print("current_L3",self.application.ev.current_L3)



    def read(self):
        while True:
            try:
                incoming = self.serial.readline()
                incoming = incoming.decode('utf-8')
                if len(incoming) > 0:
                    print("incoming data",incoming)
                    incoming = list(incoming)
                    if incoming[1] == self.get_response:
                        self.get_response_control_pilot(incoming)
                        self.get_response_pid_relay(incoming)
                        self.get_response_pid_led_control(incoming)
                        self.get_response_pid_current(incoming)
                    elif incoming[1] == self.set_response:
                        self.set_response_ralay_control(incoming)
                        self.set_response_pid_led_control(incoming)
                        self.set_response_pid_locker_control(incoming)
                    


            except Exception as e:
                print(e)
            time.sleep(1)


		
