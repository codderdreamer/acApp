import json

class Settings():
    def __init__(self) -> None:
        self.networkPriority = NetworkPriority()
        self.settings4G = Settings4G()
        self.ethernetSettings = EthernetSettings()
        self.dnsSettings = DNSSettings()
        self.wifiSettings = WifiSettings()
        
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
        return json_string
    
    def get_ethernet_settings(self):
        command = {
                    "Command" : "EthernetSettings",
                    "Data" : {
                                "ethernetEnable" : bool(self.ethernetSettings.ethernetEnable=="True"),
                                "ip" : self.ethernetSettings.ip,
                                "netmask" : self.ethernetSettings.netmask,
                                "gateway" : self.ethernetSettings.gateway
                            }
                }
        json_string = json.dumps(command)
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
        return json_string

        
    
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
        
