import json

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
        print("Gönderilen:",command)
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
        print("Gönderilen:",command)
        return json_string
    
    def get_ethernet_settings(self):
        print("get_ethernet_settings func")
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
        print("Gönderilen:",command)
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
        print("Gönderilen:",command)
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
        print("Gönderilen:",command)
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
                            }
                }
        json_string = json.dumps(command)
        print("Gönderilen:",command)
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
        print("Gönderilen:",command)
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
        print("Gönderilen:",command)
        return json_string
    
    def get_timezoon_settings(self):
        command = {
                    "Command" : "TimeZoneSettings",
                    "Data" : {
                                "timezone" : self.timezoonSettings.timezone
                            }
                }
        json_string = json.dumps(command)
        print("Gönderilen:",command)
        return json_string
    
    def get_firmware_version(self):
        command = {
                    "Command" : "FirmwareVersion",
                    "Data" : {
                                "version" : self.firmwareVersion.version
                            }
                }
        json_string = json.dumps(command)
        print("Gönderilen:",command)
        return json_string
    
    def get_charging(self):
        command = {
                    "Command" : "Charging",
                    "Data" : {
                                "charge" : False,
                                "start_date" : self.application.ev.start_date,
                                "duration" : self.application.ev.duration,
                                "current_L1" : self.application.ev.current_L1,
                                "current_L2" : self.application.ev.current_L2,
                                "current_L3" : self.application.ev.current_L3,
                                "voltage_L1" : self.application.ev.voltage_L1,
                                "voltage_L2" : self.application.ev.voltage_L2,
                                "power" : self.application.ev.power,
                                "energy" : self.application.ev.energy
                            }
                }
        json_string = json.dumps(command)
        print("Gönderilen:",command)
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
        
        
        
        