from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import array

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject
import argparse
from threading import Thread
from src.bluetoothService import advertising
from src.bluetoothService import gatt_server
import time
from datetime import datetime

class BluetoothService():
    def __init__(self,application) -> None:
        self.application = application
        self.parser = None
        self.args = None
        self.adapter_name = None
        self.bus = None
        self.mainloop = None
        Thread(target=self.run,daemon=True).start()
        
    def run(self):
        try:
            print("Bluetooth run")
            self.parser = argparse.ArgumentParser()
            self.parser.add_argument('-a', '--adapter-name', type=str, help='Adapter name', default='')
            self.args = self.parser.parse_args()
            self.adapter_name = self.args.adapter_name
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SystemBus()
            self.mainloop = GObject.MainLoop()
            advertising.advertising_main(self.mainloop, self.bus, self.adapter_name)
            gatt_server.gatt_server_main(self.application, self.mainloop, self.bus, self.adapter_name)
            self.mainloop.run()
            self.application.bluetooth_error = True
        except Exception as e:
            print(datetime.now(),"BluetoothService run Exception:",e)
        