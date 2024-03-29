import sqlite3
import time
from ocpp.v16.enums import *
from datetime import datetime

class DatabaseModule():
    def __init__(self,application) -> None:
        self.application = application
        
    def get_dns_settings(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            data_dict = {}
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            # print("device_settings",data_dict,"\n")
            if data_dict["availability"] == AvailabilityType.operative.value:
                self.application.availability = AvailabilityType.operative
            elif data_dict["availability"] == AvailabilityType.inoperative.value:
                self.application.availability = AvailabilityType.inoperative
            else:
                self.application.availability = AvailabilityType.operative
        except Exception as e:
            print(datetime.now(),"get_availability Exception:",e)
        return data_dict
     
    def get_max_current(self):
        data_dict = {}
        try:
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM device_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            for row in data:
                data_dict[row[0]] = row[1]
            self.application.max_current = int(data_dict["maxcurrent"])
        except Exception as e:
            print(datetime.now(),"get_max_current Exception:",e)
        return data_dict
    
    def set_dns_settings(self,dnsEnable,dns1,dns2):
        try:
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
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
            
    def get_local_list(self):
        id_tag_list = []
        try:
            self.settings_database = sqlite3.connect('/root/acApp/Settings.sqlite')
            self.cursor = self.settings_database.cursor()
            query = "SELECT * FROM local_list"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            self.settings_database.close()
            # print("\n get_local_list",data)
            for id in data:
                id_tag_list.append(id[0])
            return id_tag_list
        except Exception as e:
            print(datetime.now(),"get_bluetooth_settings Exception:",e)
        