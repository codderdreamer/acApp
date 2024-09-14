from src.enums import *
from threading import Thread
from ocpp.v16.enums import *
import time

class DeviceStateModule():
    def __init__(self,application) -> None:
        self.application = application
        self.__cardType : CardType = None
        self.__led_state : LedState = None
        self.__deviceState : DeviceState = None

        self.__control_pilot : ControlPlot = None                       # MCU'dan okunan değer
        self.__proximity_plot : ProximityPilot = None                   # MCU'dan okunan değer
        self.__proximity_pilot_current : int = None                     # MCU'dan okunan değer
        self.__pid_cp_pwm = None                                        # MCU'dan okunan değer
        self.__relay : Relay = None                                     # MCU'dan okunan değer
        self.__led_control : LedState = None                            # MCU'dan okunan değer

    @property
    def cardType(self):
        return self.__cardType

    @cardType.setter
    def cardType(self, value):
        if self.__cardType != value:
            print(Color.Yellow.value, "Card Type:", value)
            self.__cardType = value

    @property
    def deviceState(self):
        return self.__deviceState

    @deviceState.setter
    def deviceState(self, value):
        if self.__deviceState != value:
            print(Color.Yellow.value, "Device State:", value)
            self.__deviceState = value

    @property
    def led_state(self):
        return self.__led_state

    @led_state.setter
    def led_state(self, value):
        if self.__led_state != value:
            print(Color.Macenta.value, "Led State:", value)
            self.__led_state = value

    @property
    def pid_cp_pwm(self):
        return self.__pid_cp_pwm

    @pid_cp_pwm.setter
    def pid_cp_pwm(self, value):
        if self.__pid_cp_pwm != value:
            print(Color.Yellow.value, "MCU Readed PID CP PWM:", value)
            self.__pid_cp_pwm = value

    @property
    def proximity_plot(self):
        return self.__proximity_plot

    @proximity_plot.setter
    def proximity_plot(self, value):
        if self.__proximity_plot != value:
            print(Color.Yellow.value, "MCU Readed Proximity Plot:", value)
            self.__proximity_plot = value

    @property
    def proximity_pilot_current(self):
        return self.__proximity_pilot_current

    @proximity_pilot_current.setter
    def proximity_pilot_current(self, value):
        if self.__proximity_pilot_current != value:
            print(Color.Yellow.value, "MCU Readed Proximity Plot Current:", value)
            self.__proximity_pilot_current = value

    @property
    def control_pilot(self):
        return self.__control_pilot

    @control_pilot.setter
    def control_pilot(self, value):
        if self.__control_pilot != value:
            print(Color.Yellow.value, "MCU Readed Control Pilot:", value)
            self.__control_pilot = value

    @property
    def relay(self):
        return self.__relay

    @relay.setter
    def relay(self, value):
        if self.__relay != value:
            print(Color.Yellow.value, "MCU Readed Relay:", value)
            self.__relay = value

    @property
    def led_control(self):
        return self.__led_control

    @led_control.setter
    def led_control(self, value):
        if self.__led_control != value:
            print(Color.Yellow.value, "MCU Readed Led Control:", value)
            self.__led_control = value
            







