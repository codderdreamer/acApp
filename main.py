import asyncio
import websockets
from src.chargePoint16 import ChargePoint16
from src.configModule import Config
from threading import Thread
from src.callbacks import OcppCallbacks
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

class Application():
    def __init__(self,loop):
        self.loop = loop
        self.chargePoint = None
        
        self.availability = AvailabilityType.operative
        
        self.ocppActive = True
        self.cardType = CardType.BillingCard
        self.__deviceState = None
        self.socketType = SocketType.Type2
        self.max_current = 63
        
        self.control_A_B_C = False
        self.control_C_B = False
        self.meter_values_on = False
        
        self.settings = Settings(self)
        self.softwareSettings = SoftwareSettings(self)
        self.databaseModule = DatabaseModule(self)
        self.webSocketServer = WebSocketServer(self)
        self.bluetoothService = BluetoothService(self)
        self.ev = EV(self)
        self.config = Config()
        self.ocppCallbacks =  OcppCallbacks(self)
        self.ocpp_subprotocols = OcppVersion.ocpp16
        self.serialPort = SerialPort(self)
        self.process = Process(self)
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
        
        self.softwareSettings.set_eth()
        self.softwareSettings.set_4G()
        self.softwareSettings.set_wifi()
        self.softwareSettings.set_dns()
        Thread(target=self.softwareSettings.set_network_priority,daemon=True).start()
        self.softwareSettings.set_functions_enable()
        
        while self.config.config_writed == False:
            time.sleep(0.01)
            

        
    @property
    def deviceState(self):
        return self.__deviceState

    @deviceState.setter
    def deviceState(self, value):
        print("?????????????????????????????????????", value, self.__deviceState)
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
            if self.settings.ocppSettings.sslEnable == SSLEnable.Disable.value:
                ws = "ws://"
            elif self.settings.ocppSettings.sslEnable == SSLEnable.Enable.value:
                ws = "wss://"
            
            if self.settings.ocppSettings.port != None or self.settings.ocppSettings.port != "":
                ocpp_url = ws + self.settings.ocppSettings.domainName + ":" + self.settings.ocppSettings.port + self.settings.ocppSettings.path
            else:
                ocpp_url = ws + self.settings.ocppSettings.domainName + self.settings.ocppSettings.path
                
            print("********************************************************ocpp_url:",ocpp_url)
            
            async with websockets.connect(ocpp_url, subprotocols=[self.ocpp_subprotocols.value],open_timeout=10) as ws:
                if self.ocpp_subprotocols == OcppVersion.ocpp16:
                    self.chargePoint = ChargePoint16(self,self.config.charge_point_id, ws)
                    future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                    await self.chargePoint.send_boot_notification(self.config.charge_point_model,self.config.charge_point_vendor)
                elif self.ocpp_subprotocols == OcppVersion.ocpp20:
                    pass
                elif self.ocpp_subprotocols == OcppVersion.ocpp21:
                    pass
        
        except Exception as e:
            print("******************************************************** ocppStart",e)

    
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
        while True:
            if app.cardType == CardType.BillingCard:
                print("-----------------------------------ocpp start--------------------------------------")
                res = loop.run_until_complete(app.ocppStart())
                print("-----------------------------------ocpp stop--------------------------------------")
            time.sleep(1)
    except Exception as e:
        print("__main__",e)
    while True:
        time.sleep(5)

# ttyS5 rfid kart için 