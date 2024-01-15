import os
import time
import ipaddress
import json
import socket
import netifaces as ni
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
        
        ip_test = socket.gethostbyname(socket.gethostname())
        
        try:
            proc = subprocess.Popen(['ifconfig', "eth1"], stdout=subprocess.PIPE)
            output, _ = proc.communicate()
            netmask = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', str(output))
            if netmask:
                netmask_test = netmask.group(1)
        except:
            pass
        
        
        try:
            proc = subprocess.Popen(['ip', 'route'], stdout=subprocess.PIPE)
            output, _ = proc.communicate()
            gateway = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', str(output))
            if gateway:
                gateway_test = gateway.group(1)
        except:
            pass
        
        print("test:",ip_test,netmask_test,gateway_test)
        
        
        
        
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
                os.system("stty erase ^h")
                
                # self.application.settings.ethernetSettings.ip = ni.ifaddresses("eth1")[ni.AF_INET][0]['addr']
                # self.application.settings.ethernetSettings.netmask = ni.ifaddresses("eth1")[ni.AF_INET][0]['netmask']
                # self.application.settings.ethernetSettings.gateway = ni.gateways()['default'][ni.AF_INET][0]
        else:
            os.system("nmcli con delete static-eth1")
            os.system("stty erase ^h")
            
        
        # if ethernetEnable:
        #     netmask_obj = ipaddress.IPv4Network("0.0.0.0/" + netmask, strict=False)
        #     netmask_prefix_length = netmask_obj.prefixlen
        #     os.system("nmcli con delete static-eth1")
        #     os.system("stty erase ^h")
        #     set_eth = 'nmcli con add con-name "static-eth1" ifname eth1 type ethernet ip4 \\{0}/{1} gw4 {2}'.format(ip,netmask_prefix_length,gateway)
        #     os.system(set_eth)
        #     os.system('sudo nmcli con modify "static-eth1" ipv4.dns "8.8.8.8,8.8.4.4"')
        #     os.system('nmcli con up "static-eth1" ifname eth1')
            
        # data = {
        #     "ip" : ip
        # }
        # with open("/root/acApp/client/build/websocket.json", "w") as file:
        #     json.dump(data, file)
        #     print("ip yazıldı")
        
    def set_dns(self):
        dhcpcEnable = self.application.settings.ethernetSettings.dhcpcEnable
        dnsEnable = self.application.settings.dnsSettings.dnsEnable
        DNS1 = self.application.settings.dnsSettings.DNS1
        DNS2 = self.application.settings.dnsSettings.DNS2
        
        if dhcpcEnable == "True":
            if dnsEnable == "True":
                setDns = 'sudo nmcli con modify "static-eth1" ipv4.dns "{0},{1}"'.format(DNS1,DNS2)
                os.system(setDns)
                os.system('nmcli con up "static-eth1" ifname eth1')
        else:
            if dnsEnable == "True":
                setDns = 'sudo nmcli con modify "eth1" ipv4.dns "{0},{1}"'.format(DNS1,DNS2)
                os.system(setDns)
                os.system('nmcli con up "static-eth1" ifname eth1')
        
        # if dnsEnable:
        #     setDns = 'sudo nmcli con modify "static-eth1" ipv4.dns "{0},{1}"'.format(dns1,dns2)
        #     os.system(setDns)
        #     os.system('nmcli con up "static-eth1" ifname eth1')
        
    def set_4G(self):
        connection_name = "ppp0"
        apn = "3gnet"
        user = "uninet"
        password = "uninet"
        print("gpio ayarlanıyor")
        os.system("gpio-test.64 w d 20 1")
        time.sleep(5)
        print("gpio ayarlandı")
        add_connection_string = """nmcli connection add con-name {0} ifname ttyUSB2 autoconnect yes \\type gsm apn {1} user {2} password {3}""".format(connection_name,apn,user,password)
        print(add_connection_string)
        os.system(add_connection_string)
        
    def set_wifi(self):
        ssid = "FiberHGW_TP06BA_5GHz_EXT"
        password = "xNUEjvX9"
        set_wifi = 'nmcli device wifi connect "{0}" password "{1}" name wifi'.format(ssid,password)
        os.system(set_wifi)
        
        
        
        
        
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