import os
import time

import psutil

def check_interface(interface_name):
    interfaces = psutil.net_if_addrs()
    if interface_name in interfaces:
        return f"{interface_name} arabirimi mevcut."
    else:
        return f"{interface_name} arabirimi bulunamadı."

interface_name = "ppp0"
result = check_interface(interface_name)
print(result)

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
    
while True:
    time.sleep(1)