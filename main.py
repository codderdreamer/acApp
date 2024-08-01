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

from src.logger import ac_app_logger as logger

class Application():
    def __init__(self, loop):
        logger.info("------------------------------------------------------------")
        logger.info("------------------------------------------------------------")
        logger.info("------------------------------------------------------------")
        logger.info("------------------------------------------------------------")
        logger.info("\n--- Application Run Started ---\n")
        os.system("service bluetooth restart")
        time.sleep(2)
        os.system("gpio-test.64 w d 20 0 > /dev/null 2>&1")
        os.system("chmod +x /root/acApp/bluetooth_set.sh")
        os.system("/root/acApp/bluetooth_set.sh")
        time.sleep(5)
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
        
        self.chargingStatus = ChargePointStatus.available
        self.error_code = None
        
        self.__deviceState = None
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
        self.bluetoothService = BluetoothService(self)
        self.id_tag_list = self.databaseModule.get_local_list()
        self.softwareSettings = SoftwareSettings(self,logger)
        self.flaskModule = FlaskModuleThread(self)
        self.webSocketServer = WebSocketServer(self,logger)
        self.ev = EV(self)
        self.ocpp_subprotocols = OcppVersion.ocpp16
        self.serialPort = SerialPort(self,logger)
        self.process = Process(self)
        
        if self.settings.deviceSettings.externalMidMeter == True:
            logger.info("----------------------------self.settings.deviceSettings.externalMidMeter %s %s",
                               self.settings.deviceSettings.externalMidMeter,
                               self.settings.deviceSettings.externalMidMeterSlaveAddress)
            self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.externalMidMeterSlaveAddress)
        elif self.settings.deviceSettings.mid_meter == True:
            logger.info("----------------------------self.settings.deviceSettings.mid_meter %s %s",
                               self.settings.deviceSettings.mid_meter,
                               self.settings.deviceSettings.midMeterSlaveAddress)
            self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.midMeterSlaveAddress)
        else:
            logger.info("----------------------------self.settings.deviceSettings.mid_meter %s %s",
                               self.settings.deviceSettings.mid_meter, type(self.settings.deviceSettings.mid_meter))
            logger.info("----------------------------self.settings.deviceSettings.externalMidMeter %s %s",
                               self.settings.deviceSettings.externalMidMeter, type(self.settings.deviceSettings.externalMidMeter))
        
        Thread(target=self.read_charge_values_thred, daemon=True).start()

        self.deviceState = DeviceState.IDLE
        
    @property
    def deviceState(self):
        return self.__deviceState

    @deviceState.setter
    def deviceState(self, value):
        # print("???????????????????????????????????????????????????????", value,self.__deviceState)
        if self.__deviceState != value:
            
            self.__deviceState = value
            if self.__deviceState == DeviceState.CONNECTED:
                if self.charge_stopped != True:
                    self.control_A_B_C = True
                    Thread(target=self.process.connected,daemon=True).start()
    
            elif self.__deviceState == DeviceState.WAITING_AUTH:
                if self.charge_stopped != True:
                    Thread(target=self.process.waiting_auth,daemon=True).start()
            
            elif self.__deviceState == DeviceState.WAITING_STATE_C:
                if self.charge_stopped != True:
                    Thread(target=self.process.waiting_state_c,daemon=True).start()
                
            elif self.__deviceState == DeviceState.CHARGING:
                if self.charge_stopped != True:
                    self.control_C_B = True
                    Thread(target=self.process.charging,daemon=True).start()

            elif self.__deviceState == DeviceState.FAULT:
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.fault,daemon=True).start()

            elif self.__deviceState == DeviceState.IDLE:
                self.charge_stopped = False
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.idle,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_EVSE:
                self.charge_stopped = True
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.stopped_by_evse,daemon=True).start()
                
            elif self.__deviceState == DeviceState.STOPPED_BY_USER:
                self.charge_stopped = True
                self.control_A_B_C = False
                self.control_C_B = False
                Thread(target=self.process.stopped_by_user,daemon=True).start()
                
            elif self.__deviceState == DeviceState.SUSPENDED_EVSE:
                Thread(target=self.process.suspended_evse,daemon=True).start()
                
    def change_status_notification(self, error_code : ChargePointErrorCode, status : ChargePointStatus):
        print("error_code != self.error_code or status != self.chargingStatus",error_code != self.error_code or status != self.chargingStatus)
        print("status",status,self.chargingStatus)
        if error_code != self.error_code or status != self.chargingStatus:
            self.error_code = error_code
            self.chargingStatus = status
            if self.ocppActive:
                asyncio.run_coroutine_threadsafe(self.chargePoint.send_status_notification(connector_id=1,error_code=self.error_code,status=self.chargingStatus),self.loop)
    
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
                        logger.error("ocpp_control ping atılamadı...")
                        if time_start == None or time.time() - time_start > 10:
                            self.ocppActive = False
            
            except Exception as e:
                logger.exception("ocpp_control Exception:", e)
            time.sleep(3)
        
    def read_charge_values_thred(self):
        while True:
            try:
                # MID meter veya MCU'den veri alınıyor
                if (self.settings.deviceSettings.mid_meter or self.settings.deviceSettings.externalMidMeter) and self.modbusModule.connection:
                    logger.debug("Veriler MID'den alınıyor...")
                    self.ev.current_L1 = self.modbusModule.current_L1 if self.modbusModule.current_L1 is not None else 0
                    self.ev.current_L2 = self.modbusModule.current_L2 if self.modbusModule.current_L2 is not None else 0
                    self.ev.current_L3 = self.modbusModule.current_L3 if self.modbusModule.current_L3 is not None else 0
                    self.ev.voltage_L1 = self.modbusModule.voltage_L1 if self.modbusModule.voltage_L1 is not None else 0
                    self.ev.voltage_L2 = self.modbusModule.voltage_L2 if self.modbusModule.voltage_L2 is not None else 0
                    self.ev.voltage_L3 = self.modbusModule.voltage_L3 if self.modbusModule.voltage_L3 is not None else 0
                    # Güvenli bir çıkarma işlemi için None kontrolü ekleyin
                    energy = self.modbusModule.energy if self.modbusModule.energy is not None else 0
                    firstEnergy = self.modbusModule.firstEnergy if self.modbusModule.firstEnergy is not None else 0
                    self.ev.energy = round(energy - firstEnergy, 2)
                    self.ev.power = self.modbusModule.power if self.modbusModule.power is not None else 0
                elif not self.settings.deviceSettings.mid_meter and not self.settings.deviceSettings.externalMidMeter:
                    logger.debug("Veriler MCU'den alınıyor...")
                    self.ev.current_L1 = self.serialPort.current_L1 if self.serialPort.current_L1 is not None else 0
                    self.ev.current_L2 = self.serialPort.current_L2 if self.serialPort.current_L2 is not None else 0
                    self.ev.current_L3 = self.serialPort.current_L3 if self.serialPort.current_L3 is not None else 0
                    self.ev.voltage_L1 = self.serialPort.voltage_L1 if self.serialPort.voltage_L1 is not None else 0
                    self.ev.voltage_L2 = self.serialPort.voltage_L2 if self.serialPort.voltage_L2 is not None else 0
                    self.ev.voltage_L3 = self.serialPort.voltage_L3 if self.serialPort.voltage_L3 is not None else 0
                    self.ev.energy = round(self.serialPort.energy if self.serialPort.energy is not None else 0, 2)
                    self.ev.power = self.serialPort.power if self.serialPort.power is not None else 0
                else:
                    # Veriler geçerli değilse sıfırla
                    self.ev.current_L1 = 0
                    self.ev.current_L2 = 0
                    self.ev.current_L3 = 0
                    self.ev.voltage_L1 = 0
                    self.ev.voltage_L2 = 0
                    self.ev.voltage_L3 = 0
                    self.ev.energy = 0
                    self.ev.power = 0
                    
                # Her saniye verileri güncelle
                time.sleep(1)
                
            except Exception as e:
                logger.exception("read_charge_values_thred Exception: %s", e)
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
                logger.info("********************************************************ocpp_url:",ocpp_url)
                
                async with websockets.connect(ocpp_url, subprotocols=[self.ocpp_subprotocols.value],compression=None,timeout=10) as ws:
                    logger.info("Ocpp'ye bağlanmaya çalışıyor...")
                    if self.ocpp_subprotocols == OcppVersion.ocpp16:
                        self.chargePoint = ChargePoint16(self, self.settings.ocppSettings.chargePointId, ws, self.loop)
                        future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                        await self.chargePoint.send_boot_notification(self.settings.ocppSettings.chargePointId, self.settings.ocppSettings.chargePointId)
        except Exception as e:
            logger.exception("ocppStart Exception:", e)
            self.ocppActive = False
            if self.chargingStatus == ChargePointStatus.charging:
                Thread(target=self.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
            # else:
            #     Thread(target=self.serialPort.set_command_pid_led_control, args=(LedState.DeviceOffline,), daemon= True).start()
            #     self.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.faulted)
            
            
    def ocpp_task(self):
        while True:
            if self.cardType == CardType.BillingCard:
                logger.info("-----------------------------------ocpp start--------------------------------------")
                res = loop.run_until_complete(self.ocppStart())
                self.ocppActive = False
                logger.info("-----------------------------------ocpp stop--------------------------------------")
            time.sleep(3)
            
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
        # testServer = TestServer(app)
        # Thread(target=testServer.run,args=(loop,), daemon=True).start()
        app.testWebSocket = TestWebSocketModule(app,logger)

        app.ocpp_task()
    except Exception as e:
        logger.exception("__main__ Exception:", e)
          
    while True:
        time.sleep(5)
