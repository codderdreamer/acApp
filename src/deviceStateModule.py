from src.enums import *
from threading import Thread
from ocpp.v16.enums import *
import time

class DeviceStateModule():
    def __init__(self,application) -> None:
        self.application = application
        self.__cardType : CardType = None
        self.__led_state : LedState = None

    @property
    def cardType(self):
        return self.__cardType

    @cardType.setter
    def cardType(self, value):
        if self.__cardType != value:
            print(Color.Yellow.value, "CardType:", value)

    @property
    def led_state(self):
        return self.__led_state

    @led_state.setter
    def led_state(self, value):
        if self.__led_state != value:
            print(Color.Macenta.value, "Led State:", value)
            self.__led_state = value
            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(value,),daemon=True).start()

    def led_state_thread(self):
        rcd_error = False
        while True:
            if self.application.ev.is_there_rcd_error():
                self.led_state = LedState.RcdError
                rcd_error = True
                print("L1")
            elif rcd_error:
                self.led_state = LedState.RcdError
                print("L2")
            elif self.application.ev.is_there_locker_initialize_error():
                self.led_state = LedState.LockerError
                print("L3")
            elif self.application.process.charge_try_counter > 3:
                self.led_state = LedState.NeedReplugging
                print("L4")
            elif self.application.ev.is_there_other_error():
                self.led_state = LedState.Fault
                print("L5")
            elif self.application.chargePointStatus == ChargePointStatus.faulted and self.application.process.charge_try_counter > 3:
                self.led_state = LedState.NeedReplugging
                print("L6")
            elif self.application.chargePointStatus == ChargePointStatus.faulted and len(self.application.serialPort.error_list) > 0:
                self.led_state = LedState.Fault
                print("L7")
            elif self.application.chargePointStatus == ChargePointStatus.faulted and self.application.process.charge_try_counter != 0:
                self.led_state = LedState.Fault
                print("L8")
            elif self.application.chargePointStatus == ChargePointStatus.faulted and self.application.process.locker_error:
                self.led_state = LedState.LockerError
                print("L9")
            elif self.application.chargePointStatus == ChargePointStatus.faulted and self.application.ev.proximity_pilot_current == 0:
                self.led_state = LedState.Fault
                print("L10")
            elif self.application.deviceState == DeviceState.OFFLINE:
                self.led_state = LedState.DeviceOffline
                print("L11")
            elif self.application.process.try_charge:
                self.led_state = LedState.Fault
                print("L12")
            elif self.application.chargePointStatus == ChargePointStatus.faulted and (self.application.ev.control_pilot == ControlPlot.stateB.value or self.application.ev.control_pilot == ControlPlot.stateC.value):
                self.led_state = LedState.NeedReplugging
                print("L13")
            elif self.application.chargePointStatus == ChargePointStatus.faulted:
                self.led_state = LedState.Fault
                print("L14")
            elif self.application.chargePointStatus == ChargePointStatus.suspended_evse:
                self.led_state = LedState.Fault
                print("L15")
            elif self.application.availability == AvailabilityType.inoperative and self.application.ev.charge == False:
                self.led_state = LedState.DeviceInoperative
                print("L16")
            elif self.application.process.rfid_verified == True:
                self.led_state = LedState.RfidVerified
                self.application.process.rfid_verified = None
                print("L18")
            elif self.application.process.rfid_verified == False:
                self.led_state = LedState.RfidFailed
                self.application.process.rfid_verified = None
                print("L19")
            elif self.application.deviceState == DeviceState.SUSPENDED_EV or self.application.deviceState == DeviceState.STOPPED_BY_EVSE or self.application.deviceState == DeviceState.STOPPED_BY_USER:
                self.led_state = LedState.ChargingStopped
                print("L20")
            elif (self.application.chargePointStatus == ChargePointStatus.preparing or self.application.chargePointStatus == ChargePointStatus.reserved) and self.application.ev.control_pilot == ControlPlot.stateA.value:
                self.led_state = LedState.WaitingPluging
                print("L21")
            elif (self.application.ev.start_stop_authorize) and self.application.ev.control_pilot == ControlPlot.stateA.value:
                self.led_state = LedState.WaitingPluging
                print("L22")
            elif self.application.chargePointStatus == ChargePointStatus.available and self.application.ev.control_pilot == ControlPlot.stateA.value:
                self.led_state = LedState.StandBy
                print("L23")
            elif self.application.chargePointStatus == ChargePointStatus.preparing and self.application.ev.control_pilot == ControlPlot.stateB.value:
                self.led_state = LedState.Connecting
                print("L24")
            elif self.application.chargePointStatus == ChargePointStatus.preparing and self.application.ev.control_pilot == ControlPlot.stateC.value:
                self.led_state = LedState.Connecting
                print("L25")
            elif self.application.chargePointStatus == ChargePointStatus.charging:
                self.led_state = LedState.Charging
                print("L26")
            elif (self.application.ev.control_pilot == ControlPlot.stateA.value) and (self.application.deviceStateModule.cardType == CardType.LocalPnC or self.application.deviceStateModule.cardType == CardType.StartStopCard):
                self.led_state = LedState.StandBy
                print("L27")

            if self.application.ev.control_pilot == ControlPlot.stateA.value:
                rcd_error = False

            time.sleep(1)