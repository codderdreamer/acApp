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
from src.midMeterModule import MidMeterModule
import subprocess
import os

class Application():
    def __init__(self,loop):
        self.midMeter : ModbusModule = None
        self.settings = Settings(self)
        self.databaseModule = DatabaseModule(self)
        self.bluetoothService = BluetoothService(self)
        self.softwareSettings = SoftwareSettings(self)
        self.flaskModule = FlaskModuleThread(self)
        self.webSocketServer = WebSocketServer(self)
        self.ev = EV(self)
        self.serialPort = SerialPort(self)
        self.process = Process(self)
        self.midMeterModule = MidMeterModule(self)