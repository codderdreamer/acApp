import os
import time

class NetworkSettings():
    def __init__(self,application) -> None:
        self.application = application
        
    def set_4G(self,apn,user,password,pin):
        connection_name = "ppp0"
        # apn = "3gnet"
        # user = "uninet"
        # password = "uninet"
        print("gpio ayarlanıyor")
        os.system("gpio-test.64 w d 20 1")
        time.sleep(5)
        print("gpio ayarlandı")
        os.system(f"nmcli connection add con-name {connection_name} ifname ttyUSB2 autoconnect yes".format(connection_name))
        print("connection ekleniyor.")
        
        os.system(f"type gsm apn {apn} user {user} password {password}".format(apn,user,password))
        
        # os.system(f"nmcli connection up id {connection_name}")
        
NetworkSettings(None).set_4G("3gnet","uninet","uninet","")