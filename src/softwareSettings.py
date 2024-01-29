import os
import time
import ipaddress
import json
import socket
import subprocess
import re
import fcntl
import struct
import psutil
from src.enums import *
from datetime import datetime

class SoftwareSettings():
    def __init__(self,application) -> None:
        self.application = application
        
    def set_eth(self):
        try:
            ethernetEnable = self.application.settings.ethernetSettings.ethernetEnable
            dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
            ip = self.application.settings.ethernetSettings.ip
            netmask = self.application.settings.ethernetSettings.netmask
            gateway = self.application.settings.ethernetSettings.gateway
            print("\n************* Ethrenet Configration ************")
            print(f"*** ethernetEnable {ethernetEnable}")
            print(f"*** dhcpcEnable {dhcpcEnable}")
            print(f"*** ip {ip}")
            print(f"*** netmask {netmask}")
            print(f"*** gateway {gateway}")
            print("************* - ************\n")
            if ethernetEnable == "True":
                if dhcpcEnable == "True":
                    netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                    netmask_prefix_length = netmask_obj.prefixlen
                    os.system("nmcli con delete static-eth1")
                    os.system("stty erase ^h")
                    set_eth = 'nmcli con add con-name "static-eth1" ifname eth1 type ethernet ip4 \\{0}/{1} gw4 {2}'.format(ip,netmask_prefix_length,gateway)
                    os.system(set_eth)
                    os.system('nmcli con up "static-eth1" ifname eth1')
                    data = {
                        "ip" : ip
                    }
                    with open("/root/acApp/client/build/websocket.json", "w") as file:
                        json.dump(data, file)
                        print("ip yazıldı")
                else:
                    os.system("nmcli con delete static-eth1")
            else:
                print("Statik eth1 varsa siliniyor")
                os.system("nmcli con delete static-eth1")    
            time.sleep(7)
            if ethernetEnable == "True":
                if dhcpcEnable == "False":
                    try:
                        self.application.settings.ethernetSettings.ip = str(socket.gethostbyname(socket.gethostname()))
                    except Exception as e:
                        print( "ip" ,e)
                
                    try:
                        proc = subprocess.Popen(['ifconfig', "eth1"], stdout=subprocess.PIPE)
                        output, _ = proc.communicate()
                        netmask = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', str(output))
                        if netmask:
                            self.application.settings.ethernetSettings.netmask = str(netmask.group(1))
                    except Exception as e:
                        print( "netmask" ,e)
                    try:
                        proc = subprocess.Popen(['ip', 'route'], stdout=subprocess.PIPE)
                        output, _ = proc.communicate()
                        gateway = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', str(output))
                        if gateway:
                            self.application.settings.ethernetSettings.gateway = str(gateway.group(1))
                    except Exception as e:
                        print( "gateway" ,e)
                    
                    data = {
                        "ip" : self.application.settings.ethernetSettings.ip
                    }
                    with open("/root/acApp/client/build/websocket.json", "w") as file:
                        json.dump(data, file)
                        print("ip yazıldı")
                    print(self.application.settings.ethernetSettings.ip)
                    print(self.application.settings.ethernetSettings.netmask)
                    print(self.application.settings.ethernetSettings.gateway)
        except Exception as e:
            print(datetime.now(),"find_adapter Exception:",e)
            
    def set_dns(self):
        try:
            dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
            dnsEnable = self.application.settings.dnsSettings.dnsEnable
            DNS1 = self.application.settings.dnsSettings.DNS1
            DNS2 = self.application.settings.dnsSettings.DNS2
            if dhcpcEnable == "True":
                if dnsEnable == "True":
                    setDns = 'nmcli con modify "static-eth1" ipv4.dns "{0},{1}"'.format(DNS1,DNS2)
                    os.system(setDns)
                    os.system('nmcli con up "static-eth1" ifname eth1')
        except Exception as e:
            print(datetime.now(),"set_dns Exception:",e)
          
    def set_4G(self):
        try:
            connection_name = "ppp0"
            apn = self.application.settings.settings4G.apn
            user = self.application.settings.settings4G.user
            password = self.application.settings.settings4G.password
            pin = self.application.settings.settings4G.pin
            enableModification = self.application.settings.settings4G.enableModification
            if enableModification=="True":
                os.system("nmcli connection delete ppp0")
                time.sleep(3)
                os.system("gpio-test.64 w d 20 1")
                time.sleep(5)
                add_connection_string = """nmcli connection add con-name {0} ifname ttyUSB2 autoconnect yes \\type gsm apn {1} user {2} password {3}""".format(connection_name,apn,user,password)
                print(add_connection_string)
                os.system(add_connection_string)
                
                time.sleep(30)
                proc = subprocess.Popen(['ifconfig', "ppp0"], stdout=subprocess.PIPE)
                output, _ = proc.communicate()
                inet = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', str(output))
                print("inet------>" ,inet.group(1))
            else:
                os.system("nmcli connection delete ppp0")
        except Exception as e:
            print(datetime.now(),"set_4G Exception:",e)
    
    def set_wifi(self):
        try:
            wifiEnable = self.application.settings.wifiSettings.wifiEnable
            mod = self.application.settings.wifiSettings.mod
            ssid = self.application.settings.wifiSettings.ssid
            password = self.application.settings.wifiSettings.password
            encryptionType = self.application.settings.wifiSettings.encryptionType
            wifidhcpcEnable = self.application.settings.wifiSettings.wifidhcpcEnable
            ip = self.application.settings.wifiSettings.ip
            netmask = self.application.settings.wifiSettings.netmask
            gateway = self.application.settings.wifiSettings.gateway
            print("\n************* Wifi Configration ************")
            print(f"*** wifiEnable {wifiEnable}")
            print(f"*** mod {mod}")
            print(f"*** ssid {ssid}")
            print(f"*** password {password}")
            print(f"*** encryptionType {encryptionType}")
            print(f"*** wifidhcpcEnable {wifidhcpcEnable}")
            print(f"*** ip {ip}")
            print(f"*** netmask {netmask}")
            print("************* - ************\n")
            if mod == "AP":
                subprocess.call(["sh", "/root/acApp/accesspoint_add.sh"] + [ssid,password])
            else:
                if wifiEnable=="True":
                    os.system(f"nmcli con add type wifi ifname wlan0 con-name wifi_connection ssid {ssid}")
                    os.system(f"nmcli connection modify wifi_connection wifi-sec.key-mgmt wpa-psk")
                    os.system(f"nmcli connection modify wifi_connection wifi-sec.psk {password}")
                    if wifidhcpcEnable == "True":
                        netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                        netmask_prefix_length = netmask_obj.prefixlen
                        os.system("nmcli con modify wifi_connection ipv4.method manual")
                        os.system(f"nmcli con modify wifi_connection ipv4.address {ip}/{netmask_prefix_length}")
                        os.system(f"nmcli con modify wifi_connection ipv4.gateway {gateway}")
                    else:
                        try:
                            addresses = psutil.net_if_addrs()
                            if "wlan0" in addresses:
                                for address in addresses["wlan0"]:
                                    if address.family == socket.AF_INET:
                                        self.application.settings.wifiSettings.ip = address.address
                        except Exception as e:
                            print( "ip" ,e)
                        try:
                            proc = subprocess.Popen(['ifconfig', "wlan0"], stdout=subprocess.PIPE)
                            output, _ = proc.communicate()
                            netmask = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', str(output))
                            if netmask:
                                self.application.settings.wifiSettings.netmask = str(netmask.group(1))
                        except Exception as e:
                            print( "netmask" ,e)
                    os.system("nmcli connection up wifi_connection")
                else:
                    os.system("ifconfig wlan0 down")
        except Exception as e:
            print(datetime.now(),"set_wifi Exception:",e)
                  
    def set_network_priority(self):
        time.sleep(10)
        try:
            enableWorkmode = self.application.settings.networkPriority.enableWorkmode
            first = self.application.settings.networkPriority.first
            second = self.application.settings.networkPriority.second
            third = self.application.settings.networkPriority.third
            print("\n")
            print("************* Network Priority Ayarı ************")
            print(f"*** first {first}")
            print(f"*** second {second}")
            print(f"*** third {third}")
            if enableWorkmode == "True":
                if first == "ETH":
                    os.system("ifmetric eth1 100")
                    print("*** ifmetric eth1 100")
                elif first == "WLAN":
                    os.system("ifmetric wlan0 100")
                    print("*** ifmetric wlan0 100")
                elif first == "4G":
                    os.system("ifmetric ppp0 100")
                    print("*** ifmetric ppp0 100")
                    
                if second == "ETH":
                    os.system("ifmetric eth1 300")
                    print("*** ifmetric eth1 300")
                elif second == "WLAN":
                    os.system("ifmetric wlan0 300")
                    print("*** ifmetric wlan0 300")
                elif second == "4G":
                    os.system("ifmetric ppp0 300")
                    print("*** ifmetric ppp0 300")
                    
                if third == "ETH":
                    os.system("ifmetric eth1 700")
                    print("*** ifmetric eth1 700")
                elif third == "WLAN":
                    os.system("ifmetric wlan0 700")
                    print("*** ifmetric wlan0 700")
                elif third == "4G":
                    os.system("ifmetric ppp0 700")
                    print("*** ifmetric ppp0 700")
            print("************* - ************\n")
        except Exception as e:
            print(datetime.now(),"set_network_priority Exception:",e)
    
    def set_functions_enable(self):
        try:
            card_type = self.application.settings.functionsEnable.card_type
            if card_type == CardType.StartStopCard.value:
                self.application.cardType = CardType.StartStopCard
            elif card_type == CardType.LocalPnC.value:
                self.application.cardType = CardType.LocalPnC
            elif card_type == CardType.BillingCard.value:
                self.application.cardType = CardType.BillingCard
        except Exception as e:
            print(datetime.now(),"set_functions_enable Exception:",e)
        
        
        
    
