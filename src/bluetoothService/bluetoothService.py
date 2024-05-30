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
    def __init__(self, application) -> None:
        self.application = application
        self.parser = None
        self.args = None
        self.adapter_name = None
        self.bus = None
        self.mainloop = None
        Thread(target=self.run, daemon=True).start()

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
            self.register_agent()
            advertising.advertising_main(self.mainloop, self.bus, self.adapter_name)
            # gatt_server.gatt_server_main(self.application, self.mainloop, self.bus, self.adapter_name)
            self.mainloop.run()
        except Exception as e:
            print(datetime.now(), "BluetoothService run Exception:", e)

    def register_agent(self):
        try:
            path = "/test/agent"
            agent = Agent(self.bus, path)
            obj = self.bus.get_object("org.bluez", "/org/bluez")
            manager = dbus.Interface(obj, "org.bluez.AgentManager1")
            manager.RegisterAgent(path, "KeyboardDisplay")
            manager.RequestDefaultAgent(path)
            print("Agent registered successfully")
        except Exception as e:
            print(datetime.now(), "Failed to register agent:", e)

class Agent(dbus.service.Object):
    def __init__(self, bus, path):
        dbus.service.Object.__init__(self, bus, path)

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        print("Agent released")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode called for device: %s" % (device))
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation called for device: %s with passkey: %06u" % (device, passkey))
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode called for device: %s with pincode: %s" % (device, pincode))

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey called for device: %s" % (device))
        return dbus.UInt32(0)

    @dbus.service.method("org.bluez.Agent1", in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey called for device: %s with passkey: %06u entered: %u" % (device, passkey, entered))

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization called for device: %s" % (device))
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print("AuthorizeService called for device: %s with uuid: %s" % (device, uuid))
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel called")

if __name__ == "__main__":
    BluetoothService(application=None)
