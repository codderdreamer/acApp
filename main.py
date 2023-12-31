import asyncio
import websockets
from src.chargePoint16 import ChargePoint16
from src.configModule import Config
from threading import Thread
from src.ensureFutures import EnsureFutures
from src.callbacks import OcppCallbacks
from src.enums import *
import time
from src.ev import EV
from src.serialPort import SerialPort
from src.settings import Settings
from src.databaseModule import DatabaseModule
from src.networkSettings import NetworkSettings
from src.websocketServer import WebSocketServer
from src.bluetoothService.bluetoothService import BluetoothService
from src.process import Process
from ocpp.v16.enums import *

class Application():
    def __init__(self,loop):
        self.loop = loop
        self.chargePoint = None
        
        self.ocppActive = True
        self.cardType = CardType.BillingCard
        self.__deviceState = None
        self.socketType = SocketType.Type2
        self.max_current = 63
        self.control_A_B_C = False
        self.control_C_B = False
        self.meter_values_on = False
        
        self.settings = Settings()
        self.networkSettings = NetworkSettings(self)
        self.databaseModule = DatabaseModule(self)
        self.webSocketServer = WebSocketServer(self)
        self.bluetoothService = BluetoothService(self)
        self.ev = EV(self)
        self.config = Config()
        self.ensureFutures = EnsureFutures(self)
        self.ocppCallbacks =  OcppCallbacks(self)
        self.ocpp_subprotocols = OcppVersion.ocpp16
        self.serialPort = SerialPort(self)
        self.process = Process(self)
        self.databaseModule.get_network_priority()
        self.databaseModule.get_settings_4g()
        self.databaseModule.get_ethernet_settings()
        self.databaseModule.get_dns_settings()
        self.databaseModule.get_wifi_settings()
        
        ethernetEnable = True
        ip = "192.168.1.70"
        netmask = "255.255.255.0"
        gateway = "192.168.1.1"
        self.networkSettings.set_eth(ethernetEnable,ip,netmask,gateway)
        
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
            async with websockets.connect(self.config.ocpp_server_url + self.config.charge_point_id, subprotocols=[self.ocpp_subprotocols.value]) as ws:
                if self.ocpp_subprotocols == OcppVersion.ocpp16:
                    self.chargePoint = ChargePoint16(self,self.config.charge_point_id, ws)
                    future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                    await self.chargePoint.send_boot_notification(self.config.charge_point_model,self.config.charge_point_vendor)
                elif self.ocpp_subprotocols == OcppVersion.ocpp20:
                    pass
                elif self.ocpp_subprotocols == OcppVersion.ocpp21:
                    pass
        except Exception as e:
            print("main",e)

    
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
        res = loop.run_until_complete(app.ocppStart())
    except Exception as e:
        print("__main__",e)
    while True:
        time.sleep(5)

# ttyS5 rfid kart için 