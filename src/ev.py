from src.enums import *

class EV():
    def __init__(self):
        self.control_pilot = ControlPlot.stateF.value
        self.current_L1 = None
        self.current_L2 = None
        self.current_L3 = None
        self.power = None
        

        