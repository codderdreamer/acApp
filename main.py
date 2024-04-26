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
import os

class Application():
    def __init__(self,loop):
       self.bluetoothService = BluetoothService(self)
       print("test")

    
if __name__ == "__main__":
    try:
        print(" ----------------------------- Hera Charge AC Application is Starting ----------------------------- ")
        loop = asyncio.get_event_loop()
        app = Application(loop)
    except Exception as e:
        print(datetime.now(),"__main__ Exception:",e)
    while True:
        time.sleep(5)
