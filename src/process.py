import time
from src.enums import *

class Process():
    def __init__(self,application) -> None:
        self.application = application
        
    def connected(self):
        print("******************************************************************connected")
        time.sleep(1)
        if self.application.deviceState != DeviceState.CONNECTED:
            return
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.get_command_pid_proximity_pilot()
            time.sleep(0.5)
            if self.application.ev.proximity_pilot_current == 0:
                self.application.deviceState = DeviceState.FAULT
                print("self.application.deviceState = DeviceState.FAULT")
            else:
                self.application.serialPort.set_command_pid_cp_pwm(self.application.ev.proximity_pilot_current)
    
    
    def run(self):
        pass