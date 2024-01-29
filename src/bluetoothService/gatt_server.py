from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import array
import functools
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
from random import randint
from src.bluetoothService import exceptions
from src.bluetoothService import adapters
import json
from datetime import datetime

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'


class ApplicationBluetooth(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    def __init__(self,bus,application):
        self.application = application
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(HeartRateService(bus, 0))
        self.add_service(SoftwareSettingsService(bus, 1, self.application))

    def get_path(self):
        try:
            return dbus.ObjectPath(self.path)
        except Exception as e:
            print(datetime.now(),"get_path Exception:",e)

    def add_service(self, service):
        try:
            self.services.append(service)
        except Exception as e:
            print(datetime.now(),"add_service Exception:",e)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        try:
            response = {}
            print('GetManagedObjects')
            for service in self.services:
                response[service.get_path()] = service.get_properties()
                chrcs = service.get_characteristics()
                for chrc in chrcs:
                    response[chrc.get_path()] = chrc.get_properties()
                    descs = chrc.get_descriptors()
                    for desc in descs:
                        response[desc.get_path()] = desc.get_properties()
            return response
        except Exception as e:
            print(datetime.now(),"GetManagedObjects Exception:",e)

class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        try:
            return {
                    GATT_SERVICE_IFACE: {
                            'UUID': self.uuid,
                            'Primary': self.primary,
                            'Characteristics': dbus.Array(
                                    self.get_characteristic_paths(),
                                    signature='o')
                    }
            }
        except Exception as e:
            print(datetime.now(),"get_properties Exception:",e)

    def get_path(self):
        try:
            return dbus.ObjectPath(self.path)
        except Exception as e:
            print(datetime.now(),"get_path Exception:",e)

    def add_characteristic(self, characteristic):
        try:
            self.characteristics.append(characteristic)
        except Exception as e:
            print(datetime.now(),"add_characteristic Exception:",e)

    def get_characteristic_paths(self):
        try:
            result = []
            for chrc in self.characteristics:
                result.append(chrc.get_path())
            return result
        except Exception as e:
            print(datetime.now(),"get_characteristic_paths Exception:",e)

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        try:
            if interface != GATT_SERVICE_IFACE:
                raise exceptions.InvalidArgsException()
            return self.get_properties()[GATT_SERVICE_IFACE]
        except Exception as e:
            print(datetime.now(),"GetAll Exception:",e)

class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        try:
            return {
                    GATT_CHRC_IFACE: {
                            'Service': self.service.get_path(),
                            'UUID': self.uuid,
                            'Flags': self.flags,
                            'Descriptors': dbus.Array(
                                    self.get_descriptor_paths(),
                                    signature='o')
                    }
            }
        except Exception as e:
            print(datetime.now(),"get_properties Exception:",e)

    def get_path(self):
        try:
            return dbus.ObjectPath(self.path)
        except Exception as e:
            print(datetime.now(),"get_path Exception:",e)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        try:
            result = []
            for desc in self.descriptors:
                result.append(desc.get_path())
            return result
        except Exception as e:
            print(datetime.now(),"get_descriptor_paths Exception:",e)

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        try:
            if interface != GATT_CHRC_IFACE:
                raise exceptions.InvalidArgsException()
            return self.get_properties()[GATT_CHRC_IFACE]
        except Exception as e:
            print(datetime.now(),"GetAll Exception:",e)

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        try:
            return {
                    GATT_DESC_IFACE: {
                            'Characteristic': self.chrc.get_path(),
                            'UUID': self.uuid,
                            'Flags': self.flags,
                    }
            }
        except Exception as e:
            print(datetime.now(),"get_properties Exception:",e)

    def get_path(self):
        try:
            return dbus.ObjectPath(self.path)
        except Exception as e:
            print(datetime.now(),"get_path Exception:",e)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        try:
            if interface != GATT_DESC_IFACE:
                raise exceptions.InvalidArgsException()
            return self.get_properties()[GATT_DESC_IFACE]
        except Exception as e:
            print(datetime.now(),"GetAll Exception:",e)

    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise exceptions.NotSupportedException()

class HeartRateService(Service):
    """
    Fake Heart Rate Service that simulates a fake heart beat and control point
    behavior.

    """
    HR_UUID = '0000180d-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.HR_UUID, True)
        self.add_characteristic(HeartRateMeasurementChrc(bus, 0, self))
        self.add_characteristic(BodySensorLocationChrc(bus, 1, self))
        self.add_characteristic(HeartRateControlPointChrc(bus, 2, self))
        self.energy_expended = 0

class HeartRateMeasurementChrc(Characteristic):
    HR_MSRMT_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.HR_MSRMT_UUID,
                ['notify'],
                service)
        self.notifying = False
        self.hr_ee_count = 0

    def hr_msrmt_cb(self):
        try:
            value = []
            value.append(dbus.Byte(0x06))
            value.append(dbus.Byte(randint(90, 130)))
            if self.hr_ee_count % 10 == 0:
                value[0] = dbus.Byte(value[0] | 0x08)
                value.append(dbus.Byte(self.service.energy_expended & 0xff))
                value.append(dbus.Byte((self.service.energy_expended >> 8) & 0xff))
            self.service.energy_expended = \
                    min(0xffff, self.service.energy_expended + 1)
            self.hr_ee_count += 1
            print('Updating value: ' + repr(value))
            self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])
            return self.notifying
        except Exception as e:
            print(datetime.now(),"hr_msrmt_cb Exception:",e)

    def _update_hr_msrmt_simulation(self):
        try:
            print('Update HR Measurement Simulation')
            if not self.notifying:
                return
            GObject.timeout_add(1000, self.hr_msrmt_cb)
        except Exception as e:
            print(datetime.now(),"_update_hr_msrmt_simulation Exception:",e)

    def StartNotify(self):
        try:
            if self.notifying:
                print('Already notifying, nothing to do')
                return
            self.notifying = True
            self._update_hr_msrmt_simulation()
        except Exception as e:
            print(datetime.now(),"StartNotify Exception:",e)

    def StopNotify(self):
        try:
            if not self.notifying:
                print('Not notifying, nothing to do')
                return
            self.notifying = False
            self._update_hr_msrmt_simulation()
        except Exception as e:
            print(datetime.now(),"StopNotify Exception:",e)

