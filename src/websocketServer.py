import websocket_server
import json
import threading
import time

class WebSocketServer():
    def __init__(self,application) -> None:
        self.application = application
        self.websocketServer = websocket_server.WebsocketServer('0.0.0.0',8000)
        self.websocketServer.set_fn_new_client(self.NewClientws)
        self.websocketServer.set_fn_client_left(self.ClientLeftws)
        self.websocketServer.set_fn_message_received(self.MessageReceivedws)
        threading.Thread(target=self.websocketServer.run_forever, daemon=True).start()
        print("Web Socket started... 0.0.0.0  8000")
        
    def NewClientws(self, client, server):
        if client:
            try:
                print("New client connected and was given id %d" % client['id'], client['address'] )
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_network_priority())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_Settings4G())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_ethernet_settings())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_dns_settings())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_wifi_settings())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_ocpp_settings())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_functions_enable())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_bluetooth_settings())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_timezoon_settings())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_firmware_version())
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_charging())
            except Exception as e:
                print("could not get New Client id",e)
                
    def ClientLeftws(self, client, server):
        try:
            print("Client disconnected client[id]:{}  client['address'] ={}  ".format(client["id"], client['address'] ))
        except Exception as e:
            print("c['handler'] client remove problem",e )
            
    def MessageReceivedws(self, client, server, message):
        try:
            sjon = json.loads(message)
            print(sjon)
            if(sjon["Command"] == "NetworkPriority"):
                enableWorkmode = str(sjon["Data"]["enableWorkmode"])
                first = sjon["Data"]["1"]
                second = sjon["Data"]["2"]
                third = sjon["Data"]["3"]
                self.application.databaseModule.set_network_priority(enableWorkmode,first,second,third)
                self.application.networkSettings.set_network_priority()
            elif(sjon["Command"] == "4GSettings"):
                enableModification = str(sjon["Data"]["enableModification"])
                apn = sjon["Data"]["apn"]
                user = sjon["Data"]["user"]
                password = sjon["Data"]["password"]
                pin = sjon["Data"]["pin"]
                self.application.databaseModule.set_settings_4g(apn,user,password,enableModification,pin)
                self.application.networkSettings.set_4G()
            elif(sjon["Command"] == "EthernetSettings"):
                ethernetEnable = str(sjon["Data"]["ethernetEnable"])
                dhcpcEnable = str(sjon["Data"]["dhcpcEnable"])
                ip = sjon["Data"]["ip"]
                netmask = sjon["Data"]["netmask"]
                gateway = sjon["Data"]["gateway"]
                self.application.databaseModule.set_ethernet_settings(ethernetEnable,dhcpcEnable,ip,netmask,gateway)
                self.application.networkSettings.set_eth()
                self.application.networkSettings.set_dns()
            elif(sjon["Command"] == "DNSSettings"):
                dnsEnable = str(sjon["Data"]["dnsEnable"])
                dns1 = sjon["Data"]["DNS1"]
                dns2 = sjon["Data"]["DNS2"]
                self.application.databaseModule.set_dns_settings(dnsEnable,dns1,dns2)
                self.application.networkSettings.set_dns()
            elif(sjon["Command"] == "WifiSettings"):
                wifiEnable = str(sjon["Data"]["wifiEnable"])
                mod = sjon["Data"]["mod"]
                ssid = sjon["Data"]["ssid"]
                password = sjon["Data"]["password"]
                encryptionType = sjon["Data"]["encryptionType"]
                wifidhcpcEnable = str(sjon["Data"]["wifidhcpcEnable"])
                ip = sjon["Data"]["ip"]
                netmask = sjon["Data"]["netmask"]
                gateway = sjon["Data"]["gateway"]
                self.application.databaseModule.set_wifi_settings(wifiEnable,mod,ssid,password,encryptionType,wifidhcpcEnable,ip,netmask,gateway)
                self.application.networkSettings.set_wifi()
            elif(sjon["Command"] == "OcppSettings"):
                domainName = str(sjon["Data"]["domainName"])
                port = sjon["Data"]["port"]
                sslEnable = sjon["Data"]["sslEnable"]
                authorizationKey = sjon["Data"]["authorizationKey"]
                path = sjon["Data"]["path"]
                self.application.databaseModule.set_ocpp_settings(domainName,port,sslEnable,authorizationKey,path)
            elif(sjon["Command"] == "FunctionsEnable"):
                card_type = str(sjon["Data"]["card_type"])
                whether_to_open_the_qr_code_process = sjon["Data"]["whether_to_open_the_qr_code_process"]
                local_startup_whether_to_go_ocpp_background = sjon["Data"]["local_startup_whether_to_go_ocpp_background"]
                whether_to_transfer_private_data = sjon["Data"]["whether_to_transfer_private_data"]
                self.application.databaseModule.set_functions_enable(card_type,whether_to_open_the_qr_code_process,local_startup_whether_to_go_ocpp_background,whether_to_transfer_private_data)
            elif(sjon["Command"] == "BluetoothSettings"):
                bluetooth_enable = str(sjon["Data"]["bluetooth_enable"])
                pin = sjon["Data"]["pin"]
                bluetooth_name = sjon["Data"]["bluetooth_name"]
                self.application.databaseModule.set_bluetooth_settings(bluetooth_enable,pin,bluetooth_name)
            elif(sjon["Command"] == "TimeZoneSettings"):
                timezone = str(sjon["Data"]["timezone"])
                self.application.databaseModule.set_timezone_settings(timezone)
            elif(sjon["Command"] == "FirmwareVersion"):
                version = str(sjon["Data"]["version"])
                self.application.databaseModule.set_firmware_version(version)
        
        except Exception as e:
            print("MessageReceivedws",e)
        
        