import os
import time

class NetworkSettings():
    def __init__(self,application) -> None:
        self.application = application
        
    def set_eth(self):
        ip = "192.168.1.70"
        gateway = "192.168.1.1"
        os.system("nmcli con delete static-eth1")
        os.system("stty erase ^h")
        set_eth = 'nmcli con add con-name "static-eth1" ifname eth1 type ethernet ip4 \\{0} gw4 {1}'.format(ip,gateway)
        os.system(set_eth)
        os.system('nmcli con up "static-eth1" ifname eth1')
        
    def set_dns(self):
        dns1 = "114.114.114.114"
        dns2 = "8.8.8.8"
        set_dns = """# This file is managed by man:systemd-resolved(8). Do not edit.
#
# This is a dynamic resolv.conf file for connecting local clients to the
# internal DNS stub resolver of systemd-resolved. This file lists all
# configured search domains.
#
# Run "systemd-resolve --status" to see details about the uplink DNS servers
# currently in use.
#
# Third party programs must not access this file directly, but only through the
# symlink at /etc/resolv.conf. To manage man:resolv.conf(5) in a different way,
# replace this symlink by a static file or a different symlink.
#
# See man:systemd-resolved.service(8) for details about the supported modes of
# operation for /etc/resolv.conf.

nameserver 127.0.0.53
options edns0     
nameserver {0}
nameserver {1}  
""".format(dns1,dns2)
        print(set_dns)
        os.system('nmcli con up "static-eth1" ifname eth1')
        
        
        
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
        while True:
            os.system("ping www.google.com")
            time.sleep(3)
        
        # modify_encryptionType = 'nmcli connection modify wifi wifi-sec.psk "{0}"'
        # modify_netmask = 'nmcli connection modify wifi wifi-sec.psk "{0}"'
        # modify_gateway = 'nmcli connection modify wifi wifi-sec.psk "{0}"'
        
        # os.system(f"nmcli connection up id {connection_name}")
        
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