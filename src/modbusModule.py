import minimalmodbus
import serial
import time
from threading import Thread

class ModbusModule:
    def __init__(self,application, port, slave_address, baudrate=9600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8):
        print("*********** Modbus Bağlantı port:",port,"slave_address:",slave_address, "baudrate:",baudrate)
        self.application = application
        self.instrument = minimalmodbus.Instrument(port, slave_address)
        self.instrument.serial.baudrate = baudrate
        self.instrument.serial.parity = parity
        self.instrument.serial.stopbits = stopbits
        self.instrument.serial.bytesize = bytesize
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.serial.timeout = 1 
        
        self.voltage_L1 = None
        self.voltage_L2 = None
        self.voltage_L3 = None
        self.current_L1 = None
        self.current_L2 = None
        self.current_L3 = None
        self.power = None
        self.energy = None
        
        self.__connection = False
        self.firstEnergy = None
        
        Thread(target=self.read_all_data,daemon=True).start()
        
    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, value):
        if self.__connection != value:
            self.__connection = value
            if value == True:
                self.application.testWebSocket.send_mid_meter_state(True)
                self.firstEnergy = round(self.read_input_float(register_address=73)/1000,2)
       

    def read_float(self, register_address, number_of_registers=2, byteorder=0):
        return self.instrument.read_float(register_address, functioncode=4, number_of_registers=number_of_registers, byteorder=byteorder)

    def write_float(self, register_address, value, number_of_registers=2, byteorder=0):
        self.instrument.write_float(register_address, value, functioncode=16, number_of_registers=number_of_registers, byteorder=byteorder)

    def read_input_float(self, register_address):
        adjusted_address = register_address - 1
        float_val = self.read_float(adjusted_address, number_of_registers=2)
        return round(float_val,2)
    
    def read_all_data(self):
        while True:
            try:
                self.voltage_L1 = self.read_input_float(register_address=1)
                self.voltage_L2 = self.read_input_float(register_address=3)
                self.voltage_L3 = self.read_input_float(register_address=5)
                self.current_L1 = self.read_input_float(register_address=7)
                self.current_L2 = self.read_input_float(register_address=9)
                self.current_L3 = self.read_input_float(register_address=11)
                self.power = round(self.read_input_float(register_address=53)/1000,2)
                self.energy = round(self.read_input_float(register_address=73)/1000,2)
                
                # print("-----------MID METER-----------------")
                # print("MID METER self.volt_l1",self.volt_l1)
                # print("MID METER self.volt_l2",self.volt_l2)
                # print("MID METER self.volt_l3",self.volt_l3)
                # print("MID METER self.current_l1",self.current_l1)
                # print("MID METER self.current_l2",self.current_l2)
                # print("MID METER self.current_l3",self.current_l3)
                # print("MID METER self.power",self.power)
                # print("MID METER self.energy",self.energy)
                self.connection = True
            except Exception as e:
                # print("Mid meter HATA:",e)
                self.connection = False
                pass
            time.sleep(1)

    
    

        

    


    
    
    
    