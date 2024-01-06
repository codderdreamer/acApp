import time
from src.enums import *

class Process():
    def __init__(self,application) -> None:
        self.application = application
        
    def connected(self):
        print("******************************************************************connected")
        time.sleep(2)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.get_command_pid_proximity_pilot()
            time.sleep(0.5)
            print("********************************************************************self.application.ev.proximity_pilot_current",self.application.ev.proximity_pilot_current)
        
    def run(self):
        pass