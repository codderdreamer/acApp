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
        
    def send_network_priority(self,client):
        command = {
                    "Command" : "NetworkPriority",
                    "Data" : {
                                "enableWorkmode" : bool(self.application.settings.networkPriority.enableWorkmode),
                                "1" : self.application.settings.networkPriority.first,
                                "2" : self.application.settings.networkPriority.second,
                                "3" : self.application.settings.networkPriority.third
                            }
                }
        print("Gönderilen:",command)
        self.websocketServer.send_message(client=client,msg = json.dumps(command))

    def send_4g_settings(self,client):
        command = {
                    "Command" : "4GSettings",
                    "Data" : {
                                "enableModification" : bool(self.application.settings.settings4G.enableModification),
                                "apn" : self.application.settings.settings4G.apn,
                                "user" : self.application.settings.settings4G.user,
                                "password" : self.application.settings.settings4G.password,
                                "pin" : self.application.settings.settings4G.pin,
                            }
                }
        print("Gönderilen:",command)
        self.websocketServer.send_message(client=client,msg = json.dumps(command))
        
    
    def NewClientws(self, client, server):
        if client:
            try:
                print("New client connected and was given id %d" % client['id'], client['address'] )
                self.send_network_priority(client)
                self.send_4g_settings(client)
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