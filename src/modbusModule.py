import minimalmodbus
import serial
import time
from threading import Thread

class ModbusModule:
    def __init__(self, port, slave_address, baudrate=9600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8):
        self.instrument = minimalmodbus.Instrument(port, slave_address)
        self.instrument.serial.baudrate = baudrate
        self.instrument.serial.parity = parity
        self.instrument.serial.stopbits = stopbits
        self.instrument.serial.bytesize = bytesize
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.serial.timeout = 1 
        
        self.volt_l1 = None
        self.volt_l2 = None
        self.volt_l3 = None
        self.current_l1 = None
        self.current_l2 = None
        self.current_l3 = None
        self.power = None
        self.total_energy_import = None
        self.total_energy_export = None
        self.current_demand = None
        
        Thread(target=self.read_all_data,daemon=True).start()

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
                self.volt_l1 = self.read_input_float(register_address=1)
                self.volt_l2 = self.read_input_float(register_address=3)
                self.volt_l3 = self.read_input_float(register_address=5)
                self.current_l1 = self.read_input_float(register_address=7)
                self.current_l2 = self.read_input_float(register_address=9)
                self.current_l3 = self.read_input_float(register_address=11)
                self.power = round(self.read_input_float(register_address=13)/1000,2)
                self.total_energy_import = round(self.read_input_float(register_address=73)/1000,2)
                self.total_energy_export = round(self.read_input_float(register_address=75)/1000,2)
                self.current_demand = self.read_input_float(register_address=259)
            except Exception as e:
                print(e)
            time.sleep(3)

    
    

        

    


    
    
    
    