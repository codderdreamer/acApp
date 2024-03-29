
from enum import IntEnum,Enum

class OcppVersion(Enum):
    ocpp16 = "ocpp1.6"
    ocpp20 = "ocpp2.0"
    ocpp21 = "ocpp2.0.1"

class ControlPlot(Enum):
    stateA = "A"
    '''State A : Not Connected'''
    stateB = "B"
    '''State B : EV connected, ready to charge'''
    stateC = "C"
    '''State C : EV charging'''
    stateD = "D"
    '''State D : EV charging, ventilation required'''
    stateE = "E"
    '''State E : Error'''
    stateF = "F"
    '''State F : Unknown error'''
    
class DeviceState(Enum):
    IDLE = "IDLE"
    CONNECTED = "CONNECTED"
    WAITING_AUTH = "WAITING_AUTH"
    WAITING_STATE_C = "WAITING_STATE_C"
    CHARGING = "CHARGING"
    STOPPED_BY_EVSE = "STOPPED_BY_EVSE"
    STOPPED_BY_USER = "STOPPED_BY_USER"
    FAULT = "FAULT"
    
class SocketType(Enum):
    Type2 = "Type2"
    '''Soketli Tip; Proximity Pilot aktif, Kendi üzerinde şarj kablosu olmayan Soketli Tip (Type 2) AC Şarj cihazlarında 
    kullanıcı, şarj işlemi için kendi kablosunu kullanmaktadır. Kullanılan kablolardaki iletkenin kalınlığına 
    göre bu kablonun akım taşıma kapasitesi 13A, 20A, 32A ve 63A olarak değişiklik göstermektedir.'''
    TetheredType = "TetheredType"
    '''Kablolu tip; şarj cihazlarında Proximity Pilot ucu aktif değildir ve kullanılmamaktadır.
    Max akım set edilir.'''
    
    
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
    WaitingPluging = ";"

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
    
class CardType(Enum):
    StartStopCard = "StartStopCard"
    '''
    This is the local start and stop card allows that allows charging station to be used without 
    being connected to the platform
    '''
    LocalPnC = "LocalPnC"
    '''
    Plug and Charge
    '''
    BillingCard = "BillingCard"
    '''
    This is the authentication card that charging station needs to be connected to the platform,
    and the UID of RFID card needs to be entered into the platform before swipping card for use.
    '''

class SSLEnable(Enum):
    Enable = "Enable"
    Disable = "Disable"



