import minimalmodbus
import serial
import time
from threading import Thread
from src.logger import ac_app_logger as logger

class ModbusModule:
    def __init__(self, application, port, slave_address, baudrate=9600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8):
        print("Initializing Modbus connection on port: %s, slave_address: %s, baudrate: %s", port, slave_address, baudrate)
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
        print("Started read_all_data thread")

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, value):
        if self.__connection != value:
            self.__connection = value
            if value:
                print("Modbus connection established")
                self.application.testWebSocket.send_mid_meter_state(True)
                first_energy = self.read_input_float(register_address=73)
                self.firstEnergy = round(first_energy / 1000, 2) if first_energy is not None else None
            else:
                print("Modbus connection lost")

    def read_float(self, register_address, number_of_registers=2, byteorder=0):
        try:
            result = self.instrument.read_float(register_address, functioncode=4, number_of_registers=number_of_registers, byteorder=byteorder)
            print("Read float from register %s: %s", register_address, result)
            return result
        except minimalmodbus.NoResponseError:
            print("No response from instrument at register %s", register_address)
            return None
        except Exception as e:
            print("Exception in read_float: %s", e)
            return None

    def write_float(self, register_address, value, number_of_registers=2, byteorder=0):
        try:
            self.instrument.write_float(register_address, value, functioncode=16, number_of_registers=number_of_registers, byteorder=byteorder)
            print("Wrote float to register %s: %s", register_address, value)
        except minimalmodbus.NoResponseError:
            print("No response from instrument when writing to register %s", register_address)
        except Exception as e:
            print("Exception in write_float: %s", e)

    def read_input_float(self, register_address):
        adjusted_address = register_address - 1
        try:
            float_val = self.read_float(adjusted_address, number_of_registers=2)
            if float_val is not None:
                result = round(float_val, 2)
                print("Read input float from register %s: %s", register_address, result)
                return result
            else:
                print("Failed to read input float from register %s", register_address)
                return None
        except Exception as e:
            print("Exception in read_input_float: %s", e)
            return None
    
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
                
                power_reading = self.read_input_float(register_address=53)
                self.power = round(power_reading / 1000, 2) if power_reading is not None else None
                
                energy_reading = self.read_input_float(register_address=73)
                self.energy = round(energy_reading / 1000, 2) if energy_reading is not None else None
                
                counter = 0
                print("Read all data: Voltage L1: %s, L2: %s, L3: %s; Current L1: %s, L2: %s, L3: %s; Power: %s, Energy: %s",
                            self.voltage_L1, self.voltage_L2, self.voltage_L3,
                            self.current_L1, self.current_L2, self.current_L3,
                            self.power, self.energy)
                self.connection = True
            except Exception as e:
                counter += 1
                if counter > 10:
                    self.connection = False
                    counter = 0
                pass
            time.sleep(0.5)
