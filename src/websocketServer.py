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
        self.websocketServer.send_message_to_all(msg = json.dumps(command))

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
        self.websocketServer.send_message_to_all(msg = json.dumps(command))
        
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
        self.websocketServer.send_message_to_all(msg = json.dumps(command))
        
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
        self.websocketServer.send_message_to_all(msg = json.dumps(command))
        
    def send_wifi_settings(self):
        command = {
                    "Command" : "WifiSettings",
                    "Data" : {
                                "wifiEnable" : bool(self.application.settings.wifiSettings.wifiEnable=="True"),
                                "mod" : self.application.settings.wifiSettings.mod,
                                "ssid" : self.application.settings.wifiSettings.ssid,
                                "password" : self.application.settings.wifiSettings.password,
                                "encryptionType" : self.application.settings.wifiSettings.encryptionType
                            }
                }
        print("Gönderilen:",command)
        self.websocketServer.send_message_to_all(msg = json.dumps(command))
        
    def NewClientws(self, client, server):
        if client:
            try:
                print("New client connected and was given id %d" % client['id'], client['address'] )
                self.send_network_priority()
                self.send_4g_settings()
                self.send_ethernet_settings()
                self.send_dns_settings()
                self.send_wifi_settings()
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
                enableModification = str(sjon["Data"]["enableWorkmode"])
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
                self.application.networkSettings.set_eth(ethernetEnable,ip,netmask,gateway)
                data = {
                    "ip" : ip
                }
                with open("/root/acApp/client/build/websocket.json", "w") as file:
                    json.dump(data, file)
                    print("ip yazıldı")
            elif(sjon["Command"] == "DNSSettings"):
                dnsEnable = str(sjon["Data"]["dnsEnable"])
                dns1 = sjon["Data"]["dns1"]
                dns2 = sjon["Data"]["dns2"]
                self.application.databaseModule.set_dns_settings(dnsEnable,dns1,dns2)
            elif(sjon["Command"] == "WifiSettings"):
                wifiEnable = str(sjon["Data"]["wifiEnable"])
                mod = sjon["Data"]["mod"]
                ssid = sjon["Data"]["ssid"]
                password = sjon["Data"]["password"]
                encryptionType = sjon["Data"]["encryptionType"]
                self.application.databaseModule.set_wifi_settings(wifiEnable,mod,ssid,password,encryptionType)
            
        except Exception as e:
            print("MessageReceivedws",e)
        
        
        
        

# websocketServer = websocket_server.WebsocketServer('0.0.0.0',8000)

# def NewClientws(client, server):
#     if client:
#         try:
#             print("New client connected and was given id %d" % client['id'], client['address'] )
#         except Exception as e:
#             print("could not get New Client id",e)
            
# def ClientLeftws(client, server):
#     try:
#         print("Client disconnected client[id]:{}  client['address'] ={}  ".format(client["id"], client['address'] ))
#     except Exception as e:
#         print("c['handler'] client remove problem",e )
        
# def MessageReceivedws(client, server, message):
#     try:
#         sjon = json.loads(message)
#         print(sjon)
        
#     except Exception as e:
#         print("MessageReceivedws",e)


# websocketServer.set_fn_new_client(NewClientws)
# websocketServer.set_fn_client_left(ClientLeftws)
# websocketServer.set_fn_message_received(MessageReceivedws)

# threading.Thread(target=websocketServer.run_forever(), daemon=True).start()

# while True:
#     time.sleep(1)