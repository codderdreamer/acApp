import os
import time
from bluetooth import *
import threading
import json


class BluetoothServer:
    def __init__(self,application) -> None:
        self.application = application
        self.connection = False
        self.client_sock = None
        threading.Thread(target=self.run_thread,daemon=True).start()
        threading.Thread(target=self.send_message,daemon=True).start()

    def device_connect(self):
        os.system("rfkill unblock all")
        print("--------------------------------- 1")
        time.sleep(3)
        os.system("killall hciattach")
        print("--------------------------------- 2")
        time.sleep(3)
        os.system("hciattach -n -s 1500000 /dev/ttyS1 sprd &")

    def hci_up(self):
        os.system("sudo hciconfig hci0 up")

    def discoverable_on(self): 
        os.system("bluetoothctl pairable on")
        os.system("bluetoothctl discoverable on")
        os.system("sudo hciconfig hci0 leadv")


    def pi_scan(self):
        os.system("sudo hciconfig hci piscan")


    def btt(self):
        print("--------------------------------------------- device_connect")
        threading.Thread(target=self.device_connect,daemon=True).start()
        time.sleep(10)
        print("--------------------------------------------- hci_up")
        threading.Thread(target=self.hci_up,daemon=True).start()
        time.sleep(3)
        print("--------------------------------------------- discoverable_on")
        threading.Thread(target=self.discoverable_on,daemon=True).start()
        time.sleep(3)
        print("--------------------------------------------- pi_scan")
        threading.Thread(target=self.pi_scan,daemon=True).start()
        print("finish")

    def start_server_sock_listenning(self):
        try:
            self.server_sock=BluetoothSocket( RFCOMM )
            self.server_sock.bind(("",PORT_ANY))
            self.server_sock.listen(1)
            self.port = self.server_sock.getsockname()[1]
            uuid = "7c7dfdc9-556c-4551-bb46-391b1dd27cc0"
            advertise_service( self.server_sock, "PiServer",
                            service_id = uuid,
                            service_classes = [ uuid, SERIAL_PORT_CLASS ],
                            profiles = [ SERIAL_PORT_PROFILE ] 
            #                   protocols = [ OBEX_UUID ] 
                                )
        except Exception as e:
            print(e)
            
    def send_network_priority(self):
        command = {
                    "Command" : "NetworkPriority",
                    "Data" : {
                                "enableWorkmode" : bool(self.application.settings.networkPriority.enableWorkmode=="True"),
                                "1" : self.application.settings.networkPriority.first,
                                "2" : self.application.settings.networkPriority.second,
                                "3" : self.application.settings.networkPriority.third
                            }
                }
        print("Gönderilen:",command)
        self.client_sock.send(json.dumps(command).encode()) 
        
    def send_4g_settings(self):
        command = {
                    "Command" : "4GSettings",
                    "Data" : {
                                "enableModification" : bool(self.application.settings.settings4G.enableModification=="True"),
                                "apn" : self.application.settings.settings4G.apn,
                                "user" : self.application.settings.settings4G.user,
                                "password" : self.application.settings.settings4G.password,
                                "pin" : self.application.settings.settings4G.pin,
                            }
                }
        print("Gönderilen:",command)
        self.client_sock.send(json.dumps(command).encode()) 
        
    def send_ethernet_settings(self):
        command = {
                    "Command" : "EthernetSettings",
                    "Data" : {
                                "ethernetEnable" : bool(self.application.settings.ethernetSettings.ethernetEnable=="True"),
                                "ip" : self.application.settings.ethernetSettings.ip,
                                "netmask" : self.application.settings.ethernetSettings.netmask,
                                "gateway" : self.application.settings.ethernetSettings.gateway
                            }
                }
        print("Gönderilen:",command)
        self.client_sock.send(json.dumps(command).encode()) 
        
    def send_dns_settings(self):
        command = {
                    "Command" : "DNSSettings",
                    "Data" : {
                                "dnsEnable" : bool(self.application.settings.dnsSettings.dnsEnable=="True"),
                                "DNS1" : self.application.settings.dnsSettings.DNS1,
                                "DNS2" : self.application.settings.dnsSettings.DNS2
                            }
                }
        print("Gönderilen:",command)
        self.client_sock.send(json.dumps(command).encode()) 
        
    def waiting_connection(self):
        while True:
            try:
                print("--------------------------------------------- waiting_connection")
                threading.Thread(target=self.discoverable_on,daemon=True).start()
                time.sleep(3)
                os.system("sudo hciconfig hci0 leadv")
                if(self.connection == False):
                    print("Waiting for connection on RFCOMM channel %d" % self.port)
                    self.client_sock, client_info = self.server_sock.accept()
                    self.connection = True
                    print("Accepted connection from ", client_info)
                    self.send_network_priority()
                    self.send_dns_settings()
                    self.send_ethernet_settings()
                    self.send_network_priority()
                while self.connection:
                    print("Waiting for data receive...")
                    try:
                        data = self.client_sock.recv(1024)
                        data = data.decode('utf-8')
                        print("incoming data:", data)
                        self.message_parsing(data)
                    except Exception as e:
                        print(e)
                        self.connection = False
            except Exception as e:
                print(e)
                time.sleep(1)

    def send_message(self):
        while True:
            try:
                if self.connection:
                    print("mesaj gönderiliyor")
                    command = {
                        "test" :"test"
                    }
                    self.client_sock.send(json.dumps(command).encode()) 
                    print("mesaj gönderildi")
            except Exception as e:
                print(e)
            time.sleep(1)

    def message_parsing(self,data):
        try:
            json_object = json.loads(data)
            Command = json_object["Command"]
            Data = json_object["Data"]
            if Command == "NetworkPriority":
                self.application.databaseModule.set_network_priority(Data["enableWorkmode"],Data["1"],Data["2"],Data["3"])
                self.application.webSocketServer.send_network_priority()
            elif Command == "4GSettings":
                self.application.databaseModule.set_settings_4g(Data["enableModification"],Data["apn"],Data["user"],Data["password"],Data["pin"])
                self.application.webSocketServer.send_4g_settings()
            elif Command == "EthernetSettings":
                self.application.databaseModule.set_ethernet_settings(Data["ethernetEnable"],Data["ip"],Data["netmask"],Data["gateway"])
                self.application.webSocketServer.send_ethernet_settings()
            elif Command == "DNSSettings":
                self.application.databaseModule.set_dns_settings(Data["dnsEnable"],Data["DNS1"],Data["DNS2"])
                self.application.webSocketServer.send_dns_settings()
            
        except Exception as e:
            print(e)
            
    def run_thread(self):
        self.btt()
        time.sleep(20)
        print("------------------------------------listenning-----------------------------")
        self.start_server_sock_listenning()
        self.waiting_connection()
            

