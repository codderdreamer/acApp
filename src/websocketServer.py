import websocket_server
import json
import threading
import time
from threading import Thread
from src.enums import *

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
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_maxcurrent())
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
            self.application.settings.set_network_priority(sjon)
            self.application.settings.set_Settings4G(sjon)
            self.application.settings.set_ethernet_settings(sjon)
            self.application.settings.set_dns_settings(sjon)
            self.application.settings.set_wifi_settings(sjon)
            self.application.settings.set_ocpp_settings(sjon)
            self.application.settings.set_functions_enable(sjon)
            self.application.settings.set_bluetooth_settings(sjon)
            self.application.settings.set_timezoon_settings(sjon)
            self.application.settings.set_firmware_version(sjon)
            self.application.settings.set_maxcurrent(sjon)
            
          
          
   
            
            
            
            
            
            
        except Exception as e:
            print("MessageReceivedws",e)
            
        
        