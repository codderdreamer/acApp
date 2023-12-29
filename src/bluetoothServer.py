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

class BluetoothServer:
    def __init__(self,application) -> None:
        self.application = application
        self.connection = False
        self.client_sock = None
        threading.Thread(target=self.run_thread,daemon=True).start()
        
    def rfkill(self):
        print("rfkill")
        os.system("rfkill unblock all")
    
    def killall(self):
        print("killall")
        os.system("killall hciattach")
        
    def hciattach(self):
        print("hciattach")
        os.system("hciattach -n -s 1500000 /dev/ttyS1 sprd &")
        
    def hciconfig(self):
        print("hciconfig")
        os.system("hciconfig hci0 up")
        
    def power(self):
        print("power")
        os.system("bluetoothctl power on")
        
    def discoverable(self):
        print("discoverable")
        os.system("bluetoothctl discoverable on")
        
    def pairable(self):
        print("pairable")
        os.system("bluetoothctl pairable on")
        
    def agent(self):
        print("agent")
        os.system("bluetoothctl agent on")
        
    def defaultagent(self):
        print("defaultagent")
        os.system("bluetoothctl default-agent")
        
    def piscan(self):
        print("piscan")
        os.system("hciconfig hci piscan")
        
    def leadv(self):
        print("leadv")
        os.system("sudo hciconfig hci0 leadv")
        
             
    def run_thread(self):
        threading.Thread(target=self.rfkill,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.killall,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.hciattach,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.hciconfig,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.leadv,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.power,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.discoverable,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.pairable,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.agent,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.defaultagent,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.piscan,daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.hciconfig,daemon=True).start()
        time.sleep(3)
        try:
            monitor = BluetoothMonitor()
            monitor_thread = threading.Thread(target=monitor.start)
            monitor_thread.start()   
            monitor.adapter.onPropertiesChanged = self.on_properties_changed
        except Exception as e:
            print("!!!!!!!!!!!!!!!!!!!!!!! Bluetooth Socket Hata",e)
        while True:
            time.sleep(1)
            
    def on_properties_changed(self, interface, changed, invalidated):
        print("***************************************************************************************************************",interface,changed,invalidated)
        if 'Devices' in changed:
            for device_path in changed['Devices']:
                device = self.bus.get('org.bluez', device_path)
                if device.Connected:
                    print(f"Cihaz bağlandı: {device.Alias}")
        
        

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
        path = "/test/agent"
        pin_code = "000000"  # İstediğiniz PIN kodunu buraya yazın
        agent = Agent(self.bus, path, pin_code)
        print("Agent")
        self.bus.register_object(path, agent, AGENT_INTERFACE)
        
        # AgentManager1 arayüzünü kullanarak agent'ı kaydet
        agent_manager = self.bus.get('org.bluez', '/org/bluez')
        agent_manager.RegisterAgent(path, "DisplayOnly")
        agent_manager.RequestDefaultAgent(path)
    
        print("SystemBus")
        self.adapter = self.bus.get('org.bluez', '/org/bluez/hci0')
        self.adapter.Pairable = True

        
        print(self.adapter)
        self.adapter.onPropertiesChanged = self.on_properties_changed
        print("self.adapter.onPropertiesChanged")

    def on_properties_changed(self, interface, changed, invalidated):
        print("***************************************************************************************************************",interface,changed,invalidated)
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