from src.enums import *
from threading import Thread
import time

class EV():
    def __init__(self,application):
        self.application = application
        
        self.__control_pilot = None             # A,B,C,D,E, F 
        self.__proximity_pilot = None           # ProximityPilot  : N, E, 1, 2, 3, 6
        self.proximity_pilot_current = None
        
        self.pid_cp_pwm = None                  # float
        self.pid_relay_control = None
        self.pid_led_control = None
        self.pid_locker_control = None
        
        self.current_L1 = None
        self.current_L2 = None
        self.current_L3 = None
        
        self.voltage_L1 = None
        self.voltage_L2 = None
        self.voltage_L3 = None
        
        self.power = None
        self.energy = None
        
        self.start_date = None
        self.duration = None
        self.__charge = False
        
        self.card_id = None
        
        self.send_message_thread_start = False
        
    def send_message(self):
        self.send_message_thread_start = True
        while self.send_message_thread_start:
            try:
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_charging())
            except Exception as e:
                print("send_message",e)
            time.sleep(3)
        
    @property
    def proximity_pilot(self):
        return self.__proximity_pilot

    @proximity_pilot.setter
    def proximity_pilot(self, value):
        self.__proximity_pilot = value
        
        if self.__proximity_pilot == ProximityPilot.CableNotPlugged.value:
            self.proximity_pilot_current = 0
        elif self.__proximity_pilot == ProximityPilot.Error.value:
            self.proximity_pilot_current = 0
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger13Amper.value:
            self.proximity_pilot_current = 13
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger20Amper.value:
            self.proximity_pilot_current = 20
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger32Amper.value:
            self.proximity_pilot_current = 32
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger63Amper.value:
            self.proximity_pilot_current = 63
        print(self.proximity_pilot_current)
        
    @property
    def control_pilot(self):
        return self.__control_pilot

    @control_pilot.setter
    def control_pilot(self, value):
        if self.__control_pilot != value:
            self.__control_pilot = value
            if self.__control_pilot == ControlPlot.stateA.value:
                self.application.deviceState = DeviceState.IDLE
            elif self.__control_pilot == ControlPlot.stateB.value:
                self.application.deviceState = DeviceState.CONNECTED
            elif self.__control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING
            elif (self.__control_pilot == ControlPlot.stateD.value) or (self.__control_pilot == ControlPlot.stateE.value) or (self.__control_pilot == ControlPlot.stateF.value):
                self.application.deviceState = DeviceState.FAULT
            else:
                self.application.deviceState = DeviceState.FAULT
                
    @property
    def charge(self):
        return self.__charge

    @charge.setter
    def charge(self, value):
        if value:
            Thread(target=self.send_message,daemon=True).start()
        else:
            self.send_message_thread_start = False
            self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_charging())
        self.__charge = value
        
        
        