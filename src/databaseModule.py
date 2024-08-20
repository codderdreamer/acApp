from __future__ import print_function
import sqlite3
import time
from ocpp.v16.enums import *
from datetime import datetime
from src.enums import *
from threading import Thread
import os
from src.logger import ac_app_logger as logger

class DatabaseModule():
    def __init__(self, application) -> None:
        self.application = application
        self.full_configuration = []
        self.get_model()
        self.get_master_card()
        self.get_socket_type()
        self.get_network_priority()
        self.get_settings_4g()
        self.get_ethernet_settings()
        self.get_dns_settings()
        self.get_wifi_settings()
        self.get_ocpp_settings()
        self.get_bluetooth_settings()
        self.get_timezoon_settings()
        self.get_firmware_version()
        self.get_functions_enable()
        self.get_availability()
        self.get_max_current()
        self.get_mid_settings()
        self.get_configuration()
        self.user = self.get_user_login()["UserName"]
        self.set_diagnostics_status('None', str(datetime.now()))
        self.reset_diagnostics_status()
        self.reset_firmware_status()
        
        
    def get_charge(self):
        data_dict = {}
        try:
            self.charge_database = sqlite3.connect('/root/Charge.sqlite')
            self.cursor = self.charge_database.cursor()
            query = "SELECT * FROM ev"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.charge_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            return data_dict
        except Exception as e:
            print("get_charge Exception:", e)
        return data_dict

    def get_dns_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM dns_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.dnsSettings.dnsEnable = data_dict["dnsEnable"]
            self.application.settings.dnsSettings.DNS1 = data_dict["dns1"]
            self.application.settings.dnsSettings.DNS2 = data_dict["dns2"]
        except Exception as e:
            print("get_dns_settings Exception:", e)
        return data_dict

    def get_ethernet_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM ethernet_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.ethernetSettings.ethernetEnable = data_dict["ethernetEnable"]
            self.application.settings.ethernetSettings.dhcpcEnable = data_dict["dhcpcEnable"]
            self.application.settings.ethernetSettings.ip = data_dict["ip"]
            self.application.settings.ethernetSettings.netmask = data_dict["netmask"]
            self.application.settings.ethernetSettings.gateway = data_dict["gateway"]
        except Exception as e:
            print("get_ethernet_settings Exception:", e)
        return data_dict

    def get_network_priority(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM network_priority"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.networkPriority.enableWorkmode = data_dict["enableWorkmode"]
            self.application.settings.networkPriority.first = data_dict["first"]
            self.application.settings.networkPriority.second = data_dict["second"]
            self.application.settings.networkPriority.third = data_dict["third"]
        except Exception as e:
            print("get_network_priority Exception:", e)
        return data_dict

    def get_settings_4g(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM settings_4g"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.settings4G.apn = data_dict["apn"]
            self.application.settings.settings4G.user = data_dict["user"]
            self.application.settings.settings4G.password = data_dict["password"]
            self.application.settings.settings4G.pin = data_dict["pin"]
            self.application.settings.settings4G.enableModification = data_dict["enableModification"]
        except Exception as e:
            print("get_settings_4g Exception:", e)
        return data_dict

    def get_wifi_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM wifi_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.wifiSettings.wifiEnable = data_dict["wifiEnable"]
            self.application.settings.wifiSettings.mod = data_dict["mod"]
            self.application.settings.wifiSettings.ssid = data_dict["ssid"]
            self.application.settings.wifiSettings.password = data_dict["password"]
            self.application.settings.wifiSettings.encryptionType = data_dict["encryptionType"]
            self.application.settings.wifiSettings.wifidhcpcEnable = data_dict["wifidhcpcEnable"]
            self.application.settings.wifiSettings.ip = data_dict["ip"]
            self.application.settings.wifiSettings.netmask = data_dict["netmask"]
            self.application.settings.wifiSettings.gateway = data_dict["gateway"]
        except Exception as e:
            print("get_wifi_settings Exception:", e)
        return data_dict

    def get_ocpp_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM ocpp_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.ocppSettings.domainName = data_dict["domainName"]
            self.application.settings.ocppSettings.port = data_dict["port"]
            self.application.settings.ocppSettings.sslEnable = data_dict["sslEnable"]
            self.application.settings.ocppSettings.authorizationKey = data_dict["authorizationKey"]
            self.application.settings.ocppSettings.path = data_dict["path"]
            self.application.settings.ocppSettings.chargePointId = data_dict["chargePointId"]
            self.application.settings.ocppSettings.certFileName = data_dict["certFileName"]
        except Exception as e:
            print("get_ocpp_settings Exception:", e)
        return data_dict
        
    def get_functions_enable(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM functions_enable"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.functionsEnable.card_type = data_dict["card_type"]
            self.application.settings.functionsEnable.whether_to_open_the_qr_code_process = data_dict["whether_to_open_the_qr_code_process"]
            self.application.settings.functionsEnable.local_startup_whether_to_go_ocpp_background = data_dict["local_startup_whether_to_go_ocpp_background"]
            self.application.settings.functionsEnable.whether_to_transfer_private_data = data_dict["whether_to_transfer_private_data"]
        except Exception as e:
            print("get_functions_enable Exception:", e)
        return data_dict
    
    def get_bluetooth_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM bluetooth_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.bluetoothSettings.bluetooth_enable = data_dict["bluetooth_enable"]
            self.application.settings.bluetoothSettings.pin = data_dict["pin"]
            self.application.settings.bluetoothSettings.bluetooth_name = data_dict["bluetooth_name"]
        except Exception as e:
            print("get_bluetooth_settings Exception:", e)
        return data_dict
        
    def get_timezoon_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM timezoon_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.timezoonSettings.timezone = data_dict["timezone"]
        except Exception as e:
            print("get_timezoon_settings Exception:", e)
        return data_dict
        
    def get_firmware_version(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM firmware_version"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.settings.firmwareVersion.version = data_dict["version"]
        except Exception as e:
            print("get_firmware_version Exception:", e)
        return data_dict
        
    def get_availability(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            data_dict = {}
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            if data_dict["availability"] == AvailabilityType.operative.value:
                self.application.availability = AvailabilityType.operative
            elif data_dict["availability"] == AvailabilityType.inoperative.value:
                self.application.availability = AvailabilityType.inoperative
            else:
                self.application.availability = AvailabilityType.operative
        except Exception as e:
            print("get_availability Exception:", e)
        return data_dict
     
    def get_max_current(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.max_current = int(data_dict["maxcurrent"])
        except Exception as e:
            print("get_max_current Exception:", e)
        return data_dict
    
    def get_mid_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            print(data_dict)
            self.application.settings.deviceSettings.mid_meter = (data_dict["midMeter"] == "True")
            self.application.settings.deviceSettings.midMeterSlaveAddress = int(data_dict["midMeterSlaveAddress"])
            self.application.settings.deviceSettings.externalMidMeter = (data_dict["externalMidMeter"]=="True")
            self.application.settings.deviceSettings.externalMidMeterSlaveAddress = int(data_dict["externalMidMeterSlaveAddress"])
            return bool(data_dict["midMeter"])
        except Exception as e:
            print("get_mid_settings Exception:", e)

    def set_external_mid_settings(self, externalMidMeter, externalMidMeterSlaveAddress):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (externalMidMeter,"externalMidMeter")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (externalMidMeterSlaveAddress,"externalMidMeterSlaveAddress")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.deviceSettings.externalMidMeter = (externalMidMeter=="True")
            self.application.settings.deviceSettings.externalMidMeterSlaveAddress = int(externalMidMeterSlaveAddress)
        except Exception as e:
            print("set_external_mid_settings Exception:", e)

    def set_mid_settings(self, is_there_mid):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (str(is_there_mid),"midMeter")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.deviceSettings.mid_meter = is_there_mid
        except Exception as e:
            print("set_mid_settings Exception:", e)

    def set_serial_number(self,serialNumber):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (serialNumber,"serialNumber")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.settings_database.close()
        except Exception as e:
            print("set_serial_number Exception:", e)

    def set_master_card(self,masterCard):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            value = (masterCard,"masterCard")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.settings_database.close()
            self.application.masterCard = masterCard
            os.system("cp /root/Settings.sqlite /root/DefaultSettings.sqlite")
        except Exception as e:
            print("set_master_card Exception:", e)

    def get_master_card(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.masterCard = data_dict["masterCard"]
        except Exception as e:
            print("get_master_card Exception:", e)
        return data_dict
    
    def set_dns_settings(self,dnsEnable,dns1,dns2):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE dns_settings SET key = ? WHERE value = ?"
            
            value = (dnsEnable,"dnsEnable")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (dns1,"dns1")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (dns2,"dns2")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.settings_database.close()
            self.application.settings.dnsSettings.dnsEnable = dnsEnable
            self.application.settings.dnsSettings.DNS1 = dns1
            self.application.settings.dnsSettings.DNS2 = dns2
        except Exception as e:
            print("set_dns_settings Exception:", e)

    def set_ethernet_settings(self,ethernetEnable,dhcpcEnable,ip,netmask,gateway):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE ethernet_settings SET key = ? WHERE value = ?"
            
            value = (ethernetEnable,"ethernetEnable")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (dhcpcEnable,"dhcpcEnable")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (ip,"ip")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (netmask,"netmask")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (gateway,"gateway")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.ethernetSettings.ethernetEnable = ethernetEnable
            self.application.settings.ethernetSettings.dhcpcEnable = dhcpcEnable
            self.application.settings.ethernetSettings.ip = ip
            self.application.settings.ethernetSettings.netmask = netmask
            self.application.settings.ethernetSettings.gateway = gateway
        except Exception as e:
            print("set_ethernet_settings Exception:", e)

    def set_network_priority(self, enableWorkmode, first, second, third):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE network_priority SET key = ? WHERE value = ?"
            
            value = (enableWorkmode,"enableWorkmode")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (first,"first")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (second,"second")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (third,"third")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.settings_database.close()
            self.application.settings.networkPriority.enableWorkmode = enableWorkmode
            self.application.settings.networkPriority.first = first
            self.application.settings.networkPriority.second = second
            self.application.settings.networkPriority.third = third
        except Exception as e:
            print("set_network_priority Exception:", e)

    def set_charge(self, charge, id_tag, transaction_id):
        try:
            self.charge_database = sqlite3.connect('/root/Charge.sqlite')
            self.cursor = self.charge_database.cursor()
            query = "UPDATE ev SET key = ? WHERE value = ?"
            
            value = (charge,"charge")
            self.cursor.execute(query,value)
            self.charge_database.commit()
            
            value = (id_tag,"id_tag")
            self.cursor.execute(query,value)
            self.charge_database.commit()
            
            value = (transaction_id,"transaction_id")
            self.cursor.execute(query,value)
            self.charge_database.commit()
        except Exception as e:
            print("set_charge Exception:", e)

    def set_settings_4g(self, apn, user, password, enableModification, pin):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE settings_4g SET key = ? WHERE value = ?"
            
            value = (apn,"apn")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (user,"user")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (password,"password")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (enableModification,"enableModification")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (pin,"pin")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.settings4G.apn = apn
            self.application.settings.settings4G.user = user
            self.application.settings.settings4G.password = password
            self.application.settings.settings4G.enableModification = enableModification
            self.application.settings.settings4G.pin = pin
        except Exception as e:
            print("set_settings_4g Exception:", e)

    def set_wifi_settings(self, wifiEnable, mod, ssid, password, encryptionType, wifidhcpcEnable, ip, netmask, gateway):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE wifi_settings SET key = ? WHERE value = ?"
            
            value = (wifiEnable,"wifiEnable")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (mod,"mod")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (ssid,"ssid")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (password,"password")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (encryptionType,"encryptionType")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (wifidhcpcEnable,"wifidhcpcEnable")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (ip,"ip")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (netmask,"netmask")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (gateway,"gateway")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            self.application.settings.wifiSettings.wifiEnable = wifiEnable
            self.application.settings.wifiSettings.mod = mod
            self.application.settings.wifiSettings.ssid = ssid
            self.application.settings.wifiSettings.password = password
            self.application.settings.wifiSettings.encryptionType = encryptionType
            self.application.settings.wifiSettings.wifidhcpcEnable = wifidhcpcEnable
            self.application.settings.wifiSettings.ip = ip
            self.application.settings.wifiSettings.netmask = netmask
            self.application.settings.wifiSettings.gateway = gateway
        except Exception as e:
            print("set_wifi_settings Exception:", e)

    def set_ocpp_settings(self, domainName, port, sslEnable, authorizationKey, path, chargePointId, certFileName):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE ocpp_settings SET key = ? WHERE value = ?"
            
            value = (domainName,"domainName")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (port,"port")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (sslEnable,"sslEnable")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (authorizationKey,"authorizationKey")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (path,"path")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (chargePointId,"chargePointId")
            self.cursor.execute(query,value)
            self.settings_database.commit()

            value = (certFileName,"certFileName")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.ocppSettings.domainName = domainName
            self.application.settings.ocppSettings.port = port
            self.application.settings.ocppSettings.sslEnable = sslEnable
            self.application.settings.ocppSettings.authorizationKey = authorizationKey
            self.application.settings.ocppSettings.path = path
            self.application.settings.ocppSettings.chargePointId = chargePointId
            self.application.settings.ocppSettings.certFileName = certFileName
        except Exception as e:
            print("set_ocpp_settings Exception:", e)

    def set_charge_point_id(self, id):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE ocpp_settings SET key = ? WHERE value = ?"
            value = (id, "chargePointId")
            self.cursor.execute(query, value)
            self.settings_database.commit()
            self.settings_database.close()
            self.application.settings.ocppSettings.chargePointId = id
            return True
        except Exception as e:
            print("set_charge_point_id Exception:", e)
            return False

    def set_functions_enable(self, card_type, whether_to_open_the_qr_code_process, local_startup_whether_to_go_ocpp_background, whether_to_transfer_private_data):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE functions_enable SET key = ? WHERE value = ?"
            
            value = (card_type,"card_type")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (whether_to_open_the_qr_code_process,"whether_to_open_the_qr_code_process")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (local_startup_whether_to_go_ocpp_background,"local_startup_whether_to_go_ocpp_background")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (whether_to_transfer_private_data,"whether_to_transfer_private_data")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.functionsEnable.card_type = card_type
            self.application.settings.functionsEnable.whether_to_open_the_qr_code_process = whether_to_open_the_qr_code_process
            self.application.settings.functionsEnable.local_startup_whether_to_go_ocpp_background = local_startup_whether_to_go_ocpp_background
            self.application.settings.functionsEnable.whether_to_transfer_private_data = whether_to_transfer_private_data
        except Exception as e:
            print("set_functions_enable Exception:", e)

    def set_bluetooth_settings(self, bluetooth_enable, pin, bluetooth_name):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE bluetooth_settings SET key = ? WHERE value = ?"
            
            value = (bluetooth_enable,"bluetooth_enable")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (pin,"pin")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (bluetooth_name,"bluetooth_name")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.bluetoothSettings.bluetooth_enable = bluetooth_enable
            self.application.settings.bluetoothSettings.pin = pin
            self.application.settings.bluetoothSettings.bluetooth_name = bluetooth_name
        except Exception as e:
            print("set_bluetooth_settings Exception:", e)

    def set_timezone_settings(self,timezone):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE timezoon_settings SET key = ? WHERE value = ?"
            value = (timezone, "timezone")
            self.cursor.execute(query, value)
            self.settings_database.commit()
            self.settings_database.close()
            self.application.settings.timezoonSettings.timezone = timezone
        except Exception as e:
            print("set_timezone_settings Exception:", e)

    def set_firmware_version(self, version):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE firmware_version SET key = ? WHERE value = ?"
            value = (version, "version")
            self.cursor.execute(query, value)
            self.settings_database.commit()
            self.settings_database.close()
            self.application.settings.firmwareVersion.version = version
        except Exception as e:
            print("set_firmware_version Exception:", e)

    def set_availability(self, availability):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (availability,"availability")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.settings_database.close()
            if availability == AvailabilityType.operative.value:
                self.application.availability = AvailabilityType.operative
            elif availability == AvailabilityType.inoperative.value:
                self.application.availability = AvailabilityType.inoperative
        except Exception as e:
            print("set_availability Exception:", e)

    def set_model(self, modelId):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (modelId,"model")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.model = modelId
            g4 = self.is_there_4G(modelId)
            self.set_enable_4G(g4)
            if g4:
                Thread(target=self.application.softwareSettings.set_4G,daemon=True).start()
            self.set_socket_type(self.is_there_socket(modelId))
            self.set_mid_settings(self.is_there_mid(modelId))
            return True
        except Exception as e:
            print("set_model Exception:", e)
            return False

    def get_model(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            if data_dict["model"] == "" or data_dict["model"] == None:
                self.application.model = None
            else:
                self.application.model = data_dict["model"]
        except Exception as e:
            print("get_model Exception:", e)
        return data_dict

    def set_socket_type(self,is_there_socket):
        try:
            if is_there_socket:
                socketType = SocketType.Type2
            elif is_there_socket == False:
                socketType = SocketType.TetheredType
                
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (socketType.value,"socketType")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.settings_database.close()
            self.application.socketType = socketType
            return True
        except Exception as e:
            print("set_socket_type Exception:", e)
            return False

    def get_socket_type(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            if data_dict["socketType"] == "" or data_dict["model"] == None:
                self.application.socketType = None
            else:
                self.application.socketType = get_enum_member_by_value(SocketType,data_dict["socketType"])
        except Exception as e:
            print("get_socket_type Exception:", e)
        return data_dict
            
    def set_max_current(self,maxcurrent):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (maxcurrent,"maxcurrent")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.max_current = int(maxcurrent)
        except Exception as e:
            print("set_max_current Exception:", e)

    def set_default_local_list(self, local_list: list):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            self.cursor.execute('DELETE FROM default_local_list;')
            self.settings_database.commit()
            for idTag in local_list:
                query = '''INSERT INTO default_local_list (idTag) VALUES (?);'''
                self.cursor.execute(query, (idTag,))
                self.settings_database.commit()
            self.settings_database.close()
        except Exception as e:
            print("set_default_local_list Exception:", e)
            
    def get_default_local_list(self):
        id_tag_list = []
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM default_local_list"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for id in data:
                id_tag_list.append(id[0])
            return id_tag_list
        except Exception as e:
            print("get_default_local_list Exception:", e)

    def get_user_login(self):
        try:
            data_dict = {}
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM user_login"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict["UserName"] = row[0]
                data_dict["Password"] = row[1]
            return data_dict
        except Exception as e:
            print("get_user_login Exception:", e)

    def set_password(self, password):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE user_login SET Password = ? WHERE UserName = ?"
            
            value = (password,self.user)
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            return True
        except Exception as e:
            print("set_password Exception:", e)
            return False

    def is_there_4G(self, modelId):
        try:
            fourGList = ["faz1_mid1_4G1_S1","faz1_mid1_4G1_S0","faz1_mid0_4G1_S1","faz1_mid0_4G1_S0","faz0_mid1_4G1_S1","faz0_mid1_4G1_S0","faz0_mid0_4G1_S1","faz0_mid0_4G1_S0"]
            finded = False
            for value in fourGList:
                if modelId == value:
                    finded = True
            return finded
        except Exception as e:
            print("is_there_4G Exception:", e)

    def is_there_socket(self, modelId):
        try:
            socketList = ["faz1_mid1_4G1_S1","faz1_mid1_4G0_S1","faz1_mid0_4G1_S1","faz1_mid0_4G0_S1","faz0_mid1_4G1_S1", "faz0_mid1_4G0_S1", "faz0_mid0_4G1_S1", "faz0_mid0_4G0_S1"]
            finded = False
            for value in socketList:
                if modelId == value:
                    finded = True
            return finded
        except Exception as e:
            print("is_there_socket Exception:", e)

    def is_there_mid(self, modelId):
        try:
            midList = ["faz1_mid1_4G1_S1","faz1_mid1_4G1_S0","faz1_mid1_4G0_S1","faz1_mid1_4G0_S0","faz0_mid1_4G1_S1", "faz0_mid1_4G1_S0", "faz0_mid1_4G0_S1", "faz0_mid1_4G0_S0"]
            finded = False
            for value in midList:
                if modelId == value:
                    finded = True
            return finded
        except Exception as e:
            print("is_there_mid Exception:", e)

    def set_enable_4G(self, is_there_4G):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE settings_4g SET key = ? WHERE value = ?"
            
            value = (str(is_there_4G),"enableModification")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.application.settings.settings4G.enableModification = str(is_there_4G)
        except Exception as e:
            print("set_enable_4G Exception:", e)

    def get_configuration(self):
        try:
            configrations = []
            self.full_configuration = []
            configuration_db = sqlite3.connect('/root/configuration.db')
            cursor = configuration_db.cursor()
            query = "SELECT * FROM configs"
            cursor.execute(query)
            data = cursor.fetchall()
            configuration_db.close()
            print(Color.Cyan.value,"get_configuration",data)
            for column in data:
                key = column[0]
                readonly = column[1]
                value = column[2]
                supported = column[3]
                configrations.append({"key":key,"readonly":bool(readonly=="True"),"value":value,"supported":supported})
                self.full_configuration.append({"key":key,"readonly":(readonly=="True"),"value":value})
                setattr(self.application.settings.configuration, key, value)
            return configrations
        except Exception as e:
            print("get_configuration Exception:", e)

    def set_configuration(self,key,value):
        try:
            configuration_db = sqlite3.connect('/root/configuration.db')
            cursor = configuration_db.cursor()
            query = "UPDATE configs SET value = ? WHERE key = ?"
            value = (str(value),key)
            cursor.execute(query,value)
            configuration_db.commit()
            configuration_db.close()
            self.get_configuration()
        except Exception as e:
            print("set_configuration Exception:", e)

    def configuration_change(self,key,value):
        try:
            configuration_db = sqlite3.connect('/root/configuration.db')
            cursor = configuration_db.cursor()
            query = "SELECT * FROM configs WHERE key = ?"
            cursor.execute(query,(key,))
            data = cursor.fetchall()
            configuration_db.close()
            for column in data:
                supported = column[3]
                readonly = column[1]

            #  Accepted
            #  Configuration key is supported and setting has been changed.
            #  Rejected
            #  Configuration key is supported, but setting could not be changed.
            #  RebootRequired
            #  Configuration key is supported and setting has been changed, but change will be available after reboot (Charge Point will not
            #  reboot itself)
            #  NotSupported
            #  Configuration key is not supported.

            if supported == "True":
                if readonly == "True":
                    return "Rejected"
                else:
                    self.set_configuration(key,value)
                    return "Accepted"
            else:
                return "NotSupported"
            
        except Exception as e:
            print("check_configuration_change_availability Exception:", e)
          
               
            # return True supported and read_only 
        except Exception as e:
            print("is_configuration_supported Exception:", e)
           

    def clear_certificate_name(self):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE ocpp_settings SET key = ? WHERE value = ?"
            value = ("","certFileName")
            self.cursor.execute(query, value)
            self.settings_database.commit()
            self.settings_database.close()
        except Exception as e:
            print("clear_certificate_name Exception:", e)

    def get_diagnostics_status(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()

            query = "SELECT * FROM diagnostics_status ORDER BY id DESC LIMIT 1"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()

            if data:
                for row in data:
                    data_dict['status'] = row[1]
                    data_dict['last_update_time'] = row[2]
            else:
                data_dict['status'] = "Idle"
                data_dict['last_update_time'] = str(datetime.now())
                print("No diagnostics status found in the database.")
                return data_dict

        except Exception as e:
            print("get_diagnostics_status Exception:", e)
        
        return data_dict

    def set_diagnostics_status(self, status: str, last_update_time: str):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()

            query = "INSERT INTO diagnostics_status (status, last_update_time) VALUES (?, ?)"
            self.cursor.execute(query, (status, last_update_time))
            self.settings_database.commit()
            self.settings_database.close()

        except Exception as e:
            print("set_diagnostics_status Exception:", e)

    def reset_diagnostics_status(self):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()

            update_query = "UPDATE diagnostics_status SET status = ?"
            self.cursor.execute(update_query, ("Idle",))
            update_query = "UPDATE diagnostics_status SET last_update_time = ?"
            self.cursor.execute(update_query, (str(datetime.now()),))

            self.settings_database.commit()
            self.settings_database.close()
            print("Diagnostics status has been reset.")
        except Exception as e:
            print("reset_diagnostics_status Exception:", e)


    def get_firmware_status(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()

            query = "SELECT * FROM firmware_status ORDER BY id DESC LIMIT 1"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()

            if data:
                for row in data:
                    data_dict['status'] = row[1]
                    data_dict['last_update_time'] = row[2]
            else:
                data_dict = {'status': "Idle", 'last_update_time': str(datetime.now())}
                print("No firmware status found in the database.")
                return data_dict

        except Exception as e:
            print("get_firmware_status Exception:", e)
        
        return data_dict

    def set_firmware_status(self, status: str, last_update_time: str):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()

            query = "INSERT INTO firmware_status (status, last_update_time) VALUES (?, ?)"
            self.cursor.execute(query, (status, last_update_time))
            self.settings_database.commit()
            self.settings_database.close()

        except Exception as e:
            print("set_firmware_status Exception:", e)

    def reset_firmware_status(self):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()

            update_query = "UPDATE firmware_status SET status = ?"
            self.cursor.execute(update_query, ("Idle",))
            update_query = "UPDATE firmware_status SET last_update_time = ?"
            self.cursor.execute(update_query, (str(datetime.now()),))

            self.settings_database.commit()
            self.settings_database.close()
            print("Firmware status has been reset.")
        except Exception as e:
            print("reset_firmware_status Exception:", e)


   

    def add_auth_cache_tag(ocpp_tag, expire_date):
        try:
            settings_database = sqlite3.connect('/root/Settings.sqlite')
            cursor = settings_database.cursor()
            insert_query = "INSERT INTO auth_cache_list (ocpp_tag, expire_date) VALUES (?, ?)"
            cursor.execute(insert_query, (ocpp_tag, expire_date))
            settings_database.commit()
            settings_database.close()
            print(f"Added auth cache tag: {ocpp_tag}")
        except sqlite3.IntegrityError as e:
            print(f"Error adding auth cache tag: {e}")

    def update_auth_cache_tag(ocpp_tag, new_expire_date):
        try:
            settings_database = sqlite3.connect('/root/Settings.sqlite')
            cursor = settings_database.cursor()
            update_query = "UPDATE auth_cache_list SET expire_date = ?, updated_at = ? WHERE ocpp_tag = ?"
            cursor.execute(update_query, (new_expire_date, str(datetime.now()), ocpp_tag))
            settings_database.commit()
            settings_database.close()
            if cursor.rowcount:
                print(f"Updated auth cache tag: {ocpp_tag}")
            else:
                print(f"No auth cache tag found to update: {ocpp_tag}")
        except sqlite3.Error as e:
            print(f"Error updating auth cache tag: {e}")


    def delete_auth_cache_tag(ocpp_tag):
        try:
            settings_database = sqlite3.connect('/root/Settings.sqlite')
            cursor = settings_database.cursor()
            delete_query = "DELETE FROM auth_cache_list WHERE ocpp_tag = ?"
            cursor.execute(delete_query, (ocpp_tag,))
            settings_database.commit()
            settings_database.close()
            if cursor.rowcount:
                print(f"Deleted auth cache tag: {ocpp_tag}")
            else:
                print(f"No auth cache tag found to delete: {ocpp_tag}")
        except sqlite3.Error as e:
            print(f"Error deleting auth cache tag: {e}")

    def get_card_status_from_local_list(self, ocpp_tag):
        """
        Verilen ocpp_tag için local_auth_list tablosunda durumu döner.
        Durum `expire_date` kontrol edilerek belirlenir. Eğer tarih geçmişse 'Expired' olarak döner.
        """
        try:
            settings_database = sqlite3.connect('/root/Settings.sqlite')
            cursor = settings_database.cursor()
            select_query = "SELECT expire_date FROM local_auth_list WHERE ocpp_tag = ?"
            cursor.execute(select_query, (ocpp_tag,))
            result = cursor.fetchone()
            settings_database.close()

            if result:
                expire_date = result[0]
                if datetime.strptime(expire_date, '%Y-%m-%d').date() < datetime.now().date():
                    return "Expired"
                else:
                    return "Accepted"
            else:
                print(f"No entry found for ocpp_tag: {ocpp_tag}")
                return "Invalid"
        except sqlite3.Error as e:
            print(f"Error retrieving card status for ocpp_tag {ocpp_tag}: {e}")
            return "Invalid"
        
    def get_card_status_from_auth_cache(self, ocpp_tag):
        """
        Verilen ocpp_tag için auth_cache_list tablosunda durumu döner.
        Durum `expire_date` kontrol edilerek belirlenir. Eğer tarih geçmişse 'Expired' olarak döner.
        """
        try:
            settings_database = sqlite3.connect('/root/Settings.sqlite')
            cursor = settings_database.cursor()
            select_query = "SELECT expire_date FROM auth_cache_list WHERE ocpp_tag = ?"
            cursor.execute(select_query, (ocpp_tag,))
            result = cursor.fetchone()
            settings_database.close()

            if result:
                expire_date = result[0]
                if datetime.strptime(expire_date, '%Y-%m-%d').date() < datetime.now().date():
                    return "Expired"
                else:
                    return "Accepted"
            else:
                print(f"No entry found for ocpp_tag: {ocpp_tag}")
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving cache status for ocpp_tag {ocpp_tag}: {e}")
            return None