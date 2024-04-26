
from src.modbusModule import ModbusModule
from src.enums import *

class MidMeterModule():
    def __init__(self,application) -> None:
        from src.application import Application
        self.application : Application = application
        self.application.write_log("MidMeterModule Init Start",Color.Blue)
        self.start_mid_meter()
        self.application.write_log("MidMeterModule Init Finish",Color.Blue)
        
    def start_mid_meter(self):
        if self.application.settings.deviceSettings.mid_meter:
            print("Default Mid Meter var.")
            self.midMeter = ModbusModule(port='/dev/ttyS5', slave_address=self.application.settings.deviceSettings.midMeterSlaveAddress)
        else:
            print("Harici Mid Meter var.")
            self.midMeter = ModbusModule(port='/dev/ttyS5', slave_address=self.application.settings.deviceSettings.externalMidMeterSlaveAddress)