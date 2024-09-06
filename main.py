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
        os.system("service bluetooth restart")
        time.sleep(2)
        os.system("gpio-test.64 w d 20 0 > /dev/null 2>&1")
        # os.system("chmod +x /root/acApp/bash/bluetooth_set.sh")
        os.system("/root/acApp/bash/bluetooth_set.sh")
        time.sleep(5)
        self.initilly = True
        self.test_led = False
        self.test_charge = False
        self.testWebSocket = None
        self.logger = logger
        self.loop = loop
        self.charge_stopped = False
        self.chargePoint = None
        self.request_list = []
        self.model = None
        self.masterCard = None
        self.availability = AvailabilityType.operative
        self.bluetooth_error = None
        self.__chargePointStatus = None
        self.info = None
        self.__error_code = None
        self.__deviceState = None
        self.__led_state = None
        self.ocppActive = False
        self.cardType: CardType = None
        self.socketType = SocketType.Type2
        self.max_current = 32
        self.control_A_B_C = False
        self.control_C_B = False
        self.control_A_C = False
        self.meter_values_on = False
        self.settings = Settings(self)
        self.databaseModule = DatabaseModule(self)
        self.settings.configuration.load_configuration_from_db()
        self.bluetoothService = BluetoothService(self)
        self.id_tag_list = self.databaseModule.get_default_local_list()
        self.softwareSettings = SoftwareSettings(self,logger)
        self.flaskModule = FlaskModuleThread(self).start()
        self.webSocketServer = WebSocketServer(self,logger)
        self.ev = EV(self)
        self.ocpp_subprotocols = OcppVersion.ocpp16
        self.serialPort = SerialPort(self,logger)
        self.process = Process(self)
        if self.settings.deviceSettings.externalMidMeter == True:
            self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.externalMidMeterSlaveAddress)
        elif self.settings.deviceSettings.mid_meter == True:
            self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.midMeterSlaveAddress)
        Thread(target=self.read_charge_values_thred, daemon=True).start()
        Thread(target=self.control_output,daemon=True).start()
        # Thread(target=self.simu_test,daemon=True).start()
        self.deviceState = DeviceState.IDLE
        self.chargePointStatus = ChargePointStatus.available

        self.create_error = False
        

    @property
    def led_state(self):
        return self.__led_state

    @led_state.setter
    def led_state(self, value):
        if self.__led_state != value:
            print(Color.Macenta.value, "Led State:", value)
            self.__led_state = value
            Thread(target=self.serialPort.set_command_pid_led_control, args=(value,),daemon=True).start()

    def simu_test(self):
        while True:
            x = input()
            if x == "1":
                self.create_error = True
            elif x == "2":
                self.create_error = False
            time.sleep(1)

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
            print(Color.Cyan.value, "Device State:", value)
            self.__deviceState = value
            if self.__deviceState == DeviceState.CONNECTED:
                if self.charge_stopped != True:
                    # self.control_A_B_C = True
                    Thread(target=self.process.connected,daemon=True).start()
    
            elif self.__deviceState == DeviceState.WAITING_AUTH:
                if self.charge_stopped != True:
                    Thread(target=self.process.waiting_auth,daemon=True).start()
            
            elif self.__deviceState == DeviceState.WAITING_STATE_C:
                if self.charge_stopped != True:
                    Thread(target=self.process.waiting_state_c,daemon=True).start()
                
            elif self.__deviceState == DeviceState.CHARGING:
                if self.charge_stopped != True:
                    # self.control_C_B = True
                    Thread(target=self.process.charging,daemon=True).start()

            elif self.__deviceState == DeviceState.FAULT:
                # self.control_A_B_C = False
                # self.control_C_B = False
                Thread(target=self.process.fault,daemon=True).start()

            elif self.__deviceState == DeviceState.IDLE:
                self.charge_stopped = False
                # self.control_A_B_C = False
                # self.control_C_B = False
                Thread(target=self.process.idle,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_EVSE:
                self.charge_stopped = True
                # self.control_A_B_C = False
                # self.control_C_B = False
                Thread(target=self.process.stopped_by_evse,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_USER:
                self.charge_stopped = True
                # self.control_A_B_C = False
                # self.control_C_B = False
                Thread(target=self.process.stopped_by_user,daemon=True).start()
                
            elif self.__deviceState == DeviceState.SUSPENDED_EVSE:
                Thread(target=self.process.suspended_evse,daemon=True).start()

            elif self.__deviceState == DeviceState.SUSPENDED_EV:
                Thread(target=self.process.suspended_ev,daemon=True).start()
            
            elif self.__deviceState == DeviceState.OFFLINE:
                # self.control_C_B = False
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
            if self.chargePointStatus == ChargePointStatus.charging:
                self.led_state = LedState.Charging
 
    def ocpp_task(self):
        while True:
            if self.cardType == CardType.BillingCard:
                res = loop.run_until_complete(self.ocppStart())
                self.ocppActive = False
            time.sleep(10)
            
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
        app.testWebSocket = TestWebSocketModule(app,logger)

        app.ocpp_task()
    except Exception as e:
        print("__main__ Exception:", e)
          
    while True:
        time.sleep(5)
