import websocket_server
import json
import threading
import time
from threading import Thread
from src.enums import *
from datetime import datetime

class WebSocketServer():
    def __init__(self) -> None:
        self.application = None
        self.websocketServer = websocket_server.WebsocketServer('0.0.0.0', 8000)
        self.websocketServer.set_fn_new_client(self.NewClientws)
        self.websocketServer.set_fn_client_left(self.ClientLeftws)
        self.websocketServer.set_fn_message_received(self.MessageReceivedws)
        # threading.Thread(target=self.websocketServer.run_forever, daemon=True).start()
        
    def NewClientws(self, client, server):
        if client:
            try:
                print(f"New client connected and was given id {client['id']}, {client['address']}")
                
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
                self.websocketServer.send_message_to_all(msg = self.application.settings.get_mid_meter())
            except Exception as e:
                print(f"NewClientws Exception: {e}")
                
    def ClientLeftws(self, client, server):
        try:
            print(f"Client disconnected client[id]:{client['id']}  client['address'] ={client['address']}")
        except Exception as e:
            print(f"ClientLeftws Exception: {e}")
            
    def MessageReceivedws(self, client, server, message):
        try:
            sjon = json.loads(message)
            print(f"Received message: {sjon}")
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
            self.application.settings.set_start_transaction(sjon)
            self.application.settings.set_stop_transaction(sjon)
            self.application.settings.set_external_mid_meter(sjon)
        except Exception as e:
            print(f"MessageReceivedws Exception: {e}")