class BodySensorLocationChrc(Characteristic):
    BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.BODY_SNSR_LOC_UUID,
                ['read'],
                service)

    def ReadValue(self, options):
        # Return 'Chest' as the sensor location.
        return [ 0x01 ]

class HeartRateControlPointChrc(Characteristic):
    HR_CTRL_PT_UUID = '00002a39-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.HR_CTRL_PT_UUID,
                ['write'],
                service)

    def WriteValue(self, value, options):
        try:
            print('Heart Rate Control Point WriteValue called')
            if len(value) != 1:
                raise exceptions.InvalidValueLengthException()
            byte = value[0]
            print('Control Point value: ' + repr(byte))
            if byte != 1:
                raise exceptions.FailedException("0x80")
            print('Energy Expended field reset!')
            self.service.energy_expended = 0
        except Exception as e:
            print(datetime.now(),"WriteValue Exception:",e)

class SoftwareSettingsService(Service):
    
    SoftwareSettings_UUID = '12345678-1234-5678-1234-56789abcab00'
    
    def __init__(self, bus, index, application):
        Service.__init__(self, bus, index, self.SoftwareSettings_UUID, True)
        self.add_characteristic(NetworkPriorityCharacteristic(bus, 0, self, application))
        self.add_characteristic(SettingsFourGCharacteristic(bus, 1, self, application))
        self.add_characteristic(EthernetSettingsCharacteristic(bus, 2, self, application))
        self.add_characteristic(DNSSettingsCharacteristic(bus, 3, self, application))
        self.add_characteristic(WifiSettingsCharacteristic(bus, 4, self, application))
        self.add_characteristic(OcppSettingsCharacteristic(bus, 5, self, application))
        self.add_characteristic(FunctionsSettingsCharacteristic(bus, 6, self, application))
        self.add_characteristic(BluetoothSettingsCharacteristic(bus, 7, self, application))
        self.add_characteristic(TimezoonSettingsCharacteristic(bus, 8, self, application))
        self.add_characteristic(FirmwareSettingsCharacteristic(bus, 9, self, application))
        self.add_characteristic(MaxCurrentSettingsCharacteristic(bus, 10, self, application))
        self.add_characteristic(DeviceStatusSettingsCharacteristic(bus, 11, self, application))
        
