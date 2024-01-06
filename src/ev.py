from src.enums import *

class EV():
    def __init__(self):
        self.control_pilot = ControlPlot.stateF.value   # A,B,C,D,E, F 
        self.__proximity_pilot = None                     # ProximityPilot  : N, E, 1, 2, 3, 6
        self.proximity_pilot_current = None
        
        self.pid_cp_pwm = None                          # float
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

        