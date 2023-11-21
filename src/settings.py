
class Settings():
    def __init__(self) -> None:
        self.networkPriority = NetworkPriority()
        self.settings4G = Settings4G()
        self.ethernetSettings = EthernetSettings()
        self.dnsSettings = DNSSettings()
        self.wifiSettings = WifiSettings()

class NetworkPriority():
    def __init__(self) -> None:
        self.first = None
        self.second = None
        self.third = None

class Settings4G():
    def __init__(self) -> None:
        self.APN = None
        self.user = None
        self.password = None
        self.activate = None
        self.pin = None
        self.encryptionType = None
        
class EthernetSettings():
    def __init__(self) -> None:
        self.DHCPActivate = None
        self.ip = None
        self.netmask = None
        self.gateway = None

class DNSSettings():
    def __init__(self) -> None:
        self.DNS1 = None
        self.DNS2 = None

class WifiSettings():
    def __init__(self) -> None:
        self.wifiActivate = None
        self.mod = None
        self.ssid = None
        self.password = None
        self.encryptionType = None
        self.netmask = None
        self.gateway = None
