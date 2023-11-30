
from enum import IntEnum,Enum

class OcppVersion(Enum):
    ocpp16 = "ocpp1.6"
    ocpp20 = "ocpp2.0"
    ocpp21 = "ocpp2.0.1"

class ControlPlot(Enum):
    stateA = "A"
    stateB = "B"
    stateC = "C"
    stateD = "D"
    stateE = "E"
    stateF = "F"
