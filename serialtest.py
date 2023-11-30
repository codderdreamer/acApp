import serial
import time
from threading import Thread

# GET_COMMAND 	    :   "G" 	Bilgisayar tarafından bir verinin okunması için gönderilecektir.
# GET_RESPONSE	    :   "g"	    MCU  tarafından, ilgili veri cevap olarak gönderilecektir.
# SET_COMMAND	    :   "S"	    Bilgisayar tarafından bir verinin değiştirilmesi için gönderilecektir.
# SET_RESPONSE		:   "s"	    (decimal 115)

class SerialPort():
    def __init__(self) -> None:
        self.serial = serial.Serial("/dev/ttyS2",115200 ,timeout=1)
        print("Serial connection...")
        self.stx = b'\x02'
        self.lf = b'\n'

        self.get_command = 'G'
        self.get_response = 'g'
        self.set_command = 'S'
        self.set_response = 's'

        self.control_pilot = "C"

        self.parameter_data = ""
        self.connector_id = "1"

        Thread(target=self.read,daemon=True).start()

    def calculate_checksum(self,data):
        checksum = 2
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
        self.control_pilot = "C"
        self.parameter_data = "001"
        self.connector_id = "1"
        data = self.get_command + self.control_pilot + self.parameter_data + self.connector_id
        
        checksum = self.calculate_checksum(data)

        send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf
        print("send data",send_data)
        self.serial.write(send_data)
    

    def get_response_control_pilot(self,data):



    def read(self):
        while True:
            try:
                incoming = self.serial.readline()
                print("incoming data",incoming)
                incoming = incoming.decode('utf-8')
                if len(incoming) > 0:
                    print("incoming",incoming)
                    incoming = incoming.split()
                    if incoming[0] == self.get_response:
                        self.
                        if incoming[1] == self.control_pilot:
                            self.set_control_pilot()
                    
                    elif incoming[0] == self.set_response:
                        pass

            except Exception as e:
                print(e)
            time.sleep(1)

SerialPort().get_command_PID_control_pilot()

while True:
    time.sleep(1)

# b'\x02gC0021A176\n'

		
