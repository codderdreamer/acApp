from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import functools
from src.bluetoothService import exceptions
from src.bluetoothService import adapters
from datetime import datetime

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = None
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = None
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        try:
            properties = dict()
            properties['Type'] = self.ad_type
            if self.service_uuids is not None:
                properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                        signature='s')
            if self.solicit_uuids is not None:
                properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                        signature='s')
            if self.manufacturer_data is not None:
                properties['ManufacturerData'] = dbus.Dictionary(
                    self.manufacturer_data, signature='qv')
            if self.service_data is not None:
                properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                            signature='sv')
            if self.include_tx_power is not None:
                properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
            return {LE_ADVERTISEMENT_IFACE: properties}
        except Exception as e:
            print(datetime.now(),"get_properties Exception:",e)

    def get_path(self):
        try:
            return dbus.ObjectPath(self.path)
        except Exception as e:
            print(datetime.now(),"get_path Exception:",e)

    def add_service_uuid(self, uuid):
        try:
            if not self.service_uuids:
                self.service_uuids = []
            self.service_uuids.append(uuid)
        except Exception as e:
            print(datetime.now(),"add_service_uuid Exception:",e)

    def add_solicit_uuid(self, uuid):
        try:
            if not self.solicit_uuids:
                self.solicit_uuids = []
            self.solicit_uuids.append(uuid)
        except Exception as e:
            print(datetime.now(),"add_solicit_uuid Exception:",e)

    def add_manufacturer_data(self, manuf_code, data):
        try:
            if not self.manufacturer_data:
                self.manufacturer_data = dbus.Dictionary({}, signature='qv')
            self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')
        except Exception as e:
            print(datetime.now(),"add_manufacturer_data Exception:",e)

    def add_service_data(self, uuid, data):
        try:
            if not self.service_data:
                self.service_data = dbus.Dictionary({}, signature='sv')
            self.service_data[uuid] = dbus.Array(data, signature='y')
        except Exception as e:
            print(datetime.now(),"add_service_data Exception:",e)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        try:
            # print('GetAll')
            if interface != LE_ADVERTISEMENT_IFACE:
                raise exceptions.InvalidArgsException()
            # print('returning props')
            return self.get_properties()[LE_ADVERTISEMENT_IFACE]
        except Exception as e:
            print(datetime.now(),"GetAll Exception:",e)

    @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                         in_signature='',
                         out_signature='')
    def Release(self):
        # print('%s: Released!' % self.path)
        pass

class TestAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid('180D')
        self.add_service_uuid('180F')
        self.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03, 0x04])
        self.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
        self.include_tx_power = True

def register_ad_cb():
    # print('Advertisement registered')
    pass

def register_ad_error_cb(mainloop, error):
    try:
        print('Failed to register advertisement: ' + str(error))
        mainloop.quit()
    except Exception as e:
            print(datetime.now(),"register_ad_error_cb Exception:",e)


def advertising_main(mainloop, bus, adapter_name):
    try:
        adapter = adapters.find_adapter(bus, LE_ADVERTISING_MANAGER_IFACE, adapter_name)
        # print('adapter: %s' % (adapter,))
        if not adapter:
            raise Exception('LEAdvertisingManager1 interface not found')

        adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    "org.freedesktop.DBus.Properties")

        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

        ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_IFACE)

        test_advertisement = TestAdvertisement(bus, 0)

        ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=functools.partial(register_ad_error_cb, mainloop))
    except Exception as e:
        print(datetime.now(),"advertising_main Exception:",e)