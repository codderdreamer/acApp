
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

class Relay(Enum):
    On = "1"
    Off = "0"

class LedState(Enum):
    StandBy = "1"
    Connecting = "2"
    RfidVerified = "3"
    Charging = "4"
    RfidFailed = "5"
    NeedReplugging = "6"
    Fault = "7"
    ChargingStopped = "8"

