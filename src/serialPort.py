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
        self.pid_relay_control = "S"

        self.parameter_data = "001"
        self.connector_id = "1"

        Thread(target=self.read,daemon=True).start()
        Thread(target=self.write,daemon=True).start()
        Thread(target=self.get_command_PID_control_pilot,daemon=True).start()

        #  ************* Relay Test ***************
        self.set_command_pid_relay_control(Relay.On.value)
        time.sleep(3)
        self.set_command_pid_relay_control(Relay.Off.value)

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

    def set_command_pid_relay_control(self,relay:str):
        self.parameter_data = "001"
        data = self.set_command + self.pid_relay_control + self.parameter_data + self.connector_id + relay
        checksum = self.calculate_checksum(data)
        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.send_data_list.append(send_data)

    

    def get_response_control_pilot(self,data):
        if data[2] == self.control_pilot:
            self.application.ev.control_pilot = data[7]
            print("self.application.ev.control_pilot------>",self.application.ev.control_pilot)


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
                    
                    elif incoming[0] == self.set_response:
                        pass

            except Exception as e:
                print(e)
            time.sleep(1)


		
