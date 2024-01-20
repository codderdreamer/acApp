import os
import time



connection_name = "ppp0"
apn = "3gnet"
user = "uninet"
password = "uninet"
pin = "0000"
enableModification = "True"

if enableModification=="True":
    os.system("gpio-test.64 w d 20 1")
    time.sleep(5)
    add_connection_string = """nmcli connection add con-name {0} ifname ttyUSB2 autoconnect yes \\type gsm apn {1} user {2} password {3}""".format(connection_name,apn,user,password)
    print(add_connection_string)
    os.system(add_connection_string)
else:
    os.system("nmcli connection delete ppp0")
    
wifiEnable = "True"
ssid = "FiberHGW_TP06BA_5GHz_EXT"
password = "xNUEjvX9"
    
if wifiEnable=="True":
    os.system("systemctl restart NetworkManager")
    time.sleep(3)
    os.system("nmcli radio wifi on")
    set_wifi = 'nmcli dev wifi connect {0} password {1} ifname wlan0'.format(ssid,password)
    os.system(set_wifi)
    os.system("systemctl restart NetworkManager")
else:
    os.system("ifconfig wlan0 down")
    
while True:
    time.sleep(1)
    
