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
                return 
                 
        if self.application.cardType == CardType.LocalPnC:
            if self.application.socketType == SocketType.Type2:
                self.application.serialPort.set_command_pid_locker_control(LockerState.Lock)
                time_start = time.time()
                while True:
                    self.application.serialPort.get_command_pid_locker_control()
                    time.sleep(0.3)
                    print("self.application.ev.pid_locker_control",self.application.ev.pid_locker_control)
                    if self.application.ev.pid_locker_control == LockerState.Lock.value:
                        self.application.serialPort.set_command_pid_cp_pwm(self.application.ev.proximity_pilot_current)
                        self.application.deviceState = DeviceState.WAITING_STATE_C
                        break
                    else:
                        print("Hata Lock Connector Çalışmadı !!!")
                    if time.time() - time_start > 10:
                        self.application.deviceState = DeviceState.FAULT
                        break
            elif self.application.socketType == SocketType.TetheredType:
                self.application.serialPort.set_command_pid_cp_pwm(self.application.max_current)
                self.application.deviceState = DeviceState.WAITING_STATE_C
            
        elif self.application.cardType == CardType.BillingCard:
            self.application.deviceState = DeviceState.WAITING_AUTH
        
        elif self.application.cardType == CardType.StartStopCard:
            self.application.deviceState = DeviceState.WAITING_AUTH
            
            
    
    def run(self):
        pass