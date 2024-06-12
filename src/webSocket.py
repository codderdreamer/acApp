from os import close
from time import sleep
from datetime import datetime
import websocket_server
import json
import sys
from threading import Thread
from src.enums import *
import subprocess
import os
import time

class WebSocketModule():
    def __init__(self, application) -> None:
        self.application = application
        self.slave1 = None
        self.websocket = websocket_server.WebsocketServer('0.0.0.0',80)
        print("Web Socket Başlatılıyor... 0.0.0.0 9000")
        self.websocket.set_fn_new_client(self.NewClientws)
        self.websocket.set_fn_client_left(self.ClientLeftws)
        self.websocket.set_fn_message_received(self.MessageReceivedws)
        Thread(target=self.websocket.run_forever,daemon=True).start()

    def send_heartbeat(self,client):
        while True:
            try:
                message = {
                    "Command" : "Heartbeat",
                    "Data" : time.ti
                }
                self.websocket.send_message(client,json.dumps(message))
            except Exception as e:
                print(datetime.now(),"send_heartbeat Exception:",e)
            time.sleep(1)
        
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
                    self.save_barkod_model_cpid(client,Data)
                elif Command == "WifiMacReq":
                    self.wifimac_send(client)
                elif Command == "EthMacReq":
                    self.eth1mac_get(client)
                elif Command == "4gImeiReq":
                    self.imei4g_get(client)
                elif Command == "BluetoothSet":
                    self.application.databaseModule.set_bluetooth_settings("Enable","",self.application.settings.ocppSettings.chargePointId)
                    self.application.softwareSettings.set_bluetooth_settings()
                    self.send_bluetooth(client)
                elif Command == "WifiControl":
                    self.send_wifi_result(client)
                elif Command == "setLedRed":
                    self.application.test = True
                    self.set_led_red(client)
                elif Command == "setLedBlue":
                    self.set_led_blue(client)
                elif Command == "setLedGreen":
                    self.set_led_green(client)
                elif Command == "saveMasterCard":
                    self.save_master_card(client)
                elif Command == "SaveSlaveCard1":
                    self.save_slave_card_1(client)
                elif Command == "SaveSlaveCard2":
                    self.save_slave_card_2(client)

                # slave kart geldiğinde 1.yi hafızada tut. 2. geldiğinde 1.den farklı ise database kaydet, aynı ise lütfan farklı kart okutunuz uyarısı çıkart
                
                # elif Command == "RelayOn":
                #     self.application.serialPort.set_command_pid_relay_control(Relay.On)
                #     self.application.serialPort.get_command_pid_relay_control()
                #     print("self.application.ev.pid_relay_control",self.application.ev.pid_relay_control)
                
        
            except (Exception, RuntimeError) as e:
                print("MessageReceivedws error", e,e.__dict__)
                sys.stdout.flush()
                if client['handler'].connection._closed==False:
                    for c in server.clients:
                        if client["id"]==c["id"]:
                            c['handler'].keep_alive=False
                            c['handler'].valid_client=False
                            server.clients.remove(client)   

    def save_barkod_model_cpid(self,client,Data):
        model = Data["model"]
        chargePointId = Data["chargePointId"]
        serialNumber = Data["serialNumber"]

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
            self.application.databaseModule.set_serial_number(serialNumber)
            
            if modelReturn and chargePointIdReturn:
                message = {
                    "Command" : "ModelReturn",
                    "Data" : True
                }
                self.websocket.send_message(client,json.dumps(message))
                
    def wifimac_send(self,client):
        mac_address = ""
        try:
            result = subprocess.run(['ip', 'link'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output = result.stdout
            for line in output.splitlines():
                if 'wl' in line:  # 'wl' is a common prefix for Wi-Fi interfaces, adjust if necessary
                    interface = line.split()[1].strip(':')
                    mac_result = subprocess.run(['cat', f'/sys/class/net/{interface}/address'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    mac_address = mac_result.stdout.strip()
        except Exception as e:
            print(datetime.now(),"wifimac_get Exception:",e)
        message = {
            "Command" : "WifiMacResult",
            "Data" : mac_address
        }
        self.websocket.send_message(client,json.dumps(message))  
        
    def eth1mac_get(self,client):
        mac_address = ""
        try:
            result = subprocess.run(['ip', 'link'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output = result.stdout
            for line in output.splitlines():
                if 'eth1' in line:
                    interface = line.split()[1].strip(':')
                    mac_result = subprocess.run(['cat', f'/sys/class/net/{interface}/address'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    mac_address = mac_result.stdout.strip()
        except Exception as e:
            print(datetime.now(),"wifimac_get Exception:",e)
        message = {
            "Command" : "EthMacResult",
            "Data" : mac_address
        }
        self.websocket.send_message(client,json.dumps(message))  
        
    def imei4g_get(self,client):
        imei = ""
        try:
            if self.application.databaseModule.is_there_4G(self.application.model):
                result = subprocess.check_output("mmcli -L", shell=True).decode('utf-8')
                modem_id = result.split("/")[5].split()[0]
                modem_info = subprocess.check_output(f"mmcli -m /org/freedesktop/ModemManager1/Modem/{modem_id}", shell=True).decode('utf-8')
                for line in modem_info.split('\n'):
                    if 'imei' in line.lower():
                        imei = line.split(':')[1].strip()
            else:
                imei = "Not"
        except Exception as e:
            print(datetime.now(),"imei4g_get Exception:",e)
        message = {
            "Command" : "4gImeiResult",
            "Data" : imei
        }
        self.websocket.send_message(client,json.dumps(message))  

    def send_wifi_result(self,client):
        try:
            
            message = {
            "Command" : "WifiIpResult",
            "Data" : self.application.settings.networkip.wlan0
            }
            self.websocket.send_message(client,json.dumps(message))  

        except Exception as e:
            print(datetime.now(),"send_wifi_result Exception:",e)

    def set_led_red(self,client):
        try:
            self.application.serialPort.set_command_pid_led_control(LedState.Fault)
        except Exception as e:
            print(datetime.now(),"set_led_red Exception:",e)
        
    def set_led_blue(self,client):
        try:
            self.application.serialPort.set_command_pid_led_control(LedState.Connecting)
        except Exception as e:
            print(datetime.now(),"set_led_blue Exception:",e)

    def set_led_green(self,client):
        try:
            self.application.serialPort.set_command_pid_led_control(LedState.Connecting)
            self.application.test = False
        except Exception as e:
            print(datetime.now(),"set_led_green Exception:",e)

    def save_master_card(self,client):
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None:
                    self.application.databaseModule.set_master_card(self.application.ev.card_id)
                    message = {
                        "Command" : "MasterCard",
                        "Data" : self.application.ev.card_id
                    }
                    self.websocket.send_message(client,json.dumps(message))
                    self.application.ev.card_id = ""
                    return
            except Exception as e:
                print(datetime.now(),"save_master_card Exception:",e)
            time.sleep(0.5)

    def save_slave_card_1(self,client):
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None:
                    message = {
                        "Command" : "SlaveCard1",
                        "Data" : self.application.ev.card_id
                    }
                    self.websocket.send_message(client,json.dumps(message))
                    self.slave1 = self.application.ev.card_id
                    self.application.ev.card_id = ""
                    return
            except Exception as e:
                print(datetime.now(),"save_master_card Exception:",e)
            time.sleep(0.5)

    def save_slave_card_2(self,client):
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None and self.slave1 != self.application.ev.card_id:
                    message = {
                        "Command" : "SlaveCard2",
                        "Data" : self.application.ev.card_id
                    }
                    self.websocket.send_message(client,json.dumps(message))
                    self.application.databaseModule.set_local_list([self.slave1, self.application.ev.card_id])
                    self.application.ev.card_id = ""
                    return
            except Exception as e:
                print(datetime.now(),"save_master_card Exception:",e)
            time.sleep(0.5)

    def send_bluetooth(self,client):
        try:
            process = subprocess.Popen(['hostname'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8')
            name = output.split("\n")[0]
            print("bluetooth name",name)
            message = {
                "Command" : "Bluetooth",
                "Data" : {
                    "error" : str(self.application.bluetooth_error),
                    "name" : name
                }
            }
            self.websocket.send_message(client,json.dumps(message))
        except Exception as e:
            print(datetime.now(),"send_bluetooth Exception:",e)


                    