import os
import time

class NetworkSettings():
    def __init__(self,application) -> None:
        self.application = application
        
    def set_4G(self):
        connection_name = "ppp0"
        apn = "3gnet"
        user = "uninet"
        password = "uninet"
        print("gpio ayarlanıyor")
        os.system("gpio-test.64 w d 20 1")
        time.sleep(5)
        print("gpio ayarlandı")
        add_connection_string = """nmcli connection add con-name {0} ifname ttyUSB2 autoconnect yes \ && 
        type gsm apn {1} user {2} password {3}""".format(connection_name,apn,user,password)
        print(add_connection_string)
        os.system(add_connection_string)
        
        
        # os.system(f"nmcli connection up id {connection_name}")
        
NetworkSettings(None).set_4G()
while True:
    time.sleep(1)








# ####################### 4GSET ##############################################
# gpio-test.64 w d 20 1
# sleep 5
# if [ ! -f "/etc/NetworkManager/system-connections/ppp0" ];then
#     #nmcli connection delete ppp0
#     nmcli connection add con-name ppp0 ifname ttyUSB2 autoconnect yes \
#     type gsm apn 3gnet user uninet password uninet
# fi