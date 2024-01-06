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

class Agent(dbus.service.Object):
    AGENT_INTERFACE = 'org.bluez.Agent1'

    def __init__(self, bus, path):
        super().__init__(bus, path)

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("Agent Released")

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def RequestPinCode(self, device, attempt):
        print("*********************************RequestPinCode (%s, %d)" % (device, attempt))
        return input("Enter PIN Code: ")  # Prompt for a PIN code

class BluetoothService():
    def __init__(self,application) -> None:
        self.application = application
        self.parser = None
        self.args = None
        self.adapter_name = None
        self.bus = None
        self.mainloop = None
        Thread(target=self.run,daemon=True).start()
        
    def setup_agent(self):
        self.agent_path = "/test/agent"
        self.agent = Agent(self.bus, self.agent_path)
        agent_manager = dbus.Interface(self.bus.get_object('org.bluez', '/org/bluez'), 'org.bluez.AgentManager1')
        agent_manager.RegisterAgent(self.agent_path, 'KeyboardDisplay')
        agent_manager.RequestDefaultAgent(self.agent_path)
        print("Agent registered")
        
    def run(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-a', '--adapter-name', type=str, help='Adapter name', default='')
        self.args = self.parser.parse_args()
        self.adapter_name = self.args.adapter_name
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.mainloop = GObject.MainLoop()
        
        advertising.advertising_main(self.mainloop, self.bus, self.adapter_name)
        gatt_server.gatt_server_main(self.application, self.mainloop, self.bus, self.adapter_name)
        
        self.setup_agent()
        
        self.mainloop.run()
        
# bleService = BluetoothService()
# while True:
#     time.sleep(1)
    
            