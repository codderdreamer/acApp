from os import close
from time import sleep
from datetime import datetime
import websocket_server
import json
import sys
from threading import Thread
from src.enums import *

class WebSocketModule():
    def __init__(self, application) -> None:
        self.application = application
        self.websocket = websocket_server.WebsocketServer('0.0.0.0',9000)
        print("Web Socket Başlatılıyor... 0.0.0.0 9000")
        self.websocket.set_fn_new_client(self.NewClientws)
        self.websocket.set_fn_client_left(self.ClientLeftws)
        self.websocket.set_fn_message_received(self.MessageReceivedws)
        Thread(target=self.websocket.run_forever,daemon=True).start()
        
    def NewClientws(self, client, server):
        if client:
            try:
                print("New client connected and was given id %d" % client['id'], client['address'] )
                sys.stdout.flush()
            except Exception as e:
                print("could not get New Client id",e)
                sys.stdout.flush()  
                
    def ClientLeftws(self, client, server):
        try:
            if client:
                client['handler'].keep_alive=0
                client['handler'].valid_client=False
                client['handler'].connection._closed=True
                print("Client disconnected client[id]:{}  client['address'] ={}  ".format(client["id"], client['address'] ))
        except Exception as e:
            print("c['handler'] client remove problem",e )
            
  
    def MessageReceivedws(self, client, server, message):
        if client['id']:
            try:
                sjon = json.loads(message)
                print("Incoming:",sjon)
                Command = sjon["Command"]
                Data = sjon["Data"]
                if Command == "Barkod":
                    model = Data["model"]
                    chargePointId = Data["chargePointId"]
                    modelFind = False
                    for device in DeviceModelType:
                        if device.value == Data["model"]:
                            modelFind = True
                    message = {
                        "Command" : "Model",
                        "Data" : modelFind
                    }
                    self.websocket.send_message(client,json.dumps(message))
                    if modelFind:
                        modelReturn = self.application.databaseModule.set_model(model)
                        chargePointIdReturn = self.application.databaseModule.set_charge_point_id(chargePointId)
                        
                        
                        if modelReturn and chargePointIdReturn:
                            message = {
                                "Command" : "ModelReturn",
                                "Data" : True
                            }
                            self.websocket.send_message(client,json.dumps(message))
                
        
            except (Exception, RuntimeError) as e:
                print("MessageReceivedws error", e,e.__dict__)
                sys.stdout.flush()
                if client['handler'].connection._closed==False:
                    for c in server.clients:
                        if client["id"]==c["id"]:
                            c['handler'].keep_alive=False
                            c['handler'].valid_client=False
                            server.clients.remove(client)   

# websocket = websocket_server.WebsocketServer('0.0.0.0',9000)

# def NewClientws(client, server):
#     if client:
#         try:
#             print("New client connected and was given id %d" % client['id'], client['address'] )
#             sys.stdout.flush()
#         except Exception as e:
#             print("could not get New Client id",e)
#             sys.stdout.flush()  

# def ClientLeftws(client, server):
#     try:
#         if client:
#             client['handler'].keep_alive=0
#             client['handler'].valid_client=False
#             client['handler'].connection._closed=True
#             print("Client disconnected client[id]:{}  client['address'] ={}  ".format(client["id"], client['address'] ))
#     except Exception as e:
#         print("c['handler'] client remove problem",e )
    
# def MessageReceivedws(client, server, message):
#     if client['id']:
#         try:
#             sjon = json.loads(message)
#             print("Incoming:",sjon)
#             Command = sjon["Command"]
#             Data = sjon["Data"]
#             if Command == "Barkod":
#                 Data["model"]
#                 Data["chargePointId"]
#                 modelFind = False
#                 for device in DeviceModelType:
#                     if device.value == Data["model"]:
#                         modelFind = True
#                 message = {
#                     "Command" : "Model",
#                     "Data" : modelFind
#                 }
#                 websocket.send_message(client,json.dumps(message))

            
      
#         except (Exception, RuntimeError) as e:
#             print("MessageReceivedws error", e,e.__dict__)
#             sys.stdout.flush()
#             if client['handler'].connection._closed==False:
#                 for c in server.clients:
#                     if client["id"]==c["id"]:
#                         c['handler'].keep_alive=False
#                         c['handler'].valid_client=False
#                         server.clients.remove(client)   
                     
# websocket.set_fn_new_client(NewClientws)
# websocket.set_fn_client_left(ClientLeftws)
# websocket.set_fn_message_received(MessageReceivedws)