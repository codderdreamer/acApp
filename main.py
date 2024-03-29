import asyncio
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
import subprocess


class Application():
    def __init__(self,loop):
        # subprocess.run(["sh", "/root/acApp/bluetooth_set.sh"])
        # time.sleep(10)
        self.loop = loop
        self.chargePoint = None
        
        self.availability = AvailabilityType.operative
        self.chargingStatus = ChargePointStatus.available
        self.__deviceState = None
        
        self.ocppActive = False
        self.cardType = CardType.BillingCard
        
        self.socketType = SocketType.Type2
        self.max_current = 63
        
        self.control_A_B_C = False
        self.control_C_B = False
        self.meter_values_on = False
        self.flaskModule = FlaskModuleThread(self)
        self.settings = Settings(self)
        self.softwareSettings = SoftwareSettings(self)
        self.databaseModule = DatabaseModule(self)
        self.webSocketServer = WebSocketServer(self)
        # self.updateModule = UpdateModule(self)
        self.ev = EV(self)
        self.ocpp_subprotocols = OcppVersion.ocpp16
        self.serialPort = SerialPort(self)
        self.process = Process(self)
        self.modbusModule = ModbusModule(port='/dev/ttyS5', slave_address=1)
        self.databaseModule.get_network_priority()
        self.databaseModule.get_settings_4g()
        self.databaseModule.get_ethernet_settings()
        self.databaseModule.get_dns_settings()
        self.databaseModule.get_wifi_settings()
        self.databaseModule.get_ocpp_settings()
        self.databaseModule.get_bluetooth_settings()
        self.databaseModule.get_timezoon_settings()
        self.databaseModule.get_firmware_version()
        self.databaseModule.get_functions_enable()
        self.databaseModule.get_availability()
        self.databaseModule.get_max_current()
        self.id_tag_list = self.databaseModule.get_local_list()
        
        self.softwareSettings.set_eth()
        # time.sleep(5)
        self.softwareSettings.set_4G()
        # time.sleep(5)
        self.softwareSettings.set_wifi()
        # time.sleep(5)
        Thread(target=self.softwareSettings.set_network_priority,daemon=True).start()
        Thread(target=self.softwareSettings.control_device_status,daemon=True).start()
        self.softwareSettings.set_functions_enable()
        self.softwareSettings.set_timezoon()
        print("set_bluetooth_settings")
        self.softwareSettings.set_bluetooth_settings()
        self.process.idle()
        print("BluetoothService")
        self.bluetoothService = BluetoothService(self)
    
        
        
    @property
    def deviceState(self):
        return self.__deviceState

    @deviceState.setter
    def deviceState(self, value):
        print("???????????????????????????????????????????????????????", value,self.__deviceState)
        if self.__deviceState != value:
            self.__deviceState = value
            if self.__deviceState == DeviceState.CONNECTED:
                self.control_A_B_C = True
                Thread(target=self.process.connected,daemon=True).start()
    
            elif self.__deviceState == DeviceState.WAITING_AUTH:
                Thread(target=self.process.waiting_auth,daemon=True).start()
            
            elif self.__deviceState == DeviceState.WAITING_STATE_C:
                Thread(target=self.process.waiting_state_c,daemon=True).start()
                
            elif self.__deviceState == DeviceState.CHARGING:
                self.control_C_B = True
                Thread(target=self.process.charging,daemon=True).start()

            elif self.__deviceState == DeviceState.FAULT:
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.fault,daemon=True).start()

            elif self.__deviceState == DeviceState.IDLE:
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.idle,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_EVSE:
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.stopped_by_evse,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_USER:
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.stopped_by_user,daemon=True).start()
                

        
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
                    
                # ocpp_url = "ws://ocpp.chargehq.net/ocpp16/evseid"
                print("********************************************************ocpp_url:",ocpp_url)
                async with websockets.connect(ocpp_url, subprotocols=[self.ocpp_subprotocols.value],compression=None,timeout=10) as ws:
                    self.ocppActive = True
                    if self.ocpp_subprotocols == OcppVersion.ocpp16:
                        self.chargePoint = ChargePoint16(self,self.settings.ocppSettings.chargePointId, ws)
                        future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                        await self.chargePoint.send_boot_notification(self.settings.ocppSettings.chargePointId,self.settings.ocppSettings.chargePointId)
                    elif self.ocpp_subprotocols == OcppVersion.ocpp20:
                        pass
                    elif self.ocpp_subprotocols == OcppVersion.ocpp21:
                        pass
        except Exception as e:
            print(datetime.now(),"ocppStart Exception:",e)

    
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
        while True:
            if app.cardType == CardType.BillingCard:
                # print("-----------------------------------ocpp start--------------------------------------")
                res = loop.run_until_complete(app.ocppStart())
                app.ocppActive = False
                # print("-----------------------------------ocpp stop--------------------------------------")
            time.sleep(1)
    except Exception as e:
        print(datetime.now(),"__main__ Exception:",e)
    while True:
        time.sleep(5)
