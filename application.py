import asyncio
import sys
asyncio.current_task = asyncio.Task.current_task
import websockets
from src.chargePoint16 import ChargePoint16
from threading import Thread
from src.enums import *
import time
from src.ev import EV
from src.serialPort import SerialPort
from src.settings import Settings
from src.databaseModule import DatabaseModule
from src.softwareSettings import SoftwareSettings
from src.websocketServer import WebSocketServer
from src.bluetoothService.bluetoothService import BluetoothService
from src.process import Process
from ocpp.v16.enums import *
from datetime import datetime
from src.modbusModule import ModbusModule
from src.flaskModule import FlaskModuleThread
from src.testServer import TestServer
import subprocess
import os
from src.webSocket import *
import builtins
from src.logger import ac_app_logger as logger
import ssl
import base64
from src.utils import Utils
from src.deviceStateModule import DeviceStateModule

file = open("/root/output.txt", "a")

original_print = builtins.print
def timestamped_print(color = "",*args, **kwargs):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args = (f"[{current_time}]",) + (color,) + args + ("\033[0m",)
    original_print(*args, **kwargs)
    # file.write(" ".join(map(str, args)) + "\n")
builtins.print = timestamped_print

class Application():
    def __init__(self, loop):
        print(Color.Yellow.value, "------------------------------------------------- Application Run Started ------------------------------------------------")
        self.utils : Utils = None
        self.settings : Settings = None
        self.databaseModule : DatabaseModule = None
        self.bluetoothService : BluetoothService = None
        self.softwareSettings : SoftwareSettings = None
        self.flaskModule : FlaskModuleThread = None
        self.webSocketServer : WebSocketServer = None
        self.process : Process = None
        self.ev : EV = None
        self.serialPort : SerialPort = None
        self.modbusModule : ModbusModule = None
        self.deviceStateModule : DeviceStateModule = None

    def run(self):
        self.set_application()
        self.databaseModule.read_all_tables()
        self.softwareSettings.set_functions_enable()

    def set_application(self):
        self.settings.application = self
        self.databaseModule.application = self
        self.bluetoothService.application = self
        self.softwareSettings.application = self
        self.flaskModule.application = self
        self.webSocketServer.application = self
        self.process.application = self
        self.ev.application = self
        self.serialPort.application = self
        self.modbusModule.application = self
        self.deviceStateModule.application = self

        


        # self.initilly = True
        # self.test_led = False
        # self.test_charge = False
        # self.logger = logger
        # self.loop = loop
        # self.charge_stopped = False
        # self.chargePoint = None
        # self.request_list = []
        # self.model = None
        # self.masterCard = None
        # self.availability = AvailabilityType.operative
        # self.bluetooth_error = None
        # self.__chargePointStatus = None
        # self.info = None
        # self.__error_code = None
        # self.__deviceState = None
        # self.__led_state = None
        # self.ocppActive = False
        # self.cardType: CardType = None
        # self.socketType = SocketType.Type2
        # self.max_current = 32
        # self.control_A_B_C = False
        # self.control_C_B = False
        # self.control_A_C = False
        # self.meter_values_on = False
        # self.settings = Settings(self)
        # self.databaseModule = DatabaseModule(self)
        # self.settings.configuration.load_configuration_from_db()
        # self.bluetoothService = BluetoothService(self)
        # self.id_tag_list = self.databaseModule.get_default_local_list()
        # self.softwareSettings = SoftwareSettings(self,logger)
        # self.flaskModule = FlaskModuleThread(self).start()
        # self.webSocketServer = WebSocketServer(self,logger)
        # self.process = Process(self)
        # self.ev = EV(self)
        # self.ocpp_subprotocols = OcppVersion.ocpp16
        # self.serialPort = SerialPort(self,logger)
        # if self.settings.deviceSettings.externalMidMeter == True:
        #     self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.externalMidMeterSlaveAddress)
        # elif self.settings.deviceSettings.mid_meter == True:
        #     self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.midMeterSlaveAddress)
        # Thread(target=self.read_charge_values_thred, daemon=True).start()
        # Thread(target=self.control_output,daemon=True).start()
        # Thread(target=self.led_state_thread,daemon=True).start()
        # self.deviceState = DeviceState.IDLE
        # self.chargePointStatus = ChargePointStatus.available

        # self.deviceStateModule = DeviceStateModule(self)

    def led_state_thread(self):
        rcd_error = False
        while True:
            if self.ev.is_there_rcd_error():
                self.led_state = LedState.RcdError
                rcd_error = True
                print("L1")
            elif rcd_error:
                self.led_state = LedState.RcdError
                print("L2")
            elif self.ev.is_there_locker_initialize_error():
                self.led_state = LedState.LockerError
                print("L3")
            elif self.process.charge_try_counter > 3:
                self.led_state = LedState.NeedReplugging
                print("L4")
            elif self.ev.is_there_other_error():
                self.led_state = LedState.Fault
                print("L5")
            elif self.chargePointStatus == ChargePointStatus.faulted and self.process.charge_try_counter > 3:
                self.led_state = LedState.NeedReplugging
                print("L6")
            elif self.chargePointStatus == ChargePointStatus.faulted and len(self.serialPort.error_list) > 0:
                self.led_state = LedState.Fault
                print("L7")
            elif self.chargePointStatus == ChargePointStatus.faulted and self.process.charge_try_counter != 0:
                self.led_state = LedState.Fault
                print("L8")
            elif self.chargePointStatus == ChargePointStatus.faulted and self.process.locker_error:
                self.led_state = LedState.LockerError
                print("L9")
            elif self.chargePointStatus == ChargePointStatus.faulted and self.ev.proximity_pilot_current == 0:
                self.led_state = LedState.Fault
                print("L10")
            elif self.deviceState == DeviceState.OFFLINE:
                self.led_state = LedState.DeviceOffline
                print("L11")
            elif self.process.try_charge:
                self.led_state = LedState.Fault
                print("L12")
            elif self.chargePointStatus == ChargePointStatus.faulted and (self.ev.control_pilot == ControlPlot.stateB.value or self.ev.control_pilot == ControlPlot.stateC.value):
                self.led_state = LedState.NeedReplugging
                print("L13")
            elif self.chargePointStatus == ChargePointStatus.faulted:
                self.led_state = LedState.Fault
                print("L14")
            elif self.chargePointStatus == ChargePointStatus.suspended_evse:
                self.led_state = LedState.Fault
                print("L15")
            elif self.availability == AvailabilityType.inoperative and self.ev.charge == False:
                self.led_state = LedState.DeviceInoperative
                print("L16")
            elif self.process.rfid_verified == True:
                self.led_state = LedState.RfidVerified
                self.process.rfid_verified = None
                print("L18")
            elif self.process.rfid_verified == False:
                self.led_state = LedState.RfidFailed
                self.process.rfid_verified = None
                print("L19")
            elif self.deviceState == DeviceState.SUSPENDED_EV or self.deviceState == DeviceState.STOPPED_BY_EVSE or self.deviceState == DeviceState.STOPPED_BY_USER:
                self.led_state = LedState.ChargingStopped
                print("L20")
            elif (self.chargePointStatus == ChargePointStatus.preparing or self.chargePointStatus == ChargePointStatus.reserved) and self.ev.control_pilot == ControlPlot.stateA.value:
                self.led_state = LedState.WaitingPluging
                print("L21")
            elif (self.ev.start_stop_authorize) and self.ev.control_pilot == ControlPlot.stateA.value:
                self.led_state = LedState.WaitingPluging
                print("L22")
            elif self.chargePointStatus == ChargePointStatus.available and self.ev.control_pilot == ControlPlot.stateA.value:
                self.led_state = LedState.StandBy
                print("L23")
            elif self.chargePointStatus == ChargePointStatus.preparing and self.ev.control_pilot == ControlPlot.stateB.value:
                self.led_state = LedState.Connecting
                print("L24")
            elif self.chargePointStatus == ChargePointStatus.preparing and self.ev.control_pilot == ControlPlot.stateC.value:
                self.led_state = LedState.Connecting
                print("L25")
            elif self.chargePointStatus == ChargePointStatus.charging:
                self.led_state = LedState.Charging
                print("L26")
            elif (self.ev.control_pilot == ControlPlot.stateA.value) and (self.cardType == CardType.LocalPnC or self.cardType == CardType.StartStopCard):
                self.led_state = LedState.StandBy
                print("L27")

            if self.ev.control_pilot == ControlPlot.stateA.value:
                rcd_error = False

            time.sleep(1)


    @property
    def led_state(self):
        return self.__led_state

    @led_state.setter
    def led_state(self, value):
        if self.__led_state != value:
            print(Color.Macenta.value, "Led State:", value)
            self.__led_state = value
            Thread(target=self.serialPort.set_command_pid_led_control, args=(value,),daemon=True).start()


    def control_output(self):
        while True:
            try:
                file_size = os.path.getsize("/root/output.txt")
                print("file size:",file_size)
                one_mb = 1024*1024
                if file_size >= one_mb*30:
                    os.system("rm -r /root/output.txt")
            except Exception as e:
                print("control_output Exception:",e)
            time.sleep(60*10)

    @property
    def chargePointStatus(self):
        return self.__chargePointStatus

    @chargePointStatus.setter
    def chargePointStatus(self, value):
        if self.__chargePointStatus != value:
            print(Color.Macenta.value, "Charge Point Status:", value)
            self.__chargePointStatus = value

    @property
    def error_code(self):
        return self.__error_code

    @error_code.setter
    def error_code(self, value):
        if self.__error_code != value:
            print(Color.Macenta.value, "Error Code:", value)
            self.__error_code = value
        
    @property
    def deviceState(self):
        return self.__deviceState

    @deviceState.setter
    def deviceState(self, value):
        if self.__deviceState != value:
            if self.process.waiting_auth_value:
                if value == DeviceState.CONNECTED or value == DeviceState.SUSPENDED_EV or value == DeviceState.CHARGING:
                    print("1")
                    return
            if value == DeviceState.WAITING_STATE_C:
                if self.ev.control_pilot == ControlPlot.stateC.value:
                    print("2")
                    return
            if self.process.rcd_trip_error or self.process.locker_initialize_error:
                if value == DeviceState.IDLE:
                    pass
                elif value == DeviceState.FAULT:
                    pass
                else:
                    print("3")
                    return
            if self.process.charge_try_counter > 3:
                if value == DeviceState.IDLE:
                    pass
                elif value == DeviceState.FAULT:
                    pass
                else:
                    print("4")
                    return
            if self.process.wait_fault:
                if value == DeviceState.IDLE:
                    pass
                elif value == DeviceState.FAULT:
                    pass
                else:
                    print("5")
                    return
                
            if self.__deviceState == DeviceState.STOPPED_BY_USER:
                if value == DeviceState.IDLE:
                    pass
                else:
                    print("6")
                    return
                
            if self.process.locker_error:
                if value == DeviceState.IDLE:
                    pass
                elif value == DeviceState.FAULT:
                    pass
                else:
                    print("7")
                    return
                
            if self.process.try_charge:
                if value == DeviceState.SUSPENDED_EVSE:
                    pass
                elif value == DeviceState.IDLE:
                    pass
                else:
                    print("8")
                    return



            print(Color.Cyan.value, "Device State:", value)
            self.__deviceState = value
            if self.__deviceState == DeviceState.CONNECTED:
                if self.charge_stopped != True:
                    Thread(target=self.process.connected,daemon=True).start()
    
            elif self.__deviceState == DeviceState.WAITING_AUTH:
                if self.charge_stopped != True:
                    Thread(target=self.process.waiting_auth,daemon=True).start()
            
            elif self.__deviceState == DeviceState.WAITING_STATE_C:
                if self.charge_stopped != True:
                    Thread(target=self.process.waiting_state_c,daemon=True).start()
                
            elif self.__deviceState == DeviceState.CHARGING:
                if self.charge_stopped != True:
                    Thread(target=self.process.charging,daemon=True).start()

            elif self.__deviceState == DeviceState.FAULT:
                Thread(target=self.process.fault,daemon=True).start()

            elif self.__deviceState == DeviceState.IDLE:
                self.charge_stopped = False
                Thread(target=self.process.idle,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_EVSE:
                self.charge_stopped = True
                Thread(target=self.process.stopped_by_evse,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_USER:
                self.charge_stopped = True
                Thread(target=self.process.stopped_by_user,daemon=True).start()
                
            elif self.__deviceState == DeviceState.SUSPENDED_EVSE:
                Thread(target=self.process.suspended_evse,daemon=True).start()

            elif self.__deviceState == DeviceState.SUSPENDED_EV:
                Thread(target=self.process.suspended_ev,daemon=True).start()
            
            elif self.__deviceState == DeviceState.OFFLINE:
                pass
                
    def change_status_notification(self, error_code : ChargePointErrorCode, status : ChargePointStatus, info:str = None):
        if error_code != self.error_code or status != self.chargePointStatus:
            self.error_code = error_code
            self.chargePointStatus = status
            self.info = info
            print("Error info:",self.info)
            if self.ocppActive:
                asyncio.run_coroutine_threadsafe(self.chargePoint.send_status_notification(connector_id=1,error_code=self.error_code,status=self.chargePointStatus,info=self.info),self.loop)
    
    def ocpp_control(self):
        while True:
            try:
                time_start = None
                if self.cardType == CardType.BillingCard:
                    
                    ip_address = self.settings.ocppSettings.domainName
                        
                    response = subprocess.run(
                        ['ping', '-c 1', ip_address],
                        stdout=subprocess.PIPE,  
                        stderr=subprocess.PIPE, 
                        universal_newlines=True
                    )
                    # Eğer ping başarılı ise '0' döner
                    if response.returncode == 0:
                        time_start = time.time()
                    else:
                        if time_start == None or time.time() - time_start > 10:
                            self.ocppActive = False
            
            except Exception as e:
                print("ocpp_control Exception:", e)
            time.sleep(3)
        
    def read_charge_values_thred(self):
        while True:
            try:

                # print("-------------CHARGE VALUES------------")
                if (self.settings.deviceSettings.mid_meter == True or self.settings.deviceSettings.externalMidMeter == True) and self.modbusModule.connection == True:
                    # print("Veriler MID'den alınıyor...")
                    self.ev.current_L1 = self.modbusModule.current_L1
                    self.ev.current_L2 = self.modbusModule.current_L2
                    self.ev.current_L3 = self.modbusModule.current_L3
                    self.ev.voltage_L1 = self.modbusModule.voltage_L1
                    self.ev.voltage_L2 = self.modbusModule.voltage_L2
                    self.ev.voltage_L3 = self.modbusModule.voltage_L3
                    self.ev.energy = round((self.modbusModule.energy - self.modbusModule.firstEnergy),3)
                    self.ev.power =  self.modbusModule.power
                elif (self.settings.deviceSettings.mid_meter == False and self.settings.deviceSettings.externalMidMeter == False):
                    # print("Veriler MCU'dan alınıyor...")
                    self.ev.current_L1 = self.serialPort.current_L1
                    self.ev.current_L2 = self.serialPort.current_L2
                    self.ev.current_L3 = self.serialPort.current_L3
                    self.ev.voltage_L1 = self.serialPort.voltage_L1
                    self.ev.voltage_L2 = self.serialPort.voltage_L2
                    self.ev.voltage_L3 = self.serialPort.voltage_L3
                    self.ev.energy = round(self.serialPort.energy,2)
                    self.ev.power =  self.serialPort.power
                else:
                    self.ev.current_L1 = 0
                    self.ev.current_L2 = 0
                    self.ev.current_L3 = 0
                    self.ev.voltage_L1 = 0
                    self.ev.voltage_L2 = 0
                    self.ev.voltage_L3 = 0
                    self.ev.energy = 0
                    self.ev.power =  0
                    
                # print("self.ev.current_L1",self.ev.current_L1)
                # print("self.ev.current_L2",self.ev.current_L2)
                # print("self.ev.current_L3",self.ev.current_L3)
                # print("self.ev.voltage_L1",self.ev.voltage_L1)
                # print("self.ev.voltage_L2",self.ev.voltage_L2)
                # print("self.ev.voltage_L3",self.ev.voltage_L3)
                # print("self.ev.energy",self.ev.energy)
                # print("self.ev.power",self.ev.power)
                time.sleep(1)
                
            except Exception as e:
                print("read_charge_values_thred",e)



    async def ocppStart(self):
        try:
            self.ocppActive = False
            if self.cardType == CardType.BillingCard:
                if self.settings.ocppSettings.sslEnable == SSLEnable.Disable.value:
                    ws = "ws://"
                elif self.settings.ocppSettings.sslEnable == SSLEnable.Enable.value:
                    ws = "wss://"
                
                if self.settings.ocppSettings.port != None and self.settings.ocppSettings.port != "" and self.settings.ocppSettings.port != "80":
                    ocpp_url = ws + self.settings.ocppSettings.domainName + ":" + self.settings.ocppSettings.port + self.settings.ocppSettings.path + self.settings.ocppSettings.chargePointId
                else:
                    ocpp_url = ws + self.settings.ocppSettings.domainName + self.settings.ocppSettings.path + self.settings.ocppSettings.chargePointId
                    
                print(Color.Green.value,"Ocpp URL:",ocpp_url)

                ssl_context = None
                certs_dir = '/etc/acApp/certs'
                cert_file_path = os.path.join(certs_dir, "local_certificate.pem")

                if os.path.exists(cert_file_path) and self.settings.ocppSettings.certFileName:
                    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    ssl_context.load_verify_locations(cert_file_path)
                    ssl_context.load_cert_chain(certfile=cert_file_path)
                    print("Using verified SSL with certificate:", cert_file_path)
                else:
                    print("Using SSL without certificate")

                auth_header = None
                if self.settings.ocppSettings.authorizationKey:
                    auth_header = {'Authorization': f'Basic {base64.b64encode(f"{self.settings.ocppSettings.chargePointId}:{self.settings.ocppSettings.authorizationKey}".encode()).decode()}'}

                # Ping interval value; 0 disables client-side ping/pong
                ping_interval = float(self.settings.configuration.WebSocketPingInterval) if self.settings.configuration.WebSocketPingInterval else None

                async with websockets.connect(
                    ocpp_url, 
                    subprotocols=[self.ocpp_subprotocols.value], 
                    ssl=ssl_context, 
                    extra_headers=auth_header, 
                    compression=None, 
                    timeout=10,
                    ping_interval=ping_interval  # Ping interval added here
                ) as ws:
                    print("Ocpp'ye bağlanmaya çalışıyor...")
                    if self.ocpp_subprotocols == OcppVersion.ocpp16:
                        self.chargePoint = ChargePoint16(self, self.settings.ocppSettings.chargePointId, ws, self.loop)
                        future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                        await self.chargePoint.send_boot_notification(self.settings.ocppSettings.chargePointId, self.settings.ocppSettings.chargePointId)
        
        except Exception as e:
            print("ocppStart Exception:", e)
            self.ocppActive = False
 
    def ocpp_task(self):
        while True:
            try:
                if self.cardType == CardType.BillingCard:
                    res = self.loop.run_until_complete(self.ocppStart())
                    self.ocppActive = False
            except Exception as e:
                print("ocpp_task Exception:",e)
            time.sleep(10)
            