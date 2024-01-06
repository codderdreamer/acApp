
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
    
class ProximityPilot(Enum):
    CableNotPlugged = "N"
    Error = "E"
    CablePluggedIntoCharger13Amper = "1"
    CablePluggedIntoCharger20Amper = "2"
    CablePluggedIntoCharger32Amper = "3"
    CablePluggedIntoCharger63Amper = "6"

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

class LockerState(Enum):
    Lock = "1"
    Unlock = "0"

class PowerType(Enum):
    kw = "P"        # kw        AKTİF GÜÇ       (şuan sadece bu var)
    kVAR = "R"      # kVAR      REAKTİF GÜÇ  
    kVA = "S"       # kVA       GÖRÜNÜR GÜÇ

class EnergyType(Enum):
    kwh = "P"        # kw        Şuan sadece bu var
    kVARh = "R"      # kVAR
    kVAh = "S"       # kVA




