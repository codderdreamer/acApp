import minimalmodbus
import serial
import time
from threading import Thread
from src.logger import ac_app_logger as logger
from src.enums import *

class ModbusModule:
    def __init__(self, application, port, slave_address, baudrate=9600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8):
        print(f"Mid meter Modbus ayarlanıyor... port:{port}, slave_address:{slave_address}, baudrate:{baudrate}")
        self.port = port
        self.slave_address = slave_address
        self.baudrate = baudrate

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
        
        Thread(target=self.read_all_data, daemon=True).start()

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, value):
        if self.__connection != value:
            if value == True:
                print(Color.Blue.value,"Mid Meter Bağlandı")
                self.application.testWebSocket.send_mid_meter_state(True)
                self.firstEnergy = self.read_input_float(register_address=73)
        self.__connection = value

    def read_float(self, register_address, number_of_registers=2, byteorder=0):
        return self.instrument.read_float(register_address, functioncode=4, number_of_registers=number_of_registers, byteorder=byteorder)
        

    def write_float(self, register_address, value, number_of_registers=2, byteorder=0):
        self.instrument.write_float(register_address, value, functioncode=16, number_of_registers=number_of_registers, byteorder=byteorder)

    def read_input_float(self, register_address):
        adjusted_address = register_address - 1
        float_val = self.read_float(adjusted_address, number_of_registers=2)
        return round(float_val,2)
            
    
    def read_all_data(self):
        counter = 0
        while True:
            try:
                self.voltage_L1 = self.read_input_float(register_address=1)
                self.voltage_L2 = self.read_input_float(register_address=3)
                self.voltage_L3 = self.read_input_float(register_address=5)
                self.current_L1 = self.read_input_float(register_address=7)
                self.current_L2 = self.read_input_float(register_address=9)
                self.current_L3 = self.read_input_float(register_address=11)
                self.power = round(self.read_input_float(register_address=53)/1000,2)
                self.energy = self.read_input_float(register_address=73)
                counter = 0
                # print("-----------MID METER-----------------")
                # print("MID METER self.volt_l1",self.volt_l1)
                # print("MID METER self.volt_l2",self.volt_l2)
                # print("MID METER self.volt_l3",self.volt_l3)
                # print("MID METER self.current_l1",self.current_l1)
                # print("MID METER self.current_l2",self.current_l2)
                # print("MID METER self.current_l3",self.current_l3)
                # print("MID METER self.power",self.power)
                print("MID METER ********************* energy",self.read_input_float(register_address=73))
                print("MID METER self.energy",self.energy)
                print("MID METER self.firstEnergy",self.firstEnergy)
                self.connection = True
            except Exception as e:
                counter += 1
                if counter > 10:
                    self.connection = False
                    counter = 0
                pass
            time.sleep(0.5)
