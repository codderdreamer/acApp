from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service


BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'

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
    
def setup_agent(self):
    self.agent_path = "/test/agent"
    self.agent = Agent(self.bus, self.agent_path)
    agent_manager = dbus.Interface(self.bus.get_object('org.bluez', '/org/bluez'), 'org.bluez.AgentManager1')
    agent_manager.RegisterAgent(self.agent_path, 'KeyboardDisplay')
    agent_manager.RequestDefaultAgent(self.agent_path)
    print("Agent registered")


def find_adapter(bus, adapter_interface_name, adapter_name):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    
    setup_agent()

    for o, props in objects.items():
        print('checking adapter %s, keys: %s' % (o, props.keys()))
        if adapter_interface_name in props.keys():
            print('found adapter %s' % (o,))
            if '/' + adapter_name in o:
                print('returning adapter %s' % (o,))
                return o

    return None