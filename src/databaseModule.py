import sqlite3
import time
from ocpp.v16.enums import *
from datetime import datetime
from src.enums import *

class DatabaseModule():
    def __init__(self,application) -> None:
        from src.application import Application
        self.application : Application = application
        self.application.write_log("DatabaseModule Init Start",Color.Blue)
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
        self.get_device_settings()
        self.get_local_list()
        self.get_user_login()
        self.show_init_database()
        self.application.write_log("DatabaseModule Init Finish",Color.Blue)
        
    def show_init_database(self):
        print("----------------------------> Network Priority")
        print("enableWorkmode:",self.application.settings.networkPriority.enableWorkmode)
        print("first:", self.application.settings.networkPriority.first)
        print("second:", self.application.settings.networkPriority.second)
        print("third:", self.application.settings.networkPriority.third)
        print("----------------------------> Ethernet Settings")
        print("ethernetEnable:",self.application.settings.ethernetSettings.ethernetEnable)
        print("dhcpcEnable:",self.application.settings.ethernetSettings.dhcpcEnable)
        print("ip:", self.application.settings.ethernetSettings.ip)
        print("netmask:", self.application.settings.ethernetSettings.netmask)
        print("gateway:", self.application.settings.ethernetSettings.gateway)
        print("----------------------------> 4G Settings")
        print("apn:", self.application.settings.settings4G.apn)
        print("user:", self.application.settings.settings4G.user)
        print("password:", self.application.settings.settings4G.password)
        print("pin:", self.application.settings.settings4G.pin)
        print("enableModification:", self.application.settings.settings4G.enableModification)
        print("----------------------------> Wifi Settings")
        print("wifiEnable:", self.application.settings.wifiSettings.wifiEnable)
        print("mod:", self.application.settings.wifiSettings.mod)
        print("ssid:", self.application.settings.wifiSettings.ssid)
        print("password:", self.application.settings.wifiSettings.password)
        print("encryptionType:", self.application.settings.wifiSettings.encryptionType)
        print("wifidhcpcEnable:", self.application.settings.wifiSettings.wifidhcpcEnable)
        print("ip:", self.application.settings.wifiSettings.ip)
        print("netmask:", self.application.settings.wifiSettings.netmask)
        print("gateway:", self.application.settings.wifiSettings.gateway)
        print("----------------------------> DNS Settings")
        print("dnsEnable:", self.application.settings.dnsSettings.dnsEnable)
        print("DNS1:", self.application.settings.dnsSettings.DNS1)
        print("DNS2:", self.application.settings.dnsSettings.DNS2)
        print("----------------------------> OCPP Settings")
        print("domainName:",self.application.settings.ocppSettings.domainName)
        print("port:",self.application.settings.ocppSettings.port)
        print("sslEnable:",self.application.settings.ocppSettings.sslEnable)
        print("authorizationKey:",self.application.settings.ocppSettings.authorizationKey)
        print("path:",self.application.settings.ocppSettings.path)
        print("chargePointId:",self.application.settings.ocppSettings.chargePointId)
        print("----------------------------> Functions Enable")
        print("card_type:",self.application.settings.functionsEnable.card_type)
        print("whether_to_open_the_qr_code_process:",self.application.settings.functionsEnable.whether_to_open_the_qr_code_process)
        print("local_startup_whether_to_go_ocpp_background:",self.application.settings.functionsEnable.local_startup_whether_to_go_ocpp_background)
        print("whether_to_transfer_private_data:",self.application.settings.functionsEnable.whether_to_transfer_private_data)
        print("----------------------------> Bluetooth Settings")
        print("bluetooth_enable:",self.application.settings.bluetoothSettings.bluetooth_enable)
        print("pin:",self.application.settings.bluetoothSettings.pin)
        print("bluetooth_name:",self.application.settings.bluetoothSettings.bluetooth_name)
        print("----------------------------> Timezoone Settings")
        print("timezone:",self.application.settings.timezoonSettings.timezone)
        print("----------------------------> Firmware Settings")
        print("version:",self.application.settings.firmwareVersion.version)
        print("----------------------------> Device Settings")
        print("availability:",self.application.settings.deviceSettings.availability)
        print("max_current:",self.application.settings.deviceSettings.max_current)
        print("mid_meter:",self.application.settings.deviceSettings.mid_meter)
        print("midMeterSlaveAddress:",self.application.settings.deviceSettings.midMeterSlaveAddress)
        print("externalMidMeter:",self.application.settings.deviceSettings.externalMidMeter)
        print("externalMidMeterSlaveAddress:",self.application.settings.deviceSettings.externalMidMeterSlaveAddress)
        print("username:",self.application.settings.deviceSettings.username)
        print("password:",self.application.settings.deviceSettings.password)
        print("----------------------------> Local List")
        print("localList:",self.application.settings.localList)
        
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
            # print("get_dns_settings:",data_dict,"\n")
            self.application.settings.dnsSettings.dnsEnable = data_dict["dnsEnable"]
            self.application.settings.dnsSettings.DNS1 = data_dict["dns1"]
            self.application.settings.dnsSettings.DNS2 = data_dict["dns2"]
        except Exception as e:
            print(datetime.now(),"get_dns_settings Exception:",e)
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
            # print("get_ethernet_settings",data_dict,"\n")
            self.application.settings.ethernetSettings.ethernetEnable = data_dict["ethernetEnable"]
            self.application.settings.ethernetSettings.dhcpcEnable = data_dict["dhcpcEnable"]
            self.application.settings.ethernetSettings.ip = data_dict["ip"]
            self.application.settings.ethernetSettings.netmask = data_dict["netmask"]
            self.application.settings.ethernetSettings.gateway = data_dict["gateway"]
        except Exception as e:
            print(datetime.now(),"get_ethernet_settings Exception:",e)
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
            # print("get_network_priority",data_dict,"\n")
            self.application.settings.networkPriority.enableWorkmode = data_dict["enableWorkmode"]
            self.application.settings.networkPriority.first = data_dict["first"]
            self.application.settings.networkPriority.second = data_dict["second"]
            self.application.settings.networkPriority.third = data_dict["third"]
        except Exception as e:
            print(datetime.now(),"get_network_priority Exception:",e)
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
            # print("get_settings_4g",data_dict,"\n")
            self.application.settings.settings4G.apn = data_dict["apn"]
            self.application.settings.settings4G.user = data_dict["user"]
            self.application.settings.settings4G.password = data_dict["password"]
            self.application.settings.settings4G.pin = data_dict["pin"]
            self.application.settings.settings4G.enableModification = data_dict["enableModification"]
        except Exception as e:
            print(datetime.now(),"get_settings_4g Exception:",e)
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
            # print("get_wifi_settings",data_dict,"\n")
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
            print(datetime.now(),"get_wifi_settings Exception:",e)
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
            # print("get_ocpp_settings",data_dict,"\n")
            self.application.settings.ocppSettings.domainName = data_dict["domainName"]
            self.application.settings.ocppSettings.port = data_dict["port"]
            self.application.settings.ocppSettings.sslEnable = data_dict["sslEnable"]
            self.application.settings.ocppSettings.authorizationKey = data_dict["authorizationKey"]
            self.application.settings.ocppSettings.path = data_dict["path"]
            self.application.settings.ocppSettings.chargePointId = data_dict["chargePointId"]
        except Exception as e:
            print(datetime.now(),"get_ocpp_settings Exception:",e)
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
            # print("get_functions_enable",data_dict,"\n")
            self.application.settings.functionsEnable.card_type = data_dict["card_type"]
            self.application.settings.functionsEnable.whether_to_open_the_qr_code_process = data_dict["whether_to_open_the_qr_code_process"]
            self.application.settings.functionsEnable.local_startup_whether_to_go_ocpp_background = data_dict["local_startup_whether_to_go_ocpp_background"]
            self.application.settings.functionsEnable.whether_to_transfer_private_data = data_dict["whether_to_transfer_private_data"]
        except Exception as e:
            print(datetime.now(),"get_functions_enable Exception:",e)
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
            # print("get_bluetooth_settings",data_dict,"\n")
            self.application.settings.bluetoothSettings.bluetooth_enable = data_dict["bluetooth_enable"]
            self.application.settings.bluetoothSettings.pin = data_dict["pin"]
            self.application.settings.bluetoothSettings.bluetooth_name = data_dict["bluetooth_name"]
        except Exception as e:
            print(datetime.now(),"get_bluetooth_settings Exception:",e)
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
            # print("get_timezoon_settings",data_dict,"\n")
            self.application.settings.timezoonSettings.timezone = data_dict["timezone"]
        except Exception as e:
            print(datetime.now(),"get_timezoon_settings Exception:",e)
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
            # print("get_firmware_version",data_dict,"\n")
            self.application.settings.firmwareVersion.version = data_dict["version"]
        except Exception as e:
            print(datetime.now(),"get_firmware_version Exception:",e)
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
                self.application.settings.deviceSettings.availability = AvailabilityType.operative
            elif data_dict["availability"] == AvailabilityType.inoperative.value:
                self.application.settings.deviceSettings.availability = AvailabilityType.inoperative
            else:
                self.application.settings.deviceSettings.availability = AvailabilityType.operative
        except Exception as e:
            print(datetime.now(),"get_availability Exception:",e)
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
            self.application.settings.deviceSettings.max_current = int(data_dict["maxcurrent"])
        except Exception as e:
            print(datetime.now(),"get_max_current Exception:",e)
        return data_dict
    
    def get_device_settings(self):
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
            self.application.settings.deviceSettings.mid_meter = bool(data_dict["midMeter"])
            self.application.settings.deviceSettings.midMeterSlaveAddress = int(data_dict["midMeterSlaveAddress"])
            self.application.settings.deviceSettings.externalMidMeter = bool(data_dict["externalMidMeter"])
            self.application.settings.deviceSettings.externalMidMeterSlaveAddress = int(data_dict["externalMidMeterSlaveAddress"])
            return bool(data_dict["midMeter"])
        except Exception as e:
            print(datetime.now(),"get_device_settings Exception:",e)
    
    def get_user_login(self):
        try:
            data_dict = {}
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM user_login"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            # print("\n get_local_list",data)
            for row in data:
                data_dict["UserName"] = row[0]
                data_dict["Password"] = row[1]
            self.application.settings.deviceSettings.username = data_dict["UserName"]
            self.application.settings.deviceSettings.password = data_dict["Password"]
            return data_dict
        except Exception as e:
            print(datetime.now(),"get_user_login Exception:",e)
            
    def get_local_list(self):
        id_tag_list = []
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM local_list"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            # print("\n get_local_list",data)
            for id in data:
                id_tag_list.append(id[0])
            self.application.settings.localList = id_tag_list
            return id_tag_list
        except Exception as e:
            print(datetime.now(),"get_bluetooth_settings Exception:",e)
             
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
            print(datetime.now(),"set_dns_settings Exception:",e)

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
            print(datetime.now(),"set_ethernet_settings Exception:",e)

    def set_network_priority(self,enableWorkmode,first,second,third):
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
            print(datetime.now(),"set_network_priority Exception:",e)
    
    def set_settings_4g(self,apn,user,password,enableModification,pin):
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
            print(datetime.now(),"set_settings_4g Exception:",e)
    
    def set_wifi_settings(self,wifiEnable,mod,ssid,password,encryptionType,wifidhcpcEnable,ip,netmask,gateway):
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
            print(datetime.now(),"set_wifi_settings Exception:",e)
            
    def set_ocpp_settings(self,domainName,port,sslEnable,authorizationKey,path,chargePointId):
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
            
            self.settings_database.close()
            
            self.application.settings.ocppSettings.domainName = domainName
            self.application.settings.ocppSettings.port = port
            self.application.settings.ocppSettings.sslEnable = sslEnable
            self.application.settings.ocppSettings.authorizationKey = authorizationKey
            self.application.settings.ocppSettings.path = path
            self.application.settings.ocppSettings.chargePointId = chargePointId
        except Exception as e:
            print(datetime.now(),"set_ocpp_settings Exception:",e)
            
    def set_functions_enable(self,card_type,whether_to_open_the_qr_code_process,local_startup_whether_to_go_ocpp_background,whether_to_transfer_private_data):
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
            print(datetime.now(),"set_functions_enable Exception:",e)
            
    def set_bluetooth_settings(self,bluetooth_enable,pin,bluetooth_name):
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
            print(datetime.now(),"set_bluetooth_settings Exception:",e)
            
    def set_timezone_settings(self,timezone):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE timezoon_settings SET key = ? WHERE value = ?"
            
            value = (timezone,"timezone")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.timezoonSettings.timezone = timezone
        except Exception as e:
            print(datetime.now(),"set_timezone_settings Exception:",e)
            
    def set_firmware_version(self,version):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE firmware_version SET key = ? WHERE value = ?"
            
            value = (version,"version")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.settings.firmwareVersion.version = version
        except Exception as e:
            print(datetime.now(),"set_firmware_version Exception:",e)
            
    def set_availability(self,availability):
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
            print(datetime.now(),"set_availability Exception:",e)
            
    def set_max_current(self,maxcurrent):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE device_settings SET key = ? WHERE value = ?"
            
            value = (maxcurrent,"maxcurrent")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            self.application.max_current = maxcurrent
            
        except Exception as e:
            print(datetime.now(),"set_max_current Exception:",e)
    
    def set_local_list(self,local_list:list):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            self.cursor.execute('DELETE FROM local_list;')
            self.settings_database.commit()
            for idTag in local_list:
                query = '''INSERT INTO local_list (idTag) VALUES (?);'''
                self.cursor.execute(query, (idTag,))
                self.settings_database.commit()
            self.settings_database.close()
        except Exception as e:
            print(datetime.now(),"set_local_list Exception:",e)
            
    def set_password(self,password):
        try:
            self.settings_database = sqlite3.connect('/root/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "UPDATE user_login SET Password = ? WHERE UserName = ?"
            
            value = (password,"HCAC")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            self.settings_database.close()
            
            return True
        except Exception as e:
            print(datetime.now(),"set_password Exception:",e)
            return False
        