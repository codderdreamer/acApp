import sqlite3
import time
class DatabaseModule():
    def __init__(self,application) -> None:
        self.application = application
        self.settings_database = sqlite3.connect('Settings.sqlite')
        self.cursor = self.settings_database.cursor()
        
        self.get_dns_settings()
        self.get_ethernet_settings()
        self.get_network_priority()
        self.get_settings_4g()
        self.get_wifi_settings()

    def settings_db_connect(self):
        self.settings_database = sqlite3.connect('Settings.sqlite')
        self.cursor = self.settings_database.cursor()
        
    def get_dns_settings(self):
        try:
            data_dict = {}
            query = "SELECT * FROM dns_settings"
            self.cursor.execute(query)
            data = self.cursor.fetchall()
            for row in data:
                data_dict[row[0]] = row[1]
            print("get_dns_settings:",data_dict,"\n")
            self.application.settings.dnsSettings.DNS1 = data_dict["dns1"]
            self.application.settings.dnsSettings.DNS2 = data_dict["dns2"]
        except Exception as e:
            print(e)
        return data_dict
    
    def get_ethernet_settings(self):
        data_dict = {}
        query = "SELECT * FROM ethernet_settings"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        for row in data:
            data_dict[row[0]] = row[1]
        print("get_ethernet_settings",data_dict,"\n")
        self.application.settings.ethernetSettings.DHCPActivate = data_dict["dhcpActivate"]
        self.application.settings.ethernetSettings.ip = data_dict["ip"]
        self.application.settings.ethernetSettings.netmask = data_dict["netmask"]
        self.application.settings.ethernetSettings.gateway = data_dict["gateway"]
        return data_dict
    
    def get_network_priority(self):
        data_dict = {}
        query = "SELECT * FROM network_priority"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        for row in data:
            data_dict[row[0]] = row[1]
        print("get_network_priority",data_dict,"\n")
        self.application.settings.networkPriority.first = data_dict["first"]
        self.application.settings.networkPriority.second = data_dict["second"]
        self.application.settings.networkPriority.third = data_dict["third"]
        return data_dict
    
    def get_settings_4g(self):
        data_dict = {}
        query = "SELECT * FROM settings_4g"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        for row in data:
            data_dict[row[0]] = row[1]
        print("get_settings_4g",data_dict,"\n")
        self.application.settings.settings4G.APN = data_dict["apn"]
        self.application.settings.settings4G.user = data_dict["user"]
        self.application.settings.settings4G.password = data_dict["password"]
        self.application.settings.settings4G.activate = data_dict["activate"]
        self.application.settings.settings4G.pin = data_dict["pin"]
        self.application.settings.settings4G.encryptionType = data_dict["encryptionType"]
        return data_dict
    
    def get_wifi_settings(self):
        data_dict = {}
        query = "SELECT * FROM wifi_settings"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        for row in data:
            data_dict[row[0]] = row[1]
        print("get_wifi_settings",data_dict,"\n")
        self.application.settings.settings4G.wifiActivate = data_dict["wifiActivate"]
        self.application.settings.settings4G.mod = data_dict["mod"]
        self.application.settings.settings4G.ssid = data_dict["ssid"]
        self.application.settings.settings4G.password = data_dict["password"]
        self.application.settings.settings4G.encryptionType = data_dict["encryptionType"]
        self.application.settings.settings4G.netmask = data_dict["netmask"]
        self.application.settings.settings4G.gateway = data_dict["gateway"]
        return data_dict
    
    def set_dns_settings(self):
        query = "UPDATE settings_4g SET key = ? WHERE value = ?"
        self.cursor.execute(query,task)
        self.settings_database.commit()
    
    def set_ethernet_settings(self):
        pass
    
    def set_network_priority(self):
        pass
    
    def set_settings_4g(self):
        pass
    
    def set_wifi_settings(self):
        pass
    
settings_database = sqlite3.connect('Settings.sqlite')
cursor = settings_database.cursor()
query = "UPDATE dns_settings SET key = ? WHERE value = ?"
task = ("deneme","dns1")
cursor.execute(query,task)
settings_database.commit()
    
    
