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
            elif(sjon["Command"] == "4GSettings"):
                enableModification = str(sjon["Data"]["enableModification"])
                apn = sjon["Data"]["apn"]
                user = sjon["Data"]["user"]
                password = sjon["Data"]["password"]
                pin = sjon["Data"]["pin"]
                self.application.databaseModule.set_settings_4g(apn,user,password,enableModification,pin)
            elif(sjon["Command"] == "EthernetSettings"):
                ethernetEnable = str(sjon["Data"]["ethernetEnable"])
                ip = sjon["Data"]["ip"]
                netmask = sjon["Data"]["netmask"]
                gateway = sjon["Data"]["gateway"]
                self.application.databaseModule.set_ethernet_settings(ethernetEnable,ip,netmask,gateway)
                # self.application.networkSettings.set_eth(ethernetEnable,ip,netmask,gateway)
                # data = {
                #     "ip" : ip
                # }
                # with open("/root/acApp/client/build/websocket.json", "w") as file:
                #     json.dump(data, file)
                #     print("ip yazıldı")
            elif(sjon["Command"] == "DNSSettings"):
                dnsEnable = str(sjon["Data"]["dnsEnable"])
                dns1 = sjon["Data"]["DNS1"]
                dns2 = sjon["Data"]["DNS2"]
                self.application.databaseModule.set_dns_settings(dnsEnable,dns1,dns2)
                self.application.networkSettings.set_dns(dnsEnable,dns1,dns2)
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
            elif(sjon["Command"] == "OcppSettings"):
                domainName = str(sjon["Data"]["domainName"])
                port = sjon["Data"]["port"]
                sslEnable = sjon["Data"]["sslEnable"]
                authorizationKey = sjon["Data"]["authorizationKey"]
                path = sjon["Data"]["path"]
                self.application.databaseModule.set_ocpp_settings(domainName,port,sslEnable,authorizationKey,path)
                
                
        except Exception as e:
            print("MessageReceivedws",e)
        
        