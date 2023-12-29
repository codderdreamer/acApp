import os
import time
from bluetooth import *
import threading
import json
from bluetooth.ble import BeaconService, GATTRequester
from pydbus import SystemBus
from gi.repository import GLib
import threading
import subprocess

class BluetoothServer:
    def __init__(self,application) -> None:
        self.application = application
        self.connection = False
        self.client_sock = None
        threading.Thread(target=self.run_thread,daemon=True).start()
        # threading.Thread(target=self.send_message,daemon=True).start()

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
        # time.sleep(3)
        # print("--------------------------------------------- pi_scan")
        # threading.Thread(target=self.pi_scan,daemon=True).start()
        # print("finish")

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
                print("self.connection",self.connection)
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
            
    def pairable_on(self):
        print("**************************************** bluetoothctl pairable on")
        komutlar = "power on\ndiscoverable on\npairable on\nagent on\ndefault-agent"
        os.system(f"echo -e '{komutlar}' | bluetoothctl")
            
             
    def run_thread(self):
        def on_ble_scan(addr, data, rssi):
            print(f"Received data from {addr}: {data}")
            
            # GATTRequester ile cihaza bağlanma
            requester = GATTRequester(addr, False)
            requester.connect(True)

            # Bağlantı başarılı olursa burada işlemler yapabilirsiniz.
            # Örneğin, cihaza bir komut göndermek, veri okumak, yazmak, vb.

            # Bağlantıyı kapatma
            # requester.disconnect()

        print("**************************************** rfkill unblock all")
        os.system("rfkill unblock all")
        time.sleep(3)
        print("**************************************** killall hciattach")
        os.system("killall hciattach")
        time.sleep(3)
        print("**************************************** hciattach -n -s 1500000 /dev/ttyS1 sprd &")
        os.system("hciattach -n -s 1500000 /dev/ttyS1 sprd &")
        time.sleep(5)
        print("**************************************** sudo hciconfig hci0 up")
        os.system("sudo hciconfig hci0 up")
        time.sleep(3)
        threading.Thread(target=self.pairable_on,daemon=True).start()
        time.sleep(3)
        print("**************************************** pi_scan")
        threading.Thread(target=self.pi_scan,daemon=True).start()
        print("**************************************** sudo hciconfig hci0 leadv")
        os.system("sudo hciconfig hci0 leadv")
        time.sleep(5)
        # self.make_device_discoverable()
        try:
            # print("Starting BLE BeaconService")
            # service = BeaconService()
            # service.start_advertising("11111111-2222-3333-4444-555555555555",1, 1, 1, 200)
            # # service.set_scan_response_raw(b"\x08\x09MyDevice")
            # while True:
            #     devices = service.scan(2)
            #     print(devices)
            #     time.sleep(1)
            
            monitor = BluetoothMonitor()
            monitor_thread = threading.Thread(target=monitor.start)
            monitor_thread.start()
            
            
        except Exception as e:
            print("!!!!!!!!!!!!!!!!!!!!!!! Bluetooth Socket Hata",e)
        
    def make_device_discoverable(self):
        try:
            # Cihazı keşfedilebilir yap
            subprocess.run(["sudo", "hciconfig", "hci0", "piscan"], check=True)
            print("Cihaz keşfedilebilir yapıldı.")
        except subprocess.CalledProcessError as e:
            print(f"Hata: {e}") 
        
            
    def run_thread_xx(self):
        self.btt()
        print("time---------------------------------------")
        time.sleep(20)
        print("config---------------------------------------")
        os.system("sudo hciconfig hci0 leadv")
        print("sudo hciconfig hci0 leadv---------------------------------------")
        
        # print("------------------------------------listenning-----------------------------")
        # self.start_server_sock_listenning()
        # self.waiting_connection()
AGENT_INTERFACE = """
<node>
  <interface name='org.bluez.Agent1'>
    <method name='RequestPinCode'>
      <arg type='o' name='device' direction='in'/>
      <arg type='s' name='pincode' direction='out'/>
    </method>
  </interface>
</node>
"""

class Agent:
    def __init__(self, bus, path, pin_code):
        self.bus = bus
        self.path = path
        self.pin_code = pin_code

    def RequestPinCode(self, device):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("PIN kodu istendi, cihaz:", device)
        return self.pin_code
            
class BluetoothMonitor:
    def __init__(self):
        print("BluetoothMonitor")
        self.bus = SystemBus()
        path = "/agent"
        pin_code = "0000"  # İstediğiniz PIN kodunu buraya yazın
        agent = Agent(self.bus, path, pin_code)
        print("Agent")
        self.bus.register_object(path, agent, AGENT_INTERFACE)
        
        # AgentManager1 arayüzünü kullanarak agent'ı kaydet
        agent_manager = self.bus.get('org.bluez', '/org/bluez')
        agent_manager.RegisterAgent(path, "KeyboardDisplay")
        agent_manager.RequestDefaultAgent(path)
    
        print("SystemBus")
        self.adapter = self.bus.get('org.bluez', '/org/bluez/hci0')
        # self.adapter.Pairable = True

        
        print(self.adapter)
        self.adapter.onPropertiesChanged = self.on_properties_changed
        print("self.adapter.onPropertiesChanged")

    def on_properties_changed(self, interface, changed, invalidated):
        print("on_properties_changed",interface,changed,invalidated)
        if 'Devices' in changed:
            for device_path in changed['Devices']:
                device = self.bus.get('org.bluez', device_path)
                if device.Connected:
                    print(f"Cihaz bağlandı: {device.Alias}")

    def start(self):
        loop = GLib.MainLoop()
        loop.run()
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