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

class Application():
    def __init__(self,loop):
        os.system("gpio-test.64 w d 20 0 > /dev/null 2>&1")
        os.system("chmod +x /root/acApp/bluetooth_set.sh")
        os.system("/root/acApp/bluetooth_set.sh")
        time.sleep(5)
        self.test_led = False
        self.test_charge = False
        self.testWebSocket = None
        
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
        self.cardType : CardType = None
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
        self.softwareSettings = SoftwareSettings(self)
        self.flaskModule = FlaskModuleThread(self)
        self.webSocketServer = WebSocketServer(self)
        self.ev = EV(self)
        self.ocpp_subprotocols = OcppVersion.ocpp16
        self.serialPort = SerialPort(self)
        self.process = Process(self)
        
        if self.settings.deviceSettings.externalMidMeter == True:
            print("----------------------------self.settings.deviceSettings.externalMidMeter",self.settings.deviceSettings.externalMidMeter, self.settings.deviceSettings.externalMidMeterSlaveAddress)
            self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.externalMidMeterSlaveAddress)
        elif self.settings.deviceSettings.mid_meter == True:
            print("----------------------------self.settings.deviceSettings.mid_meter",self.settings.deviceSettings.mid_meter, self.settings.deviceSettings.midMeterSlaveAddress)
            self.modbusModule = ModbusModule(self, port='/dev/ttyS5', slave_address=self.settings.deviceSettings.midMeterSlaveAddress)
        else:
            print("----------------------------self.settings.deviceSettings.mid_meter",self.settings.deviceSettings.mid_meter,type(self.settings.deviceSettings.mid_meter))
            print("----------------------------self.settings.deviceSettings.externalMidMeter",self.settings.deviceSettings.externalMidMeter,type(self.settings.deviceSettings.externalMidMeter))
        
        Thread(target=self.read_charge_values_thred,daemon=True).start()
        
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
                        print("ocpp_control ping atılamadı...")
                        if time_start == None or time.time() - time_start > 10:
                            self.ocppActive = False
            
            except Exception as e:
                print("ocpp_control",e)
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
                    self.ev.energy = self.modbusModule.energy - self.modbusModule.firstEnergy
                    self.ev.power =  self.modbusModule.power
                elif (self.settings.deviceSettings.mid_meter == False and self.settings.deviceSettings.externalMidMeter == False):
                    # print("Veriler MCU'dan alınıyor...")
                    self.ev.current_L1 = self.serialPort.current_L1
                    self.ev.current_L2 = self.serialPort.current_L2
                    self.ev.current_L3 = self.serialPort.current_L3
                    self.ev.voltage_L1 = self.serialPort.voltage_L1
                    self.ev.voltage_L2 = self.serialPort.voltage_L2
                    self.ev.voltage_L3 = self.serialPort.voltage_L3
                    self.ev.energy = self.serialPort.energy
                    self.ev.power =  self.modbusModule.power
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
                    
                # ocpp_url = "ws://ocpp.chargehq.net/ocpp16/evseid"
                print("********************************************************ocpp_url:",ocpp_url)
                
                async with websockets.connect(ocpp_url, subprotocols=[self.ocpp_subprotocols.value],compression=None,timeout=10) as ws:
                    
                    if self.ocpp_subprotocols == OcppVersion.ocpp16:
                        self.chargePoint = ChargePoint16(self,self.settings.ocppSettings.chargePointId, ws, self.loop)
                        future = asyncio.run_coroutine_threadsafe(self.chargePoint.start(), self.loop)
                        await self.chargePoint.send_boot_notification(self.settings.ocppSettings.chargePointId,self.settings.ocppSettings.chargePointId)
                        
                    elif self.ocpp_subprotocols == OcppVersion.ocpp20:
                        pass
                    elif self.ocpp_subprotocols == OcppVersion.ocpp21:
                        pass
        except Exception as e:
            self.ocppActive = False
            if self.chargingStatus == ChargePointStatus.charging:
                Thread(target=self.serialPort.set_command_pid_led_control, args=(LedState.Charging,), daemon= True).start()
            else:
                Thread(target=self.serialPort.set_command_pid_led_control, args=(LedState.DeviceOffline,), daemon= True).start()
                self.change_status_notification(ChargePointErrorCode.other_error,ChargePointStatus.faulted)
            print(datetime.now(),"ocppStart Exception:",e)
            
    def ocpp_task(self):
        while True:
            if self.cardType == CardType.BillingCard:
                print("-----------------------------------ocpp start--------------------------------------")
                res = loop.run_until_complete(self.ocppStart())
                self.ocppActive = False
                print("-----------------------------------ocpp stop--------------------------------------")
            time.sleep(3)
            
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
        app.testWebSocket = TestWebSocketModule(app)
        # testServer = TestServer(app)
        # Thread(target=testServer.run,args=(loop,), daemon=True).start()
        app.ocpp_task()
    except Exception as e:
        print(datetime.now(),"__main__ Exception:",e)
          
    while True:
        time.sleep(5)
