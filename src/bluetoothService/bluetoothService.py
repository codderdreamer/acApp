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
import advertising
import gatt_server
import time

class BluetoothService():
    def __init__(self) -> None:
        self.parser = None
        self.args = None
        self.adapter_name = None
        self.bus = None
        self.mainloop = None
        Thread(target=self.run,daemon=True).start()
        
    def run(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-a', '--adapter-name', type=str, help='Adapter name', default='')
        self.args = self.parser.parse_args()
        self.adapter_name = self.args.adapter_name
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.mainloop = GObject.MainLoop()
        
        advertising.advertising_main(self.mainloop, self.bus, self.adapter_name)
        gatt_server.gatt_server_main(self.mainloop, self.bus, self.adapter_name)
        self.mainloop.run()
        
bleService = BluetoothService()
while True:
    time.sleep(1)
    
            