# bt = BluetoothServer(None)
# bt.btt()
# time.sleep(20)
# print("------------------------------------listenning-----------------------------")
# bt.start_server_sock_listenning()
# bt.waiting_connection()

# while True:
#     time.sleep(1)


#######################################################
# Filename     : bluetooth_set.sh
#######################################################
# #!/bin/sh

# rfkill unblock all

# SDIO=`cat /sys/bus/sdio/devices/mmc2*1/device`
# if [ $SDIO = "0x0145" ];then
#         #find hci0
#         killall hciattach
#         hciattach -n -s 1500000 /dev/ttyS1 sprd &
# elif [ $SDIO = "0xc821" ];then
#         #find hci0
#         killall rtk_hciattach
#         rtk_hciattach -n -s 115200 /dev/ttyS1 rtk_h5 &
# fi

# #bluetooth up
# hciconfig hci0 up && hciconfig hci0 piscan
# bluetoothctl

#######################################################
# Filename     : bluetooth_rfcomm.sh
#######################################################
# #!/bin/sh
# #add serial port service
# sdptool add SP
# #add serial port
# sleep 1
# rfcomm watch hci0 &
# #read: cat /dev/rfcomm0
# #write: echo "test" > /dev/rfcomm0


#######################################################
# Filename     : 4g_set.sh
# Last modified: 2021-04-07 15:45
# Author       : jzzh
# Email        : jzzh@szbaijie.cn
# Company site : http://www.szbaijie.cn/index.php
# Description  :
#######################################################
#!/bin/sh

# gpio-test.64 w d 20 1
# sleep 5
# if [ ! -f "/etc/NetworkManager/system-connections/ppp0" ];then
#     #nmcli connection delete ppp0
#     nmcli connection add con-name ppp0 ifname ttyUSB2 autoconnect yes \
#     type gsm apn 3gnet user uninet password uninet
# fi