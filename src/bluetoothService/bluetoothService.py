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
            gatt_server.gatt_server_main(self.application, self.mainloop, self.bus, self.adapter_name)
            self.mainloop.run()
        except Exception as e:
            print(datetime.now(), "BluetoothService run Exception:", e)

    def register_agent(self):
        agent_path = "/test/agent"
        capability = "DisplayYesNo"
        agent = Agent(self.bus, agent_path, capability)
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/org/bluez"), "org.bluez.AgentManager1")
        manager.RegisterAgent(agent_path, capability)
        manager.RequestDefaultAgent(agent_path)

class Agent(dbus.service.Object):
    def __init__(self, bus, path, capability):
        dbus.service.Object.__init__(self, bus, path)
        self.capability = capability

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        print("Agent released")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode (%s)" % (device))
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06u)" % (device, passkey))
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        return dbus.UInt32(0)

    @dbus.service.method("org.bluez.Agent1", in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print("AuthorizeService (%s, %s)" % (device, uuid))
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")



# if __name__ == "__main__":
#     BluetoothService(application=None)
