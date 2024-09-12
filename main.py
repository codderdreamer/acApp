from application import Application
import asyncio
import time


from src.chargePoint16 import ChargePoint16
from src.ev import EV
from src.serialPort import SerialPort
from src.settings import Settings
from src.databaseModule import DatabaseModule
from src.softwareSettings import SoftwareSettings
from src.websocketServer import WebSocketServer
from src.bluetoothService.bluetoothService import BluetoothService
from src.process import Process
from src.modbusModule import ModbusModule
from src.flaskModule import FlaskModuleThread
from src.utils import Utils
from src.deviceStateModule import DeviceStateModule

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        utils = Utils()
        settings = Settings()
        databaseModule = DatabaseModule()
        bluetoothService = BluetoothService()
        softwareSettings = SoftwareSettings()
        # flaskModule = FlaskModuleThread()
        # webSocketServer = WebSocketServer()
        # process = Process()
        # ev = EV()
        # serialPort = SerialPort()
        # modbusModule = ModbusModule()
        # deviceStateModule = DeviceStateModule()
        # app = Application(loop)
        # app.utils = utils
        # app.settings = settings
        # app.databaseModule = databaseModule
        # app.bluetoothService = bluetoothService
        # app.softwareSettings = softwareSettings
        # app.flaskModule = flaskModule
        # app.webSocketServer = webSocketServer
        # app.process = process
        # app.ev = ev
        # app.serialPort = serialPort
        # app.modbusModule = modbusModule
        # app.deviceStateModule = deviceStateModule
        # app.run()
        # app.ocpp_task()
    except Exception as e:
        print("__main__ Exception:", e)
    while True:
        time.sleep(5)
