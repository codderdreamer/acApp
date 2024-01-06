import time
from src.enums import *

class Process():
    def __init__(self,application) -> None:
        self.application = application
        
    def connected(self):
        print("****************************************************************** connected")
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
            
    def waiting_auth(self):
        print("****************************************************************** waiting_auth")
        pass
    
    def waiting_state_c(self):
        print("****************************************************************** waiting_state_c")
        time.sleep(1)
        if self.application.control_C_B:
            self.application.serialPort.set_command_pid_relay_control(Relay.Off)
            return
        if self.application.deviceState != DeviceState.WAITING_STATE_C:
            return
        self.application.serialPort.set_command_pid_relay_control(Relay.On)
        time_start = time.time()
        while True:
            if self.application.ev.control_pilot == ControlPlot.stateB.value:
                if time.time() - time_start > 60*5:
                    self.application.deviceState = DeviceState.STOPPED_BY_EVSE
                    break
            elif self.application.ev.control_pilot == ControlPlot.stateC.value:  # Adan Cye geçen için
                self.application.deviceState = DeviceState.CHARGING
                break
            else:
                break
            time.sleep(0.3)
        
            
            
    def charging(self):
        print("****************************************************************** charging")
        if self.application.control_A_B_C != True:                               # Adan Cye geçen için
            self.application.deviceState = DeviceState.CONNECTED
            return
        
        
        
        
        
    def fault(self):
        print("****************************************************************** fault")
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        
    def stopped_by_evse(self):
        print("****************************************************************** stopped_by_evse")
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
            
    def idle(self):
        print("****************************************************************** idle")
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
            
    def stopped_by_user(self):
        print("****************************************************************** stopped_by_user")
        self.application.serialPort.set_command_pid_cp_pwm(0)
        time.sleep(0.3)
        self.application.serialPort.set_command_pid_relay_control(Relay.Off)
        time.sleep(4)
        if self.application.socketType == SocketType.Type2:
            self.application.serialPort.set_command_pid_locker_control(LockerState.Unlock)
        
        
        