class NetworkPriorityCharacteristic(Characteristic):
    
    NETWORK_PRIORITY_UUID = '12345678-1234-5678-1234-56789abcab01'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.NETWORK_PRIORITY_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_network_priority().encode('utf-8')
            print('NetworkPriorityCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"NetworkPriorityCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("NetworkPriorityCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("NetworkPriorityCharacteristic WriteValue -->", json_object)
            self.application.settings.set_network_priority(json_object)
        except Exception as e:
            print(datetime.now(),"NetworkPriorityCharacteristic WriteValue Exception:",e)
            
class SettingsFourGCharacteristic(Characteristic):
    
    Settings4G_UUID = '12345678-1234-5678-1234-56789abcab02'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.Settings4G_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_Settings4G().encode('utf-8')
            print('Settings4GCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"SettingsFourGCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("Settings4GCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("SettingsFourGCharacteristic WriteValue -->", json_object)
            self.application.settings.set_Settings4G(json_object)
        except Exception as e:
            print(datetime.now(),"SettingsFourGCharacteristic WriteValue Exception:",e)

class EthernetSettingsCharacteristic(Characteristic):
    
    Ethernet_Settings_UUID = '12345678-1234-5678-1234-56789abcab03'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.Ethernet_Settings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_ethernet_settings().encode('utf-8')
            print('EthernetSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"EthernetSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("EthernetSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("EthernetSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_ethernet_settings(json_object)
        except Exception as e:
            print(datetime.now(),"EthernetSettingsCharacteristic WriteValue Exception:",e)

class DNSSettingsCharacteristic(Characteristic):
    
    DNSSettings_UUID = '12345678-1234-5678-1234-56789abcab04'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.DNSSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_dns_settings().encode('utf-8')
            print('DNSSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"DNSSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("DNSSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("DNSSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_dns_settings(json_object)
        except Exception as e:
            print(datetime.now(),"DNSSettingsCharacteristic WriteValue Exception:",e)
            
class WifiSettingsCharacteristic(Characteristic):
    
    WifiSettings_UUID = '12345678-1234-5678-1234-56789abcab05'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.WifiSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_wifi_settings().encode('utf-8')
            print('WifiSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"WifiSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("WifiSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("WifiSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_wifi_settings(json_object)
        except Exception as e:
            print(datetime.now(),"WifiSettingsCharacteristic WriteValue Exception:",e)
            
class OcppSettingsCharacteristic(Characteristic):
    
    OcppSettings_UUID = '12345678-1234-5678-1234-56789abcab06'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.OcppSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_ocpp_settings().encode('utf-8')
            print('OcppSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"OcppSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("OcppSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("OcppSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_ocpp_settings(json_object)
        except Exception as e:
            print(datetime.now(),"OcppSettingsCharacteristic WriteValue Exception:",e)
            
class FunctionsSettingsCharacteristic(Characteristic):
    
    FunctionsSettings_UUID = '12345678-1234-5678-1234-56789abcab07'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.FunctionsSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_functions_enable().encode('utf-8')
            print('FunctionsSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"FunctionsSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("FunctionsSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("FunctionsSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_functions_enable(json_object)
        except Exception as e:
            print(datetime.now(),"FunctionsSettingsCharacteristic WriteValue Exception:",e)

class TimezoonSettingsCharacteristic(Characteristic):
    
    TimezoonSettings_UUID = '12345678-1234-5678-1234-56789abcab08'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.TimezoonSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_timezoon_settings().encode('utf-8')
            print('TimezoonSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"TimezoonSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("TimezoonSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("TimezoonSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_timezoon_settings(json_object)
        except Exception as e:
            print(datetime.now(),"TimezoonSettingsCharacteristic WriteValue Exception:",e)
            
class BluetoothSettingsCharacteristic(Characteristic):
    
    BluetoothSettings_UUID = '12345678-1234-5678-1234-56789abcab09'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.BluetoothSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_bluetooth_settings().encode('utf-8')
            print('BluetoothSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"BluetoothSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("BluetoothSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("BluetoothSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_bluetooth_settings(json_object)
        except Exception as e:
            print(datetime.now(),"BluetoothSettingsCharacteristic WriteValue Exception:",e)
            
class FirmwareSettingsCharacteristic(Characteristic):
    
    FirmwareSettings_UUID = '12345678-1234-5678-1234-56789abcab10'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.FirmwareSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_firmware_version().encode('utf-8')
            print('FirmwareSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"FirmwareSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("FirmwareSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("FirmwareSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_firmware_version(json_object)
        except Exception as e:
            print(datetime.now(),"FirmwareSettingsCharacteristic WriteValue Exception:",e)
            
class DeviceStatusSettingsCharacteristic(Characteristic):
    
    DeviceStatusSettings_UUID = '12345678-1234-5678-1234-56789abcab11'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.DeviceStatusSettings_UUID,
                ['read', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_device_status().encode('utf-8')
            print('DeviceStatusSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"DeviceStatusSettingsCharacteristic ReadValue Exception:",e)
            
class MaxCurrentSettingsCharacteristic(Characteristic):
    
    MaxCurrentSettings_UUID = '12345678-1234-5678-1234-56789abcab12'
    
    def __init__(self, bus, index, service, application):
        self.application = application
        Characteristic.__init__(
                self, bus, index,
                self.MaxCurrentSettings_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = None
        
    def ReadValue(self, options):
        try:
            self.value = self.application.settings.get_maxcurrent().encode('utf-8')
            print('MaxCurrentSettingsCharacteristic Read: ' + repr(self.value))
            return self.value
        except Exception as e:
            print(datetime.now(),"MaxCurrentSettingsCharacteristic ReadValue Exception:",e)

    def WriteValue(self, value, options):
        try:
            print("MaxCurrentSettingsCharacteristic Write: ",repr(value) )
            byte_array = bytes([byte for byte in value])
            json_string = byte_array.decode('utf-8')
            json_object = json.loads(json_string)
            print("MaxCurrentSettingsCharacteristic WriteValue -->", json_object)
            self.application.settings.set_maxcurrent(json_object)
        except Exception as e:
            print(datetime.now(),"MaxCurrentSettingsCharacteristic WriteValue Exception:",e)
            
def register_app_cb():
    print('GATT application registered')

def register_app_error_cb(mainloop, error):
    try:
        print('Failed to register application: ' + str(error))
        mainloop.quit()
    except Exception as e:
        print(datetime.now(),"register_app_error_cb Exception:",e)

def gatt_server_main(application, mainloop, bus, adapter_name):
    try:
        adapter = adapters.find_adapter(bus, GATT_MANAGER_IFACE, adapter_name)
        if not adapter:
            raise Exception('GattManager1 interface not found')
        service_manager = dbus.Interface(
                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                GATT_MANAGER_IFACE)
        app = ApplicationBluetooth(bus,application)
        print('Registering GATT application...')
        service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=functools.partial(register_app_error_cb, mainloop))
    except Exception as e:
        print(datetime.now(),"gatt_server_main Exception:",e)
