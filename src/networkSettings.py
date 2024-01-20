import os
import time
import ipaddress
import json
import socket
import subprocess
import re

class NetworkSettings():
    def __init__(self,application) -> None:
        self.application = application
        
    def set_eth(self):
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
            
        os.system("systemctl restart NetworkManager")
            
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
            
    def set_dns(self):
        dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
        dnsEnable = self.application.settings.dnsSettings.dnsEnable
        DNS1 = self.application.settings.dnsSettings.DNS1
        DNS2 = self.application.settings.dnsSettings.DNS2
        
        if dhcpcEnable == "True":
            if dnsEnable == "True":
                setDns = 'nmcli con modify "static-eth1" ipv4.dns "{0},{1}"'.format(DNS1,DNS2)
                os.system(setDns)
                os.system('nmcli con up "static-eth1" ifname eth1')
        else:
            pass
            # if dnsEnable == "True":
            #     setDns = 'nmcli con modify "eth1" ipv4.dns "{0},{1}"'.format(DNS1,DNS2)
            #     os.system(setDns)
            #     os.system('nmcli con up "eth1" ifname eth1')
          
    def set_4G(self):
        connection_name = "ppp0"
        apn = self.application.settings.settings4G.apn
        user = self.application.settings.settings4G.user
        password = self.application.settings.settings4G.password
        pin = self.application.settings.settings4G.pin
        enableModification = self.application.settings.settings4G.enableModification
        
        if enableModification=="True":
            os.system("nmcli connection delete ppp0")
            os.system("gpio-test.64 w d 20 1")
            time.sleep(5)
            add_connection_string = """nmcli connection add con-name {0} ifname ttyUSB2 autoconnect yes \\type gsm apn {1} user {2} password {3}""".format(connection_name,apn,user,password)
            print(add_connection_string)
            os.system(add_connection_string)
        else:
            os.system("nmcli connection delete ppp0")
            
        os.system("systemctl restart NetworkManager")
          
    def set_wifi(self):
        wifiEnable = self.application.settings.wifiSettings.wifiEnable
        mod = self.application.settings.wifiSettings.mod
        ssid = self.application.settings.wifiSettings.ssid
        password = self.application.settings.wifiSettings.password
        encryptionType = self.application.settings.wifiSettings.encryptionType
        wifidhcpcEnable = self.application.settings.wifiSettings.wifidhcpcEnable
        ip = self.application.settings.wifiSettings.ip
        netmask = self.application.settings.wifiSettings.netmask
        gateway = self.application.settings.wifiSettings.gateway
        
        if wifiEnable=="True":
            os.system("systemctl restart NetworkManager")
            time.sleep(3)
            os.system("nmcli radio wifi on")
            set_wifi = 'nmcli dev wifi connect {0} password {1} ifname wlan0'.format(ssid,password)
            os.system(set_wifi)
            os.system("systemctl restart NetworkManager")
        else:
            os.system("nmcli connection delete wifi")
            
            
    def set_network_priority(self):
        time.sleep(10)
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
            
        

        
        
        
# NetworkSettings(None).set_4G()
# NetworkSettings(None).set_wifi()
# NetworkSettings(None).set_eth()
# NetworkSettings(None).set_dns()
# while True:
#     time.sleep(1)


        # modify_encryptionType = 'nmcli connection modify wifi wifi-sec.psk "{0}"'
        # modify_netmask = 'nmcli connection modify wifi wifi-sec.psk "{0}"'
        # modify_gateway = 'nmcli connection modify wifi wifi-sec.psk "{0}"'
        # os.system(f"nmcli connection up id {connection_name}")

# ####################### ETH SET ############################################
# #!/bin/sh
# stty erase ^h
# read -p "Enter your static ip: " eth0_ip
# read -p "Enter your static route: " eth0_route
# nmcli con add con-name "static-eth0" ifname eth0 type ethernet ip4 \
# $eth0_ip gw4 $eth0_route
# nmcli con up "static-eth0" ifname eth0

# ####################### ETH MOD ############################################
# #!/bin/sh
# stty erase ^h
# read -p "Enter your static ip: " eth0_ip
# nmcli con mod "static-eth0" ipv4.address "$eth0_ip,8.8.8.8"
# nmcli con up "static-eth0" ifname eth0
# ####################### ETH DEL ############################################
# #!/bin/sh
# nmcli con delete static-eth0

# ####################### 4GSET ##############################################
# #!/bin/sh

# gpio-test.64 w d 20 1
# sleep 5
# if [ ! -f "/etc/NetworkManager/system-connections/ppp0" ];then
#     #nmcli connection delete ppp0
#     nmcli connection add con-name ppp0 ifname ttyUSB2 autoconnect yes \
#     type gsm apn 3gnet user uninet password uninet
# fi
# ####################### 4G DEL #############################################
#!/bin/sh
# nmcli connection delete ppp0


# ####################### WİFİ SET ##########################################
# #!/bin/sh
# stty erase ^h
# read -p "Enter your WIFI SSID: " wifi_ssid
# read -p "Enter your WIFI Password: " wifi_password
# nmcli device wifi connect "$wifi_ssid" password "$wifi_password" name wifi

# ####################### WİFİ MOD ##########################################
#!/bin/sh
# stty erase ^h
# read -p "Enter your WIFI SSID: " wifi_ssid
# read -p "Enter your WIFI Password: " wifi_password
# nmcli connection modify wifi wifi.ssid "$wifi_ssid"
# nmcli connection modify wifi wifi-sec.psk "$wifi_password"
# nmcli connection up wifi

# ####################### WİFİ DEL ##########################################
#!/bin/sh
# nmcli connection delete wifi