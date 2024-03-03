import json
from datetime import datetime
import time
from threading import Thread
from src.enums import *

class Settings():
    def __init__(self,application) -> None:
        self.application = application
        self.networkPriority = NetworkPriority()
        self.settings4G = Settings4G()
        self.ethernetSettings = EthernetSettings()
        self.dnsSettings = DNSSettings()
        self.wifiSettings = WifiSettings()
        self.ocppSettings = OcppSettings()
        self.functionsEnable = FunctionsEnable()
        self.bluetoothSettings = BluetoothSettings()
        self.timezoonSettings = TimeZoneSettings()
        self.firmwareVersion = FirmwareVersion()
        self.deviceStatus = DeviceStatus()
        self.networkip = NeworkIP()
        
        self.change_ocpp = False
        
        self.__websocketIp = None
        
    @property
    def websocketIp(self):
        return self.__websocketIp

    @websocketIp.setter
    def websocketIp(self, value):
        print("websocketIp",self.__websocketIp,value)
        if self.__websocketIp == None:
            self.__websocketIp = value
            self.set_websocket_ip(value)
            self.application.flaskModule.host = self.__websocketIp
            self.application.flaskModule.start()
            print("self.application.flaskModule.start()")
        elif self.__websocketIp != value:
            print("if self.__websocketIp != value:")
            self.application.flaskModule.stop_event.set()
            print("self.application.flaskModule.stop_event.set()")
            self.__websocketIp = value
            print("self.set_websocket_ip(value)")
            self.set_websocket_ip(value)
            self.application.flaskModule.host = self.__websocketIp
            self.application.flaskModule.start()
            
    def set_websocket_ip(self,ip):
        try:
            print("ip",ip)
            data = {
                    "ip" : ip
                }
            print("data",data)
            with open("/root/acApp/client/build/websocket.json", "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(datetime.now(),"set_websocket_ip Exception:",e)
        
    def get_network_priority(self):
        command = {
                    "Command" : "NetworkPriority",
                    "Data" : {
                                "enableWorkmode" : bool(self.networkPriority.enableWorkmode=="True"),
                                "1" : self.networkPriority.first,
                                "2" : self.networkPriority.second,
                                "3" : self.networkPriority.third
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_Settings4G(self):
        command = {
                    "Command" : "4GSettings",
                    "Data" : {
                                "enableModification" : bool(self.settings4G.enableModification=="True"),
                                "apn" : self.settings4G.apn,
                                "user" : self.settings4G.user,
                                "password" : self.settings4G.password,
                                "pin" : self.settings4G.pin,
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_ethernet_settings(self):
        # print("get_ethernet_settings func")
        command = {
                    "Command" : "EthernetSettings",
                    "Data" : {
                                "ethernetEnable" : bool(self.ethernetSettings.ethernetEnable=="True"),
                                "dhcpcEnable" : bool(self.ethernetSettings.dhcpcEnable=="True"),
                                "ip" : self.ethernetSettings.ip,
                                "netmask" : self.ethernetSettings.netmask,
                                "gateway" : self.ethernetSettings.gateway
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_dns_settings(self):
        command = {
                    "Command" : "DNSSettings",
                    "Data" : {
                                "dnsEnable" : bool(self.dnsSettings.dnsEnable=="True"),
                                "DNS1" : self.dnsSettings.DNS1,
                                "DNS2" : self.dnsSettings.DNS2
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_wifi_settings(self):
        command = {
                    "Command" : "WifiSettings",
                    "Data" : {
                                "wifiEnable" : bool(self.wifiSettings.wifiEnable=="True"),
                                "mod" : self.wifiSettings.mod,
                                "ssid" : self.wifiSettings.ssid,
                                "password" : self.wifiSettings.password,
                                "encryptionType" : self.wifiSettings.encryptionType,
                                "wifidhcpcEnable" : bool(self.wifiSettings.wifidhcpcEnable=="True"),
                                "ip" : self.wifiSettings.ip,
                                "netmask" : self.wifiSettings.netmask,
                                "gateway" : self.wifiSettings.gateway
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_ocpp_settings(self):
        command = {
                    "Command" : "OcppSettings",
                    "Data" : {
                                "domainName" : self.ocppSettings.domainName,
                                "port" : self.ocppSettings.port,
                                "sslEnable" : self.ocppSettings.sslEnable,
                                "authorizationKey" : self.ocppSettings.authorizationKey,
                                "path" : self.ocppSettings.path,
                                "chargePointId" : self.ocppSettings.chargePointId
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_functions_enable(self):
        command = {
                    "Command" : "FunctionsEnable",
                    "Data" : {
                                "card_type" : self.functionsEnable.card_type,
                                "whether_to_open_the_qr_code_process" : self.functionsEnable.whether_to_open_the_qr_code_process,
                                "local_startup_whether_to_go_ocpp_background" : self.functionsEnable.local_startup_whether_to_go_ocpp_background,
                                "whether_to_transfer_private_data" : self.functionsEnable.whether_to_transfer_private_data
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_bluetooth_settings(self):
        command = {
                    "Command" : "BluetoothSettings",
                    "Data" : {
                                "bluetooth_enable" : self.bluetoothSettings.bluetooth_enable,
                                "pin" : self.bluetoothSettings.pin,
                                "bluetooth_name" : self.bluetoothSettings.bluetooth_name
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_timezoon_settings(self):
        command = {
                    "Command" : "TimeZoneSettings",
                    "Data" : {
                                "timezone" : self.timezoonSettings.timezone
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_firmware_version(self):
        command = {
                    "Command" : "FirmwareVersion",
                    "Data" : {
                                "version" : self.firmwareVersion.version
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_charging(self):
        duration = None
        if self.application.ev.start_date != None and self.application.ev.start_date != "":
            date_obj = datetime.strptime(self.application.ev.start_date, "%d-%m-%Y %H:%M")
            second = int(time.time() - time.mktime(date_obj.timetuple()))
            hour, remainder = divmod(second, 3600)
            minute, second = divmod(remainder, 60)

            # Formatlı string olarak saat:dakika:saniye
            duration = f"{hour:02d}:{minute:02d}:{second:02d}"
        
        command = {
                    "Command" : "Charging",
                    "Data" : {
                                "charge" : self.application.ev.charge,
                                "start_date" : self.application.ev.start_date,
                                "duration" : duration,
                                "current_L1" : self.application.ev.current_L1,
                                "current_L2" : self.application.ev.current_L2,
                                "current_L3" : self.application.ev.current_L3,
                                "voltage_L1" : self.application.ev.voltage_L1,
                                "voltage_L2" : self.application.ev.voltage_L2,
                                "voltage_L3" : self.application.ev.voltage_L3,
                                "power" : self.application.ev.power,
                                "energy" : self.application.ev.energy,
                                "temperature" : self.application.ev.temperature
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_device_status(self):
        command = {
                    "Command" : "DeviceStatus",
                    "Data" : {
                                "linkStatus" : self.deviceStatus.linkStatus,
                                "strenghtOf4G" : self.deviceStatus.strenghtOf4G,
                                "networkCard" : self.deviceStatus.networkCard,
                                "stateOfOcpp" : self.deviceStatus.stateOfOcpp
                            }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
    
    def get_maxcurrent(self):
        command = {
                    "Command": "ACCurrent",
                    "Data": {
                                "maxcurrent": self.application.max_current
                    }
                }
        json_string = json.dumps(command)
        # print("Gönderilen:",command)
        return json_string
        
    def set_network_priority(self,sjon):
        try:
            if(sjon["Command"] == "NetworkPriority"):
                enableWorkmode = str(sjon["Data"]["enableWorkmode"])
                first = sjon["Data"]["1"]
                second = sjon["Data"]["2"]
                third = sjon["Data"]["3"]
                self.application.databaseModule.set_network_priority(enableWorkmode,first,second,third)
                Thread(target=self.application.softwareSettings.set_network_priority,daemon=True).start()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_network_priority())
        except Exception as e:
            print(datetime.now(),"set_network_priority Exception:",e)
    
    def set_Settings4G(self,sjon):
        try:
            if(sjon["Command"] == "4GSettings"):
                enableModification = str(sjon["Data"]["enableModification"])
                apn = sjon["Data"]["apn"]
                user = sjon["Data"]["user"]
                password = sjon["Data"]["password"]
                pin = sjon["Data"]["pin"]
                self.application.databaseModule.set_settings_4g(apn,user,password,enableModification,pin)
                self.application.softwareSettings.set_4G()
                Thread(target=self.application.softwareSettings.set_network_priority,daemon=True).start()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_Settings4G())
        except Exception as e:
            print(datetime.now(),"set_Settings4G Exception:",e)
        
    def set_ethernet_settings(self,sjon):
        try:
            if(sjon["Command"] == "EthernetSettings"):
                ethernetEnable = str(sjon["Data"]["ethernetEnable"])
                dhcpcEnable = str(sjon["Data"]["dhcpcEnable"])
                ip = sjon["Data"]["ip"]
                netmask = sjon["Data"]["netmask"]
                gateway = sjon["Data"]["gateway"]
                self.application.databaseModule.set_ethernet_settings(ethernetEnable,dhcpcEnable,ip,netmask,gateway)
                self.application.softwareSettings.set_eth()
                Thread(target=self.application.softwareSettings.set_network_priority,daemon=True).start()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_ethernet_settings())
        except Exception as e:
            print(datetime.now(),"set_ethernet_settings Exception:",e)
            
    def set_dns_settings(self,sjon):
        try:
            if(sjon["Command"] == "DNSSettings"):
                dnsEnable = str(sjon["Data"]["dnsEnable"])
                dns1 = sjon["Data"]["DNS1"]
                dns2 = sjon["Data"]["DNS2"]
                self.application.databaseModule.set_dns_settings(dnsEnable,dns1,dns2)
                self.application.softwareSettings.set_dns()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_dns_settings())
        except Exception as e:
            print(datetime.now(),"set_dns_settings Exception:",e)
            
    def set_wifi_settings(self,sjon):
        try:
            if(sjon["Command"] == "WifiSettings"):
                wifiEnable = str(sjon["Data"]["wifiEnable"])
                mod = sjon["Data"]["mod"]
                ssid = sjon["Data"]["ssid"]
                password = sjon["Data"]["password"]
                encryptionType = sjon["Data"]["encryptionType"]
                wifidhcpcEnable = str(sjon["Data"]["wifidhcpcEnable"])
                ip = sjon["Data"]["ip"]
                netmask = sjon["Data"]["netmask"]
                gateway = sjon["Data"]["gateway"]
                self.application.databaseModule.set_wifi_settings(wifiEnable,mod,ssid,password,encryptionType,wifidhcpcEnable,ip,netmask,gateway)
                self.application.softwareSettings.set_wifi()
                Thread(target=self.application.softwareSettings.set_network_priority,daemon=True).start()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_wifi_settings())
        except Exception as e:
            print(datetime.now(),"set_wifi_settings Exception:",e)
            
    def set_ocpp_settings(self,sjon):
        try:
            if(sjon["Command"] == "OcppSettings"):
                domainName = str(sjon["Data"]["domainName"])
                port = sjon["Data"]["port"]
                sslEnable = sjon["Data"]["sslEnable"]
                authorizationKey = sjon["Data"]["authorizationKey"]
                path = sjon["Data"]["path"]
                chargePointId = sjon["Data"]["chargePointId"]
                self.application.databaseModule.set_ocpp_settings(domainName,port,sslEnable,authorizationKey,path,chargePointId)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_ocpp_settings())
                self.change_ocpp = True
        except Exception as e:
            print(datetime.now(),"set_ocpp_settings Exception:",e)
        
    def set_functions_enable(self,sjon):
        try:
            if(sjon["Command"] == "FunctionsEnable"):
                card_type = str(sjon["Data"]["card_type"])
                whether_to_open_the_qr_code_process = sjon["Data"]["whether_to_open_the_qr_code_process"]
                local_startup_whether_to_go_ocpp_background = sjon["Data"]["local_startup_whether_to_go_ocpp_background"]
                whether_to_transfer_private_data = sjon["Data"]["whether_to_transfer_private_data"]
                self.application.databaseModule.set_functions_enable(card_type,whether_to_open_the_qr_code_process,local_startup_whether_to_go_ocpp_background,whether_to_transfer_private_data)
                self.application.softwareSettings.set_functions_enable()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_functions_enable())
        except Exception as e:
            print(datetime.now(),"set_functions_enable Exception:",e)
    
    def set_bluetooth_settings(self,sjon):
        try:
            if(sjon["Command"] == "BluetoothSettings"):
                bluetooth_enable = str(sjon["Data"]["bluetooth_enable"])
                pin = sjon["Data"]["pin"]
                bluetooth_name = sjon["Data"]["bluetooth_name"]
                self.application.databaseModule.set_bluetooth_settings(bluetooth_enable,pin,bluetooth_name)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_bluetooth_settings())
        except Exception as e:
            print(datetime.now(),"set_bluetooth_settings Exception:",e)
            
    def set_timezoon_settings(self,sjon):
        try:
            if(sjon["Command"] == "TimeZoneSettings"):
                timezone = str(sjon["Data"]["timezone"])
                self.application.databaseModule.set_timezone_settings(timezone)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_timezoon_settings())
                self.application.softwareSettings.set_timezoon()
        except Exception as e:
            print(datetime.now(),"set_timezoon_settings Exception:",e)
    
    def set_firmware_version(self,sjon):
        try:
            if(sjon["Command"] == "FirmwareVersion"):
                version = str(sjon["Data"]["version"])
                self.application.databaseModule.set_firmware_version(version)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_firmware_version())
        except Exception as e:
            print(datetime.now(),"set_firmware_version Exception:",e)
            
    def set_maxcurrent(self,sjon):
        try:
            if(sjon["Command"] == "ACCurrent"):
                maxcurrent = str(sjon["Data"]["maxcurrent"])
                self.application.databaseModule.set_max_current(maxcurrent)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_maxcurrent())
        except Exception as e:
            print(datetime.now(),"set_maxcurrent Exception:",e)
            
    def set_start_transaction(self,sjon):
        try:
            if(sjon["Command"] == "StartTransaction"):
                print("set_start_transaction")
                self.application.ev.start_stop_authorize = True
        except Exception as e:
            print(datetime.now(),"set_start_transaction Exception:",e)
            
    def set_stop_transaction(self,sjon):
        try:
            if(sjon["Command"] == "StopTransaction"):
                self.application.deviceState = DeviceState.STOPPED_BY_USER
        except Exception as e:
            print(datetime.now(),"set_stop_transaction Exception:",e)
            

    
class NetworkPriority():
    def __init__(self) -> None:
        self.enableWorkmode = None
        self.first = None
        self.second = None
        self.third = None

class Settings4G():
    def __init__(self) -> None:
        self.apn = None
        self.user = None
        self.password = None
        self.pin = None
        self.enableModification = None
        
class EthernetSettings():
    def __init__(self) -> None:
        self.ethernetEnable = None
        self.dhcpcEnable = None
        self.ip = None
        self.netmask = None
        self.gateway = None

class DNSSettings():
    def __init__(self) -> None:
        self.dnsEnable = None
        self.DNS1 = None
        self.DNS2 = None

class WifiSettings():
    def __init__(self) -> None:
        self.wifiEnable = None
        self.mod = None
        self.ssid = None
        self.password = None
        self.encryptionType = None
        self.wifidhcpcEnable = None
        self.ip = None
        self.netmask = None
        self.gateway = None
        
class OcppSettings():
    def __init__(self) -> None:
        self.domainName = None
        self.port = None
        self.sslEnable = None
        self.authorizationKey = None
        self.path = None
        self.chargePointId = None
        
class FunctionsEnable():
    def __init__(self) -> None:
        self.card_type = None
        self.whether_to_open_the_qr_code_process = None
        self.local_startup_whether_to_go_ocpp_background = None
        self.whether_to_transfer_private_data = None
        
class BluetoothSettings():
    def __init__(self) -> None:
        self.bluetooth_enable = None
        self.pin = None
        self.bluetooth_name = None
        
class TimeZoneSettings():
    def __init__(self) -> None:
        self.timezone = None
        
class FirmwareVersion():
    def __init__(self) -> None:
        self.version = None
        
class DeviceStatus():
    def __init__(self) -> None:
        self.linkStatus = None
        self.strenghtOf4G = None
        self.networkCard = None
        self.stateOfOcpp = None  

class ACCurrent():
    def __init__(self) -> None:
        self.maxcurrent = None
        
class NeworkIP():
    def __init__(self) -> None:
        self.eth1 = None
        self.ppp0 = None
        self.wlan0 = None
        