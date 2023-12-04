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
        
        self.set_dns_settings("2.2.2.2","333")
        self.get_dns_settings()
        
        self.set_ethernet_settings("true","10.30.5.22","22","33")
        self.get_ethernet_settings()
        
        self.set_network_priority("ETH","4G","WLAN")
        self.get_network_priority()
        
        self.set_settings_4g("apn","usr","pass","true","pinn","enc")
        self.get_settings_4g()
        
        self.set_wifi_settings("true","dene","ssid","pass","A","net","255")
        self.get_wifi_settings()
        
        

    def settings_db_connect(self):
        try:
            self.settings_database = sqlite3.connect('Settings.sqlite')
            self.cursor = self.settings_database.cursor()
        except Exception as e:
            print(e)
        
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
        try:
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
        except Exception as e:
            print(e)
        return data_dict
    
    def get_network_priority(self):
        try:
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
        except Exception as e:
            print(e)
        return data_dict
    
    def get_settings_4g(self):
        try:
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
        except Exception as e:
            print(e)
        return data_dict
    
    def get_wifi_settings(self):
        try:
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
        except Exception as e:
            print(e)
        return data_dict
    
    def set_dns_settings(self,dns1:str,dns2:str):
        try:
            query = "UPDATE dns_settings SET key = ? WHERE value = ?"
            value = (dns1,"dns1")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            value = (dns2,"dns2")
            self.cursor.execute(query,value)
            self.settings_database.commit()
        except Exception as e:
            print(e)
    
    def set_ethernet_settings(self,dhcpActivate,ip,netmask,gateway):
        try:
            query = "UPDATE ethernet_settings SET key = ? WHERE value = ?"
            
            value = (dhcpActivate,"dhcpActivate")
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
        except Exception as e:
            print(e)
    
    def set_network_priority(self,first,second,third):
        try:
            query = "UPDATE network_priority SET key = ? WHERE value = ?"
            
            value = (first,"first")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (second,"second")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (third,"third")
            self.cursor.execute(query,value)
            self.settings_database.commit()
        except Exception as e:
            print(e)
    
    def set_settings_4g(self,apn,user,password,activate,pin,encryptionType):
        try:
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
            
            value = (activate,"activate")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (pin,"pin")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (encryptionType,"encryptionType")
            self.cursor.execute(query,value)
            self.settings_database.commit()
        except Exception as e:
            print(e)
    
    def set_wifi_settings(self,wifiActivate,mod,ssid,password,encryptionType,netmask,gateway):
        try:
            query = "UPDATE wifi_settings SET key = ? WHERE value = ?"
            
            value = (wifiActivate,"wifiActivate")
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
            
            value = (netmask,"netmask")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            
            value = (gateway,"gateway")
            self.cursor.execute(query,value)
            self.settings_database.commit()
        except Exception as e:
            print(e)
    
# settings_database = sqlite3.connect('Settings.sqlite')
# cursor = settings_database.cursor()
# query = "UPDATE dns_settings SET key = ? WHERE value = ?"
# task = ("deneme","dns1")
# cursor.execute(query,task)
# settings_database.commit()
    
    
