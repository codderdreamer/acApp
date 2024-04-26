
from src.modbusModule import ModbusModule

class MidMeterModule():
    def __init__(self,application) -> None:
        print("MidMeterModule Init Start")
        from src.application import Application
        self.application : Application = application
        self.start_mid_meter()
        print("MidMeterModule Init Finish")
        
    def start_mid_meter(self):
        if self.application.settings.deviceSettings.mid_meter:
            print("Default Mid Meter var.")
            self.midMeter = ModbusModule(port='/dev/ttyS5', slave_address=self.application.settings.deviceSettings.midMeterSlaveAddress)
        else:
            print("Harici Mid Meter var.")
            self.midMeter = ModbusModule(port='/dev/ttyS5', slave_address=self.application.settings.deviceSettings.externalMidMeterSlaveAddress)