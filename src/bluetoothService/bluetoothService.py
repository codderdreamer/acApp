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
from src.logger import ac_app_logger as logger


class BluetoothService():
    def __init__(self, application) -> None:
        self.application = application
        self.parser = None
        self.args = None
        self.adapter_name = None
        self.bus = None
        self.mainloop = None
        # Thread(target=self.run, daemon=True).start()

    def run(self):
        try:
            self.parser = argparse.ArgumentParser()
            self.parser.add_argument('-a', '--adapter-name', type=str, help='Adapter name', default='')
            self.args = self.parser.parse_args()
            self.adapter_name = self.args.adapter_name
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SystemBus()
            self.register_agent()
            self.mainloop = GObject.MainLoop()
            advertising.advertising_main(self.mainloop, self.bus, self.adapter_name)
            gatt_server.gatt_server_main(self.application, self.mainloop, self.bus, self.adapter_name)
            self.mainloop.run()
        except Exception as e:
            print("BluetoothService run Exception:", e)

    def register_agent(self):
        try:
            path = "/test/agent"
            agent = Agent(self.bus, path)
            obj = self.bus.get_object("org.bluez", "/org/bluez")
            manager = dbus.Interface(obj, "org.bluez.AgentManager1")
            manager.RegisterAgent(path, "NoInputNoOutput")
            manager.RequestDefaultAgent(path)
            print("Agent registered successfully")
        except Exception as e:
            print("Failed to register agent:", e)

class Agent(dbus.service.Object):
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        print("Agent released")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode called for device:", device)
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel called")

if __name__ == "__main__":
    BluetoothService(application=None)
