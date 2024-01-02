from src.enums import *

class EV():
    def __init__(self):
        self.control_pilot = ControlPlot.stateF.value  # A,B,C,D,E veya F değerini almaktadır
        self.proximity_pilot = None
        self.pid_relay_control = None
        self.pid_led_control = None
        self.current_L1 = None
        self.current_L2 = None
        self.current_L3 = None
        self.power = None
        self.energy = None
        

        