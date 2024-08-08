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
        self.set_functions_enable()
        Thread(target=self.set_eth, daemon=True).start()
        Thread(target=self.set_4G, daemon=True).start()
        Thread(target=self.set_wifi, daemon=True).start()
        # Thread(target=self.set_network_priority, daemon=True).start()
        Thread(target=self.control_device_status, daemon=True).start()
        self.set_timezoon()
        self.set_bluetooth_settings()
        Thread(target=self.check_internet_connection, daemon=True).start()

    def check_internet_connection(self):
        interfaces = ["eth1", "wlan0", "ppp0"]
        while True:
            try:
                success_interfaces = []
                for interface in interfaces:
                    command = f"ping -I {interface} -c 3 8.8.8.8"
                    try:
                        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if result.returncode == 0:
                            print(f"Başarılı ağ arayüzü: {interface}")
                            success_interfaces.append(interface)
                        else:
                            print(f"Başarısız ağ arayüzü: {interface}")
                    except Exception as e:
                        print(f"{interface} için ping atılırken hata oluştu: {str(e)}")

                print("success_interfaces",success_interfaces)
                
                if self.turn_interface(self.application.settings.networkPriority.first) in success_interfaces:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.first) + " 100")
                    print(self.application.settings.networkPriority.first, "100")
                else:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.first) + " 800")
                    print(self.application.settings.networkPriority.first, "800")

                if self.turn_interface(self.application.settings.networkPriority.second) in success_interfaces:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.second) + " 300")
                    print(self.application.settings.networkPriority.second, "300")
                else:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.second) + " 850")

                if self.turn_interface(self.application.settings.networkPriority.third) in success_interfaces:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.third) + " 700")
                    print(self.application.settings.networkPriority.third, "700")
                else:
                    os.system("ifmetric " + self.turn_interface(self.application.settings.networkPriority.third) + " 900")
            
            except Exception as e:
                self.logger.exception("Exception in check_internet_connection: " + e)

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
            self.logger.exception("Exception in turn_interface: " + e)

    def control_websocket_ip(self):
        try:
            self.get_active_ips()
            self.logger.debug(f"Active IPs: eth1={self.application.settings.networkip.eth1}, ppp0={self.application.settings.networkip.ppp0}, wlan0={self.application.settings.networkip.wlan0}")

            if self.application.settings.deviceStatus.networkCard == "Ethernet":
                self.application.settings.websocketIp = self.application.settings.networkip.eth1
            elif self.application.settings.deviceStatus.networkCard == "Wifi":
                self.application.settings.websocketIp = self.application.settings.networkip.wlan0
            elif self.application.settings.deviceStatus.networkCard == "4G":
                self.application.settings.websocketIp = self.application.settings.networkip.ppp0

            self.logger.debug(f"WebSocket IP set to: {self.application.settings.websocketIp}")

            if self.application.settings.networkPriority.first == "ETH" and self.application.settings.deviceStatus.networkCard != "Ethernet":
                Thread(target=self.set_eth, daemon=True).start()
            elif self.application.settings.networkPriority.first == "WLAN" and self.application.settings.deviceStatus.networkCard != "Wifi":
                Thread(target=self.set_wifi, daemon=True).start()
            elif self.application.settings.networkPriority.first == "4G" and self.application.settings.deviceStatus.networkCard != "4G":
                Thread(target=self.set_4G, daemon=True).start()
        except Exception as e:
            self.logger.exception("Exception in control_websocket_ip")

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
            self.logger.exception("Exception in get_active_ips")

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
            self.logger.exception("Exception in get_connections")

    def delete_connection_type(self, con_type):
        try:
            connections = self.get_connections()
            for connection in connections:
                if con_type in connection:
                    subprocess.run(["nmcli", "con", "delete", connection[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            self.logger.exception("Exception in delete_connection_type")

    def set_eth(self):
        try:
            ethernetEnable = self.application.settings.ethernetSettings.ethernetEnable
            dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
            ip = self.application.settings.ethernetSettings.ip
            netmask = self.application.settings.ethernetSettings.netmask
            gateway = self.application.settings.ethernetSettings.gateway
            self.delete_connection_type("ethernet")
            self.logger.debug("Setting Ethernet connection")

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
            else:
                self.delete_connection_type("ethernet")
        except Exception as e:
            self.logger.exception("Exception in set_eth")

    def set_dns(self):
        try:
            dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
            dnsEnable = self.application.settings.dnsSettings.dnsEnable
            DNS1 = self.application.settings.dnsSettings.DNS1
            DNS2 = self.application.settings.dnsSettings.DNS2

            if dhcpcEnable == "False":
                if dnsEnable == "True":
                    setDns = 'nmcli con modify "static-eth1" ipv4.dns "{0},{1}" > /dev/null 2>&1'.format(DNS1, DNS2)
                    print(datetime.now(), "set_dns: Executing command:", setDns)
                    os.system(setDns)
                    os.system('nmcli con up "static-eth1" ifname eth1 > /dev/null 2>&1')

            if dnsEnable == "False":
                setDns = "nmcli con modify \"static-eth1\" ipv4.dns \"\""
                os.system(setDns)

        except Exception as e:
            self.logger.exception("Exception in set_dns")

    def set_4G(self):
        try:
            connection_name = "ppp0"
            apn = self.application.settings.settings4G.apn
            user = self.application.settings.settings4G.user
            password = self.application.settings.settings4G.password
            pin = self.application.settings.settings4G.pin
            enableModification = self.application.settings.settings4G.enableModification
            self.delete_connection_type("gsm")
            self.logger.debug("Setting 4G connection")

            if enableModification == "True":
                time.sleep(3)
                os.system("gpio-test.64 w d 20 1 > /dev/null 2>&1")
                time.sleep(5)
                add_connection_string = """nmcli connection add con-name {0} ifname ttyUSB2 autoconnect yes \\type gsm apn {1} user {2} password {3} > /dev/null 2>&1""".format(connection_name,apn,user,password)
                os.system(add_connection_string)
                if pin:
                    time_start = time.time()
                    pin_valid = False
                    
                    # PIN doğrulama
                    try:
                        result = subprocess.check_output("mmcli -L", shell=True).decode('utf-8')
                        modem_id = result.split("/")[5].split()[0]
                        pin_check = subprocess.run("""mmcli -i {0} --pin={1}""".format(modem_id, pin), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        if "error" in pin_check.stderr.decode('utf-8').lower():
                            self.logger.error("PIN hatalı. Lütfen doğru PIN'i girin.")
                        else:
                            pin_valid = True
                    except Exception as e:
                        self.logger.error(f"PIN doğrulama sırasında bir hata oluştu: {str(e)}")

                    if pin_valid:
                        while True:
                            if time.time() - time_start > 60:
                                break
                            try:
                                net = """nmcli con up "{0}" ifname ttyUSB2 > /dev/null 2>&1""".format(connection_name)
                                os.system(net)
                                break
                            except:
                                pass
                            time.sleep(2)
                else:
                    time_start = time.time()
                    while True:
                        if time.time() - time_start > 60:
                                break
                        try:
                            result = subprocess.check_output("mmcli -L", shell=True).decode('utf-8')
                            modem_id = result.split("/")[5].split()[0]
                            net = """nmcli con up "{0}" ifname ttyUSB2""".format(connection_name)
                            os.system(net)
                            break
                        except:
                            pass
        except Exception as e:
            self.logger.exception("Exception in set_4G")
            
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
            
            print(datetime.now(), "set_wifi: wifiEnable:", wifiEnable)
            print(datetime.now(), "set_wifi: mod:", mod)
            print(datetime.now(), "set_wifi: ssid:", ssid)
            print(datetime.now(), "set_wifi: password:", password)
            print(datetime.now(), "set_wifi: encryptionType:", encryptionType)
            print(datetime.now(), "set_wifi: wifidhcpcEnable:", wifidhcpcEnable)
            print(datetime.now(), "set_wifi: ip:", ip)
            print(datetime.now(), "set_wifi: netmask:", netmask)
            print(datetime.now(), "set_wifi: gateway:", gateway)
            
            self.delete_connection_type("wifi")
            
            if wifiEnable == "True":
                if mod == "AP":
                    if wifidhcpcEnable == "True":
                        subprocess.run(["sh", "/root/acApp/accesspoint_add.sh", ssid, password, "True", "192.168.1.100", "24", "192.168.1.1"])
                    else:
                        netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                        netmask_prefix_length = netmask_obj.prefixlen
                        subprocess.run(["sh", "/root/acApp/accesspoint_add.sh", ssid, password, "False", ip, str(netmask_prefix_length), gateway])
                else:
                    result = subprocess.run(f"nmcli con add type wifi ifname wlan0 con-name wifi_connection ssid {ssid}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    print(datetime.now(), "nmcli con add result:", result.stdout, result.stderr)
                    
                    # Bağlantının eklenmesi için kısa bir bekleme süresi
                    time.sleep(2)
                    
                    result = subprocess.run(f"nmcli connection modify wifi_connection wifi-sec.key-mgmt wpa-psk", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    print(datetime.now(), "nmcli modify key-mgmt result:", result.stdout, result.stderr)
                    
                    result = subprocess.run(f"nmcli connection modify wifi_connection wifi-sec.psk {password}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    print(datetime.now(), "nmcli modify psk result:", result.stdout, result.stderr)
                    
                    if wifidhcpcEnable == "False":
                        print("Statik IP ayarlanıyor...")
                        netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
                        netmask_prefix_length = netmask_obj.prefixlen

                        result = subprocess.run(f"nmcli con modify wifi_connection ipv4.addresses {ip}/{netmask_prefix_length}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        print(datetime.now(), "nmcli modify addresses result:", result.stdout, result.stderr)

                        result = subprocess.run(f"nmcli con modify wifi_connection ipv4.gateway {gateway}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        print(datetime.now(), "nmcli modify gateway result:", result.stdout, result.stderr)

                        result = subprocess.run("nmcli con modify wifi_connection ipv4.method manual", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        print(datetime.now(), "nmcli modify method manual result:", result.stdout, result.stderr)
                        
                        print(f"IP: {ip}, Netmask: {netmask_prefix_length}, Gateway: {gateway}")
                        
                    result = subprocess.run("nmcli connection up wifi_connection", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    print(datetime.now(), "nmcli connection up result:", result.stdout, result.stderr)
            else:
                print(datetime.now(), "set_wifi: WiFi devre dışı")
        except Exception as e:
            print(datetime.now(), "set_wifi Hatası:", e)

    def set_network_priority(self):
        time.sleep(10)
        try:
            enableWorkmode = self.application.settings.networkPriority.enableWorkmode
            first = self.application.settings.networkPriority.first
            second = self.application.settings.networkPriority.second
            third = self.application.settings.networkPriority.third
            self.logger.debug(f"Setting network priority: first={first}, second={second}, third={third}")

            if enableWorkmode == "True":
                if first == "ETH":
                    os.system("ifmetric eth1 100")
                elif first == "WLAN":
                    os.system("ifmetric wlan0 100")
                elif first == "4G":
                    os.system("ifmetric ppp0 100 > /dev/null 2>&1") # Not logging this as it is not an error

                if second == "ETH":
                    os.system("ifmetric eth1 300")
                elif second == "WLAN":
                    os.system("ifmetric wlan0 300")
                elif second == "4G":
                    os.system("ifmetric ppp0 300 > /dev/null 2>&1") # Not logging this as it is not an error

                if third == "ETH":
                    os.system("ifmetric eth1 700")
                elif third == "WLAN":
                    os.system("ifmetric wlan0 700")
                elif third == "4G":
                    os.system("ifmetric ppp0 700 > /dev/null 2>&1") # Not logging this as it is not an error
        except Exception as e:
            self.logger.exception("Exception in set_network_priority")

    def set_functions_enable(self):
        try:
            card_type = self.application.settings.functionsEnable.card_type
            self.logger.debug(f"Setting functions enable: card_type={card_type}")

            if card_type == CardType.StartStopCard.value:
                self.application.cardType = CardType.StartStopCard
            elif card_type == CardType.LocalPnC.value:
                self.application.cardType = CardType.LocalPnC
            elif card_type == CardType.BillingCard.value:
                self.application.cardType = CardType.BillingCard
        except Exception as e:
            self.logger.exception("Exception in set_functions_enable")

    def ping_google(self):
        try:
            try:
                response = requests.get("http://www.google.com", timeout=5)
                self.application.settings.deviceStatus.linkStatus = "Online" if response.status_code == 200 else "Offline"
            except Exception as e:
                self.application.settings.deviceStatus.linkStatus = "Offline"
            self.logger.debug(f"Ping Google: linkStatus={self.application.settings.deviceStatus.linkStatus}")

            if self.application.settings.deviceStatus.linkStatus == "Offline":
                Thread(target=self.set_eth, daemon=True).start()
                Thread(target=self.set_4G, daemon=True).start()
                Thread(target=self.set_wifi, daemon=True).start()
                # Thread(target=self.set_network_priority, daemon=True).start()
                time.sleep(15)
        except Exception as e:
            self.logger.exception("Exception in ping_google")

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
                    print("wlan0_metric", data.split("metric")[1], wlan0_metric)
                elif "ppp0" in data:
                    ppp0_metric = int(data.split("metric")[1])
            min_metric = min(eth1_metric, wlan0_metric, ppp0_metric)
            if min_metric == eth1_metric:
                self.application.settings.deviceStatus.networkCard = "Ethernet"
            elif min_metric == wlan0_metric:
                self.application.settings.deviceStatus.networkCard = "Wifi"
            elif min_metric == ppp0_metric:
                self.application.settings.deviceStatus.networkCard = "4G"
            self.logger.debug(f"Network found: {self.application.settings.deviceStatus.networkCard}")
            self.control_websocket_ip()
        except Exception as e:
            self.logger.exception("Exception in find_network")

    def find_stateOfOcpp(self):
        try:
            self.application.settings.deviceStatus.stateOfOcpp = "Online" if self.application.ocppActive else "Offline"
            self.logger.debug(f"OCPP state: {self.application.settings.deviceStatus.stateOfOcpp}")
        except Exception as e:
            self.logger.exception("Exception in find_stateOfOcpp")

    # buraya önceki halinde log'lar ekledim ve hata yazdırıyordu hataları düzeltmek adına yeni kontroller ekledim
    def strenghtOf4G(self):
        try:
            enableModification = self.application.settings.settings4G.enableModification
            if enableModification == "True":
                # Get modem list
                result = subprocess.check_output("mmcli -L", shell=True).decode('utf-8')
                
                # Check if the result contains modem details
                modems = result.strip().split("\n")
                if len(modems) > 0:
                    modem_info = modems[0]  # Assuming the first modem is the one we need
                    modem_parts = modem_info.split()
                    
                    # Check if the modem information is in the expected format
                    if len(modem_parts) > 0 and modem_parts[0].startswith("/org/"):
                        modem_id = modem_parts[0].split("/")[-1]  # Get the short modem id
                        
                        # Get modem details
                        result = subprocess.check_output(f"mmcli -m {modem_id}", shell=True).decode('utf-8')
                        # Parse modem details
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
                            self.logger.warning("Signal quality information not found in modem details.")
                            self.application.settings.deviceStatus.strenghtOf4G = "Unknown"
                    else:
                        self.logger.warning("No valid modem information found.")
                        self.application.settings.deviceStatus.strenghtOf4G = "Unknown"
                else:
                    self.logger.warning("No modems found.")
                    self.application.settings.deviceStatus.strenghtOf4G = "Unknown"
                    
                self.logger.info(f"4G strength: {self.application.settings.deviceStatus.strenghtOf4G}")
        except subprocess.CalledProcessError as e:
            self.logger.exception("Subprocess error in strenghtOf4G: %s", e)
        except Exception as e:
            self.logger.exception("Exception in strenghtOf4G: %s", e)

    def set_timezoon(self):
        try:
            subprocess.run(['timedatectl', 'set-timezone', self.application.settings.timezoonSettings.timezone], check=True)
            self.logger.debug(f"Timezone set to: {self.application.settings.timezoonSettings.timezone}")
        except subprocess.CalledProcessError as e:
            self.logger.exception("Exception in set_timezoon")

    def control_device_status(self):
        while True:
            try:
                time.sleep(10)
                self.ping_google()
                self.find_network()
                self.find_stateOfOcpp()
                self.strenghtOf4G()
                # Thread(target=self.set_network_priority, daemon=True).start()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_device_status())
            except Exception as e:
                self.logger.exception("Exception in control_device_status")
            time.sleep(10)

    def set_bluetooth_settings(self):
        try:
            process = subprocess.Popen(['hostname'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8')
            name = output.split("\n")[0]
            self.logger.info(f"Current hostname: {name}")

            new_bluetooth_name = self.application.settings.bluetoothSettings.bluetooth_name
           
            if (name != new_bluetooth_name) and (new_bluetooth_name != "") and (new_bluetooth_name is not None):
                max_length = 32  # Bluetooth adı için genel kabul gören maksimum uzunluk
                valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ")

                if len(new_bluetooth_name) > max_length:
                    self.logger.warning("Bluetooth name is too long")
                    return

                if not all(char in valid_chars for char in new_bluetooth_name):
                    self.logger.warning("Bluetooth name contains invalid characters")
                    return

                os.system("""hostnamectl set-hostname {0}""".format(new_bluetooth_name))

                # D-Bus üzerinden Bluetooth adını değiştirme
                dbus_command = [
                    'dbus-send',
                    '--system',
                    '--dest=org.bluez',
                    '--print-reply',
                    '/org/bluez/hci0',
                    'org.freedesktop.DBus.Properties.Set',
                    'string:org.bluez.Adapter1',
                    'string:Alias',
                    'variant:string:' + new_bluetooth_name
                ]

                process = subprocess.Popen(dbus_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                # Bluetooth servisini yeniden başlatma

                os.system("hciconfig hci0 down")
                time.sleep(2)
                os.system("service bluetooth restart")
                time.sleep(2)
                os.system("hciconfig hci0 up")

                self.logger.info(f"Bluetooth name changed to: {new_bluetooth_name}")
        except Exception as e:
            self.logger.exception("Exception in set_bluetooth_settings")