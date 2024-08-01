from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
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

from src.logger import ac_app_logger as logger

def find_adapter(bus, adapter_interface_name, adapter_name):
    try:
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()
        for o, props in objects.items():
            logger.debug('Checking adapter %s, keys: %s', o, props.keys())
            if adapter_interface_name in props.keys():
                logger.debug('Found adapter %s', o)
                if '/' + adapter_name in o:
                    logger.debug('Returning adapter %s', o)
                    return o
        return None
    except Exception as e:
        logger.exception("find_adapter Exception: %s", e)
