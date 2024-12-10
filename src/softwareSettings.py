import os
import time
import ipaddress
import subprocess
import re
from src.enums import *
from datetime import datetime
import requests
from threading import Thread
from src.bluetoothService.bluetoothService import BluetoothService
from subprocess import Popen, PIPE, STDOUT


class SoftwareSettings():
    def __init__(self, application, logger) -> None:
        self.application = application
        self.logger = logger
        self.__success_interfaces = []
        self.set_functions_enable()
        Thread(target=self.set_eth, daemon=True).start()
        Thread(target=self.set_4G, daemon=True).start()
        Thread(target=self.set_wifi, daemon=True).start()
        Thread(target=self.control_device_status, daemon=True).start()
        self.set_timezoon()
        self.set_bluetooth_settings()
        Thread(target=self.check_internet_connection, daemon=True).start()

    @property
    def success_interfaces(self):
        return self.__success_interfaces

    @success_interfaces.setter
    def success_interfaces(self, value):
        if self.__success_interfaces != value:
            print(Color.Yellow.value, "Success Interfaces:", value)
            self.__success_interfaces = value

    def check_ip_exists(self):
        try:
            command = ['ip', 'addr', 'show', "eth1"]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if "192.168.52.5" in stdout.decode():
                return True
            else:
                return False
        except Exception as e:
            print("check_ip_exists Exception:",e)

    def check_internet_connection(self):
        interfaces = ["eth1", "wlan0", "ppp0"]
        while True:
            try:
                success_interfaces = []
                for interface in interfaces:
                    command = ["ping", "-I", interface, "-c", "1", "8.8.8.8"]
                    try:
                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate()
                        result = stdout.decode()
                        if process.returncode == 0:
                            success_interfaces.append(interface)
                    except Exception as e:
                        print("check_internet_connection ping Exception:",e)
                self.success_interfaces = success_interfaces
                if self.turn_interface(self.application.settings.networkPriority.first) in success_interfaces:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.first) + " 100")
                else:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.first) + " 800")

                if self.turn_interface(self.application.settings.networkPriority.second) in success_interfaces:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.second) + " 300")
                else:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.second) + " 850")

                if self.turn_interface(self.application.settings.networkPriority.third) in success_interfaces:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.third) + " 700")
                else:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.third) + " 900")
            
            except Exception as e:
                print("check_internet_connection Exception:",e)

            time.sleep(2)

    def turn_interface(self,value):
        try:
            if value == "ETH":
                return "eth1"
            elif value == "WLAN":
                return "wlan0"
            elif value == "4G":
                return "ppp0"
        except Exception as e:
            print("turn_interface Exception:",e)

    def get_active_ips(self):
        try:
            eth1, ppp0, wlan0 = None, None, None
            process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            result = stdout.decode()
            data = result.split("\n")
            counter = 0
            for net in data:
                if "eth1" in net:
                    if ":" in data[counter + 1].split()[1]:
                        eth1 = None
                    else:
                        eth1 = data[counter + 1].split()[1]
                if "ppp0" in net:
                    if ":" in data[counter + 1].split()[1]:
                        ppp0 = None
                    else:
                        ppp0 = data[counter + 1].split()[1]
                if "wlan0" in net:
                    if ":" in data[counter + 1].split()[1]:
                        wlan0 = None
                    else:
                        wlan0 = data[counter + 1].split()[1]
                counter += 1
            self.application.settings.networkip.eth1 = eth1
            self.application.settings.networkip.ppp0 = ppp0
            self.application.settings.networkip.wlan0 = wlan0
        except Exception as e:
            print("get_active_ips Exception:",e)

    def get_connections(self):
        try:
            connections = []
            process = subprocess.Popen(['nmcli', 'con', 'show'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            result = stdout.decode()
            data = result.split("\n")
            for i in range(1, len(data)):
                new_connection = []
                connection = data[i].split()
                if len(connection) > 4:
                    connection_name = ""
                    for j in range(0, len(connection) - 3):
                        if j == len(connection) - 4:
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
            print("get_connections Exception:",e)

    def delete_connection_type(self, con_type):
        try:
            connections = self.get_connections()
            for connection in connections:
                if con_type in connection:
                    subprocess.run(["nmcli", "connection", "down", connection[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["nmcli", "con", "delete", connection[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print("delete_connection_type Exception:",e)

    def set_eth(self):
        try:
            print("Set eth")
            ethernetEnable = self.application.settings.ethernetSettings.ethernetEnable
            dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
            ip = self.application.settings.ethernetSettings.ip
            netmask = self.application.settings.ethernetSettings.netmask
            gateway = self.application.settings.ethernetSettings.gateway
            self.delete_connection_type("ethernet")

            if ethernetEnable == "True":
                if dhcpcEnable == "False":
                    netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                    netmask_prefix_length = netmask_obj.prefixlen
                    os.system("stty erase ^h")
                    set_eth = 'nmcli con add con-name "static-eth1" ifname eth1 type ethernet ip4 \\{0}/{1} gw4 {2} > /dev/null 2>&1'.format(ip,netmask_prefix_length,gateway)
                    os.system(set_eth)
                    os.system('nmcli con up "static-eth1" ifname eth1 > /dev/null 2>&1')
                    self.set_dns()
                else:
                    os.system("stty erase ^h > /dev/null 2>&1")
                    set_eth = 'nmcli con add con-name "wire" ifname eth1 type ethernet > /dev/null 2>&1'
                    os.system(set_eth)
                    os.system('nmcli con up "wire" ifname eth1 > /dev/null 2>&1')
        except Exception as e:
            print("set_eth Exception:",e)

    def set_dns(self):
        try:
            dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
            dnsEnable = self.application.settings.dnsSettings.dnsEnable
            DNS1 = self.application.settings.dnsSettings.DNS1
            DNS2 = self.application.settings.dnsSettings.DNS2
            if dhcpcEnable == "False":
                if dnsEnable == "True":
                    setDns = 'nmcli con modify "static-eth1" ipv4.dns "{0},{1}" > /dev/null 2>&1'.format(DNS1, DNS2)
                    os.system(setDns)
                    os.system('nmcli con up "static-eth1" ifname eth1 > /dev/null 2>&1')
            if dnsEnable == "False":
                setDns = "nmcli con modify \"static-eth1\" ipv4.dns \"\""
                os.system(setDns)
        except Exception as e:
            print("set_dns Exception:",e)

    def set_4G(self):
        try:
            print(Color.Yellow.value,"4G set ediliyor...")
            connection_name = "ppp0"
            apn = self.application.settings.settings4G.apn
            user = self.application.settings.settings4G.user
            password = self.application.settings.settings4G.password
            pin = self.application.settings.settings4G.pin
            enableModification = self.application.settings.settings4G.enableModification

            # Mevcut GSM bağlantısını sil
            self.delete_connection_type(connection_name)

            # GPIO kontrol komutlarını çalıştır
            subprocess.run("gpio-test.64 w d 20 0 > /dev/null 2>&1", shell=True, check=True)
            time.sleep(3)

            if enableModification == "True":
                time.sleep(3)
                subprocess.run("gpio-test.64 w d 20 1 > /dev/null 2>&1", shell=True, check=True)
                time.sleep(5)

                # Bağlantı ekleme komutunu oluştur
                add_connection_string = f"nmcli connection add con-name {connection_name} ifname ttyUSB2 autoconnect yes type gsm "
                if apn:
                    add_connection_string += f"apn {apn} "
                if user:
                    add_connection_string += f"user {user} "
                if password:
                    add_connection_string += f"password {password} "
                if pin:
                    add_connection_string += f"gsm.pin {pin} "
                add_connection_string += "> /dev/null 2>&1"

                # Bağlantı ekleme komutunu çalıştır
                subprocess.run(add_connection_string, shell=True, check=True)

                # PIN zaten bağlantı sırasında tanımlandı, bağlantıyı etkinleştir
                subprocess.run(f"nmcli connection up {connection_name} ifname ttyUSB2", shell=True, check=True)

        except Exception as e:
            print("set_4G Exception:", e)
   
    def set_wifi(self):
        try:
            print(Color.Yellow.value,"Wifi set ediliyor...")
            wifiEnable = self.application.settings.wifiSettings.wifiEnable
            mod = self.application.settings.wifiSettings.mod
            ssid = self.application.settings.wifiSettings.ssid
            password = self.application.settings.wifiSettings.password
            encryptionType = self.application.settings.wifiSettings.encryptionType
            wifidhcpcEnable = self.application.settings.wifiSettings.wifidhcpcEnable
            ip = self.application.settings.wifiSettings.ip
            netmask = self.application.settings.wifiSettings.netmask
            gateway = self.application.settings.wifiSettings.gateway
            self.delete_connection_type("wifi")
            if wifiEnable == "True":
                if mod == "AP":
                    if wifidhcpcEnable == "True":
                        subprocess.run(["sh", "/root/acApp/bash/accesspoint_add.sh", ssid, password, "True", "192.168.1.100", "24", "192.168.1.1"])
                    else:
                        netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                        netmask_prefix_length = netmask_obj.prefixlen
                        subprocess.run(["sh", "/root/acApp/bash/accesspoint_add.sh", ssid, password, "False", ip, str(netmask_prefix_length), gateway])
                else:
                    result = subprocess.run(f"nmcli con add type wifi ifname wlan0 con-name wifi_connection ssid {ssid}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    time.sleep(2)
                    result = subprocess.run(f"nmcli connection modify wifi_connection wifi-sec.key-mgmt wpa-psk", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    
                    # result = subprocess.run(f"nmcli connection modify wifi_connection wifi-sec.psk {password}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    result = subprocess.run(f"nmcli connection modify wifi_connection wifi-sec.psk \"{password}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    if wifidhcpcEnable == "False":
                        netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                        netmask_prefix_length = netmask_obj.prefixlen
                        result = subprocess.run(f"nmcli con modify wifi_connection ipv4.addresses {ip}/{netmask_prefix_length}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        result = subprocess.run(f"nmcli con modify wifi_connection ipv4.gateway {gateway}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        result = subprocess.run("nmcli con modify wifi_connection ipv4.method manual", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    result = subprocess.run("nmcli connection up wifi_connection", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    if wifidhcpcEnable == "False":
                        setDns = 'nmcli con modify "wifi_connection" ipv4.dns "{0},{1}" > /dev/null 2>&1'.format("8.8.8.8", "8.8.4.4")
                        os.system(setDns)
                        os.system('nmcli con up "wifi_connection" ifname wlan0 > /dev/null 2>&1')
        
        except Exception as e:
            print("set_wifi Exception:",e)

    def set_network_priority(self):
        time.sleep(10)
        try:
            enableWorkmode = self.application.settings.networkPriority.enableWorkmode
            first = self.application.settings.networkPriority.first
            second = self.application.settings.networkPriority.second
            third = self.application.settings.networkPriority.third
            if enableWorkmode == "True":
                if first == "ETH":
                    os.system("ifmetric eth1 100")
                elif first == "WLAN":
                    os.system("ifmetric wlan0 100")
                elif first == "4G":
                    os.system("ifmetric ppp0 100 > /dev/null 2>&1")
                if second == "ETH":
                    os.system("ifmetric eth1 300")
                elif second == "WLAN":
                    os.system("ifmetric wlan0 300")
                elif second == "4G":
                    os.system("ifmetric ppp0 300 > /dev/null 2>&1")
                if third == "ETH":
                    os.system("ifmetric eth1 700")
                elif third == "WLAN":
                    os.system("ifmetric wlan0 700")
                elif third == "4G":
                    os.system("ifmetric ppp0 700 > /dev/null 2>&1")
        except Exception as e:
            print("set_network_priority Exception:",e)

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
            print("set_functions_enable Exception:",e)

    def ping_google(self):
        try:
            response = requests.get("http://www.google.com", timeout=5)
            self.application.settings.deviceStatus.linkStatus = "Online" if response.status_code == 200 else "Offline"
        except Exception as e:
            self.application.settings.deviceStatus.linkStatus = "Offline"

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
                    wlan0_metric = int(data.split("metric")[1].strip().split()[0])
                elif "ppp0" in data:
                    ppp0_metric = int(data.split("metric")[1])
            min_metric = min(eth1_metric, wlan0_metric, ppp0_metric)
            if min_metric == eth1_metric:
                self.application.settings.deviceStatus.networkCard = "Ethernet"
            elif min_metric == wlan0_metric:
                self.application.settings.deviceStatus.networkCard = "Wifi"
            elif min_metric == ppp0_metric:
                self.application.settings.deviceStatus.networkCard = "4G"
        except Exception as e:
            print("find_network Exception:",e)

    def find_stateOfOcpp(self):
        try:
            self.application.settings.deviceStatus.stateOfOcpp = "Online" if self.application.ocppActive else "Offline"
        except Exception as e:
            print("find_stateOfOcpp Exception:",e)


    def strenghtOf4G(self):
        try:
            enableModification = self.application.settings.settings4G.enableModification
            if enableModification == "True":
                result = subprocess.check_output("mmcli -L", shell=True).decode('utf-8')
                modems = result.strip().split("\n")
                if len(modems) > 0:
                    modem_info = modems[0]
                    modem_parts = modem_info.split()
                    if len(modem_parts) > 0 and modem_parts[0].startswith("/org/"):
                        modem_id = modem_parts[0].split("/")[-1]  # Get the short modem id
                        result = subprocess.check_output(f"mmcli -m {modem_id}", shell=True).decode('utf-8')
                        result_list = result.split("\n")
                        for data in result_list:
                            if "signal quality" in data.lower():
                                strength = re.findall(r'\d+', data.split("signal quality:")[1])
                                if strength:
                                    self.application.settings.deviceStatus.strenghtOf4G = strength[0] + "%"
                                else:
                                    self.application.settings.deviceStatus.strenghtOf4G = "Unknown"
                                break
                        else:
                            self.application.settings.deviceStatus.strenghtOf4G = "Unknown"
                    else:
                        self.application.settings.deviceStatus.strenghtOf4G = "Unknown"
                else:
                    self.application.settings.deviceStatus.strenghtOf4G = "Unknown"
        except Exception as e:
            print("strenghtOf4G Exception:",e)

    def set_timezoon(self):
        try:
            subprocess.run(['timedatectl', 'set-timezone', self.application.settings.timezoonSettings.timezone], check=True)
        except subprocess.CalledProcessError as e:
            print("set_timezoon Exception:",e)

    def control_device_status(self):
        time.sleep(10)
        while True:
            try:
                self.ping_google()
                self.find_network()
                self.get_active_ips()
                self.find_stateOfOcpp()
                self.strenghtOf4G()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_device_status())
            except Exception as e:
                print("control_device_status Exception:",e)
            time.sleep(10)

    def set_bluetooth_settings(self):
        try:
            new_bluetooth_name = self.application.settings.bluetoothSettings.bluetooth_name

            # Geçerli hostname'i kontrol ediyoruz
            process = subprocess.run(['hostname'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            current_name = process.stdout.decode('utf-8').strip()

            # Eğer mevcut hostname ile yeni Bluetooth adı aynı değilse, Bluetooth adını değiştir
            if current_name != new_bluetooth_name:
                # bluetoothctl ile Bluetooth adını değiştir ve gerekli ayarları yap
                commands = f"system-alias {new_bluetooth_name}\npower on\ndiscoverable on\nquit\n"
                subprocess.run(['bluetoothctl'], input=commands.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # 'hciconfig' ile Bluetooth Name değerini değiştiriyoruz
                subprocess.run(['hciconfig', 'hci0', 'name', new_bluetooth_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Hostname'i de yeni Bluetooth adı ile değiştirme
                os.system(f"hostnamectl set-hostname '{new_bluetooth_name}'")
                
                print(f"Bluetooth adı '{new_bluetooth_name}' olarak ayarlandı.")
        except Exception as e:
            print(f"set_bluetooth_settings fonksiyonunda hata: {str(e)}")