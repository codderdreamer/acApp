import os
import time
import ipaddress
import json
import socket
import subprocess
import re
import psutil
from src.enums import *
from datetime import datetime
import requests

class SoftwareSettings():
    def __init__(self,application) -> None:
        self.application = application
        
        self.get_active_ips()
        
    def get_active_ips(self):
        try:
            process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            result = stdout.decode()
            print(result)
            data = result.split("\n")
            # print(data)
        except Exception as e:
            print(datetime.now(),"get_active_ips Exception:",e)
        
    def set_websocket_ip(self,ip):
        try:
            data = {
                    "ip" : ip
                }
            with open("/root/acApp/client/build/websocket.json", "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(datetime.now(),"set_websocket_ip Exception:",e)
        
    def get_connections(self):
        try:
            connections = []
            process = subprocess.Popen(['nmcli', 'con', 'show'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            result = stdout.decode()
            data = result.split("\n")
            for i in range(1,len(data)):
                new_connection = []
                connection = data[i].split()
                if len(connection) > 4:
                    connection_name = ""
                    for j in range(0,len(connection)-3):
                        if j == len(connection)-4:
                            connection_name += connection[j]
                        else:
                            connection_name += connection[j] + " "
                    new_connection.append(connection_name)
                    new_connection.append(connection[-3])
                    new_connection.append(connection[-2])
                    new_connection.append(connection[-1])
                    connections.append(new_connection)
                else:
                    connections.append(connection)
            return connections
        except Exception as e:
            print(datetime.now(),"get_connections Exception:",e)
            
    def delete_connection_type(self,con_type):
        try:
            connections = self.get_connections()
            for connection in connections:
                if con_type in connection:
                    subprocess.run(["nmcli", "con", "delete", connection[0]])
        except Exception as e:
            print(datetime.now(),"delete_connection Exception:",e)
        
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
            
            self.delete_connection_type("ethernet")
            
            if ethernetEnable == "True":
                if dhcpcEnable == "True":
                    netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                    netmask_prefix_length = netmask_obj.prefixlen
                    os.system("nmcli con delete static-eth1")
                    os.system("stty erase ^h")
                    set_eth = 'nmcli con add con-name "static-eth1" ifname eth1 type ethernet ip4 \\{0}/{1} gw4 {2}'.format(ip,netmask_prefix_length,gateway)
                    os.system(set_eth)
                    os.system('nmcli con up "static-eth1" ifname eth1')
                else:
                    os.system("stty erase ^h")
                    set_eth = 'nmcli con add con-name "wire" ifname eth1 type ethernet'
                    os.system(set_eth)
                    os.system('nmcli con up "wire" ifname eth1')
            else:
                self.delete_connection_type("ethernet")
        except Exception as e:
            print(datetime.now(),"set_eth Exception:",e)
        
    def set_eth_old(self):
        try:
            ethernetEnable = self.application.settings.ethernetSettings.ethernetEnable
            dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
            ip = self.application.settings.ethernetSettings.ip
            netmask = self.application.settings.ethernetSettings.netmask
            gateway = self.application.settings.ethernetSettings.gateway
            # print("\n************* Ethrenet Configration ************")
            # print(f"*** ethernetEnable {ethernetEnable}")
            # print(f"*** dhcpcEnable {dhcpcEnable}")
            # print(f"*** ip {ip}")
            # print(f"*** netmask {netmask}")
            # print(f"*** gateway {gateway}")
            # print("************* - ************\n")
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
                else:
                    os.system("nmcli con delete static-eth1")
            else:
                os.system("nmcli con delete static-eth1")    
            time.sleep(7)
            if ethernetEnable == "True":
                if dhcpcEnable == "False":
                    try:
                        self.application.settings.ethernetSettings.ip = str(socket.gethostbyname(socket.gethostname()))
                    except Exception as e:
                        print(datetime.now(),"str(socket.gethostbyname(socket.gethostname())) Exception:",e)
                
                    try:
                        proc = subprocess.Popen(['ifconfig', "eth1"], stdout=subprocess.PIPE)
                        output, _ = proc.communicate()
                        netmask = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', str(output))
                        if netmask:
                            self.application.settings.ethernetSettings.netmask = str(netmask.group(1))
                    except Exception as e:
                        print(datetime.now(),"subprocess.Popen(['ifconfig', 'eth1'], stdout=subprocess.PIPE) Exception:",e)
                    
                    try:
                        proc = subprocess.Popen(['ip', 'route'], stdout=subprocess.PIPE)
                        output, _ = proc.communicate()
                        gateway = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', str(output))
                        if gateway:
                            self.application.settings.ethernetSettings.gateway = str(gateway.group(1))
                    except Exception as e:
                        print(datetime.now(),"subprocess.Popen(['ip', 'route'], stdout=subprocess.PIPE) Exception:",e)
                    
                    data = {
                        "ip" : self.application.settings.ethernetSettings.ip
                    }
                    with open("/root/acApp/client/build/websocket.json", "w") as file:
                        json.dump(data, file)
        except Exception as e:
            print(datetime.now(),"set_eth Exception:",e)
            
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
                # print(add_connection_string)
                os.system(add_connection_string)
                
                # time.sleep(30)
                # proc = subprocess.Popen(['ifconfig', "ppp0"], stdout=subprocess.PIPE)
                # output, _ = proc.communicate()
                # ip = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', str(output))
                # # print("ip------>" ,ip.group(1))
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
            # print("\n************* Wifi Configration ************")
            # print(f"*** wifiEnable {wifiEnable}")
            # print(f"*** mod {mod}")
            # print(f"*** ssid {ssid}")
            # print(f"*** password {password}")
            # print(f"*** encryptionType {encryptionType}")
            # print(f"*** wifidhcpcEnable {wifidhcpcEnable}")
            # print(f"*** ip {ip}")
            # print(f"*** netmask {netmask}")
            # print("************* - ************\n")
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
                            print(datetime.now(),"psutil.net_if_addrs() Exception:",e)
                        try:
                            proc = subprocess.Popen(['ifconfig', "wlan0"], stdout=subprocess.PIPE)
                            output, _ = proc.communicate()
                            netmask = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', str(output))
                            if netmask:
                                self.application.settings.wifiSettings.netmask = str(netmask.group(1))
                        except Exception as e:
                            print(datetime.now(),"subprocess.Popen(['ifconfig', 'wlan0'], stdout=subprocess.PIPE) Exception:",e)
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
            # print("\n")
            # print("************* Network Priority Ayarı ************")
            # print(f"*** first {first}")
            # print(f"*** second {second}")
            # print(f"*** third {third}")
            if enableWorkmode == "True":
                if first == "ETH":
                    os.system("ifmetric eth1 100")
                    # print("*** ifmetric eth1 100")
                elif first == "WLAN":
                    os.system("ifmetric wlan0 100")
                    # print("*** ifmetric wlan0 100")
                elif first == "4G":
                    os.system("ifmetric ppp0 100")
                    # print("*** ifmetric ppp0 100")
                    
                if second == "ETH":
                    os.system("ifmetric eth1 300")
                    # print("*** ifmetric eth1 300")
                elif second == "WLAN":
                    os.system("ifmetric wlan0 300")
                    # print("*** ifmetric wlan0 300")
                elif second == "4G":
                    os.system("ifmetric ppp0 300")
                    # print("*** ifmetric ppp0 300")
                    
                if third == "ETH":
                    os.system("ifmetric eth1 700")
                    # print("*** ifmetric eth1 700")
                elif third == "WLAN":
                    os.system("ifmetric wlan0 700")
                    # print("*** ifmetric wlan0 700")
                elif third == "4G":
                    os.system("ifmetric ppp0 700")
                    # print("*** ifmetric ppp0 700")
            # print("************* - ************\n")
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
        
    def ping_google(self):
        try:
            response = requests.get("http://www.google.com", timeout=5)
            self.application.settings.deviceStatus.linkStatus = "Online" if response.status_code == 200 else "Offline"
        except Exception as e:
            print(datetime.now(),"ping_google Exception:",e)
            
    def find_network(self):
        try:
            result = subprocess.check_output("ip route", shell=True).decode('utf-8')
            result_list = result.split("\n")
            eth1_metric = 1000
            wlan0_metric = 1000
            ppp0_metric = 1000
            for data in result_list:
                if "eth1" in data:
                    eth1_metric = int(data.split("metric")[1]) 
                elif "wlan0" in data:
                    wlan0_metric = int(data.split("metric")[1])
                elif "ppp0" in data:
                    ppp0_metric = int(data.split("metric")[1])
            min_metric = min(eth1_metric,wlan0_metric,ppp0_metric)
            if min_metric == eth1_metric:
                self.application.settings.deviceStatus.networkCard = "Ethernet"
            elif min_metric == wlan0_metric:
                self.application.settings.deviceStatus.networkCard = "Wifi"
            elif min_metric == ppp0_metric:
                self.application.settings.deviceStatus.networkCard = "4G"
                proc = subprocess.Popen(['ifconfig', "ppp0"], stdout=subprocess.PIPE)
                output, _ = proc.communicate()
                ip = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', str(output))
                # print("ip------>" ,ip.group(1))
        except Exception as e:
            print(datetime.now(),"find_network Exception:",e)
            
    def find_stateOfOcpp(self):
        try:
            if self.application.ocppActive:
                self.application.settings.deviceStatus.stateOfOcpp = "Online"
            else:
                self.application.settings.deviceStatus.stateOfOcpp = "Offline"
        except Exception as e:
            print(datetime.now(),"find_stateOfOcpp Exception:",e)
            pass
            
    def strenghtOf4G(self):
        try:
            result = subprocess.check_output("mmcli -m 0", shell=True).decode('utf-8')
            result_list = result.split("\n")
            for data in result_list:
                if "signal quality" in data:
                    self.application.settings.deviceStatus.strenghtOf4G = re.findall(r'\d+', data.split("signal quality:")[1])[0] + "%"
        except Exception as e:
            print(datetime.now(),"strenghtOf4G Exception:",e)
            pass
                     
    def control_device_status(self):
        while True:
            try:
                self.ping_google()
                self.find_network()
                self.find_stateOfOcpp()
                self.strenghtOf4G()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg = self.application.settings.get_device_status()) 
            except Exception as e:
                print(datetime.now(),"control_device_status Exception:",e)
            time.sleep(10)   
        
    
