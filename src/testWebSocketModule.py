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
import re

class TestWebSocketModule():
    def __init__(self, application, logger) -> None:
        print("-------------------------------------------------------")
        self.application = application
        self.simu_test = False
        self.logger = logger
        self.client = None
        self.master_card = None
        self.user_1_card = None
        self.user_2_card = None

        self.cancel_test = False
        self.websocket = websocket_server.WebsocketServer('0.0.0.0', 9000)
        self.websocket.set_fn_new_client(self.NewClientws)
        self.websocket.set_fn_client_left(self.ClientLeftws)
        self.websocket.set_fn_message_received(self.MessageReceivedws)
        Thread(target=self.websocket.run_forever, daemon=True).start()
        Thread(target=self.test, daemon=True).start()

    def test(self):
        while True:
            try:
                x = input()
                if x == "1":
                    self.application.ev.card_id = "11111111111111"
                elif x == "2":
                    self.application.ev.card_id = "22222222222222"
                elif x == "3":
                    self.application.ev.card_id = "33333333333333"
            except Exception as e:
                # print("test")
                pass
            time.sleep(1)

    def get_eth_mac(self):
        try:
            result = subprocess.run(['ip', 'link'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output = result.stdout
            for line in output.splitlines():
                if 'eth1' in line:
                    interface = line.split()[1].strip(':')
                    mac_result = subprocess.run(['cat', f'/sys/class/net/{interface}/address'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    return mac_result.stdout.strip()
        except Exception as e:
            print("get_eth_mac Exception:",e)

    def up_Wifi(self,Data):
        try:
            sjon = {
                    "Command": "WifiSettings",
                    "Data": {
                        "wifiEnable": True,
                        "mod": "STA",
                        "ssid": Data["wifiSSID"],
                        "password": Data["wifiPassword"],
                        "encryptionType": "WPA2",
                        "wifidhcpcEnable": True,
                        "ip": None,
                        "netmask": None,
                        "gateway": None
                        }
                    }
            self.application.settings.set_wifi_settings(sjon)
        except Exception as e:
            print("up_Wifi Exception:",e)

    def up_4g(self,Data):
        try:
            if Data["fourg"]:
                print("4G up yapılıyor...")
                sjon = {
                    "Command": "4GSettings",
                                "Data": {
                                    "apn": Data["fourG_apn"],
                                    "enableModification" : True,
                                    "password" : Data["fourG_password"],
                                    "pin" : Data["fourG_pin"],
                                    "user" : Data["fourG_user"]
                                    }
                    }
                self.application.settings.set_Settings4G(sjon)
        except Exception as e:
            print("up_4g Exception:",e)

    def up_bluetooth(self,Data):
        try:
            print("Bluetooth up yapılıyor...")
            sjon = {
                        "Command": "BluetoothSettings",
                                    "Data": {
                                        "bluetooth_enable": "Enable",
                                        "bluetooth_name" : Data["chargePointId"],
                                        "pin" : ""
                                        }
                        }
            self.application.settings.set_bluetooth_settings(sjon)
        except Exception as e:
            print("up_bluetooth Exception:",e)

    def get_bluetooth_mac(self):
        try:
            result = subprocess.check_output('hciconfig', shell=True).decode('utf-8')
            print("result",result)
            # for line in result:
            #     if "BD Address" in line:
            #         match = re.search(r"BD Address: ([0-9A-F:]{17})", line)
            #         if match:
            #             print("Bluetooth mac: ",match.group(1))
            #             return match.group(1)
                    
            mac_regex = r"BD Address:\s*([A-Fa-f0-9:]{17})"
            match = re.search(mac_regex, result)
            if match:
                mac_address = match.group(1)
                print(f"Bluetooth MAC Adresi: {mac_address}")
                return mac_address
            else:
                print("Bluetooth MAC adresi bulunamadı.")
            return None
        except Exception as e:
            print("get_bluetooth_mac Exception:",e)
            return None

    def get_4g_imei(self,Data):
            try:
                if Data["fourg"]:
                    result = subprocess.check_output("mmcli -L", shell=True).decode('utf-8')
                    modem_id = result.split("/")[5].split()[0]
                    modem_info = subprocess.check_output(f"mmcli -m /org/freedesktop/ModemManager1/Modem/{modem_id}", shell=True).decode('utf-8')
                    for line in modem_info.split('\n'):
                        if 'imei' in line.lower():
                            return line.split(':')[1].strip()
            except Exception as e:
                print("get_4g_imei Exception:",e)
                return None

    def set_start_stop(self):
        try:
            print("Start and stop olarak ayarlanıyor...")
            sjon = {
                        "Command" : "FunctionsEnable",
                        "Data" : {
                            "card_type" : "StartStopCard",
                            "local_startup_whether_to_go_ocpp_background" : "no",
                            "whether_to_open_the_qr_code_process" : "no",
                            "whether_to_transfer_private_data" : "no"
                        }
                    }
            self.application.settings.set_functions_enable(sjon)
        except Exception as e:
            print("set_start_stop Exception:",e)

    def set_connector_type(self,Data):
        try:
            self.application.databaseModule.set_socket_type(Data["connectorType"] == "Type2_Socket")
        except Exception as e:
            print("set_connector_type Exception:",e)

    def set_seri_no(self,Data):
        try:
            self.application.databaseModule.set_serial_number(Data["seriNo"])
        except Exception as e:
            print("set_seri_no Exception:",e)

    def set_mid(self,Data):
        try:
            self.application.databaseModule.set_mid_settings(Data["midMeter"]=="Yes")
        except Exception as e:
            print("set_mid Exception:",e)

    def get_mcu_error(self):
        try:
            error_list = []
            for error in self.application.serialPort.error_list:
                error_list.append(error.name)
            return error_list
        except Exception as e:
            print("get_mcu_error Exception:",e)

    def wait_4g(self,Data):
        imei_4g = None
        if Data["fourg"]:
            time_start = time.time()
            while True: 
                print("ppp0 ip bekleniyor...",self.application.settings.networkip.ppp0)
                if self.application.settings.networkip.ppp0:
                    imei_4g = self.get_4g_imei(Data)
                    print("imei_4g",imei_4g)
                    return imei_4g
                if time.time() - time_start > 120:
                    print("süre doldu!")
                    break
                time.sleep(3)
        return imei_4g
    
    def wait_wlan0(self):
        wlan0_connection = False
        time_start = time.time()
        while True:
            if self.application.settings.networkip.wlan0:
                wlan0_connection = True
                return wlan0_connection
            if time.time() - time_start > 30:
                print("süre doldu!")
                break
            time.sleep(3)
        return wlan0_connection

    def save_config(self,client,Data):
        # start and stop ayarla
        # wifi'yi ayağa kaldır,
        # 4G varsa 4g'yi ayağa kaldır,
        # bluetooth adını charge point id ile değiştir,
        # Bluetooth mac numarasını al,
        # ethernet mac numarasını al,
        # 4G imei numarasını al,
        # MCU'da hata varlığını al,
        # connectorType değiştir,
        # seriNo kaydet
        # mid meter ayarla
        try:
            Thread(target=self.set_start_stop,daemon=True).start()
            Thread(target=self.up_4g,args=(Data,),daemon=True).start()
            Thread(target=self.up_Wifi,args=(Data,),daemon=True).start()
            Thread(target=self.up_bluetooth,args=(Data,),daemon=True).start()
            Thread(target=self.set_connector_type,args=(Data,),daemon=True).start()
            Thread(target=self.set_seri_no,args=(Data,),daemon=True).start()
            Thread(target=self.set_mid,args=(Data,),daemon=True).start()
            time.sleep(10)
            time_start = time.time()
            bluetooth_mac = self.get_bluetooth_mac()
            eth_mac = self.get_eth_mac()
            mcu_error = self.get_mcu_error()
            mcu_connection = self.application.serialPort.connection
            imei_4g = self.wait_4g(Data)
            wlan0_connection = self.wait_wlan0()
            message = {
                "Command": "SaveConfigResult",
                "Data": {
                    "fourg" : Data["fourg"],
                    "bluetooth_mac" : bluetooth_mac,    # string
                    "eth_mac" : eth_mac,                # string
                    "mcu_error" : mcu_error,            # list
                    "mcu_connection" : mcu_connection,  # bool
                    "imei_4g" : imei_4g,                # string
                    "wlan0_connection" : wlan0_connection   # bool
                    }
                }
            self.websocket.send_message(client, json.dumps(message))
            print("sended:",message)
            print("Total***********************",time.time()-time_start)
        except Exception as e:
            print("save_config Exception:",e)

    def save_master_card(self, client):
        time_start = time.time()
        while True:
            try:
                self.master_card = None
                self.user_1_card = None
                self.user_2_card = None
                if self.application.ev.card_id != "" and self.application.ev.card_id != None:
                    self.application.process.rfid_verified = True
                    self.application.databaseModule.set_master_card(self.application.ev.card_id)
                    message = {
                        "Command": "MasterCardResult",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    print("sended:",message)
                    self.master_card = self.application.ev.card_id
                    self.application.ev.card_id = ""
                    return
                if time.time() - time_start > 60:
                    message = {
                        "Command": "MasterCardResult",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    print("sended:",message)
                    return
            except Exception as e:
                print(f"save_master_card Exception: {e}")
            time.sleep(0.5)

    def save_user_1_card(self,client):
        time_start = time.time()
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None:
                    if self.application.ev.card_id == self.master_card:
                        self.application.process.rfid_verified = False
                        message = {
                            "Command": "User1CardResult",
                            "Data": "Same"
                        }
                        self.websocket.send_message(client, json.dumps(message))
                        self.application.ev.card_id = ""
                        return
                    else:
                        self.application.process.rfid_verified = True
                        message = {
                            "Command": "User1CardResult",
                            "Data": self.application.ev.card_id
                        }
                        self.websocket.send_message(client, json.dumps(message))
                        print("sended:",message)
                        self.user_1_card = self.application.ev.card_id
                        self.application.ev.card_id = ""
                        return
                
                if time.time() - time_start > 60:
                    message = {
                        "Command": "User1CardResult",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    print("sended:",message)
                    return
            except Exception as e:
                print(f"save_user_1_card Exception: {e}")
            time.sleep(0.5)

    def save_user_2_card(self,client):
        time_start = time.time()
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None:
                    if self.application.ev.card_id == self.master_card or self.application.ev.card_id == self.user_1_card:
                        self.application.process.rfid_verified = False
                        message = {
                            "Command": "User1CardResult",
                            "Data": "Same"
                        }
                        self.websocket.send_message(client, json.dumps(message))
                        self.application.ev.card_id = ""
                        return
                    else:
                        message = {
                            "Command": "User2CardResult",
                            "Data": self.application.ev.card_id
                        }
                        self.websocket.send_message(client, json.dumps(message))
                        print("sended:",message)
                        self.user_2_card = self.application.ev.card_id
                        self.application.ev.card_id = ""
                        self.application.databaseModule.set_default_local_list([self.user_1_card, self.user_2_card])
                        return
                if time.time() - time_start > 60:
                    message = {
                        "Command": "User2CardResult",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    print("sended:",message)
                    return
            except Exception as e:
                print(f"save_user_2_card Exception: {e}")
            time.sleep(0.5)

    def send_wait_user_1_card_result(self):
        time_start = time.time()
        while True:
            try:
                if self.application.ev.start_stop_authorize:
                    message = {
                                "Command": "WaitUser1CardResult",
                                "Data": True
                            }
                    print("sended:",message)
                    self.websocket.send_message(self.client, json.dumps(message))
                    return
                if time.time() - time_start > 60:
                    message = {
                                "Command": "WaitUser1CardResult",
                                "Data": False
                            }
                    print("sended:",message)
                    self.websocket.send_message(self.client, json.dumps(message))
                    return
                if self.cancel_test:
                    return
            except Exception as e:
                    print(f"send_wait_user_1_card_result Exception: {e}")

            time.sleep(1)

    def send_wait_user_2_card_result(self):
        time_start = time.time()
        while True:
            try:
                if self.application.ev.start_stop_authorize:
                    message = {
                                "Command": "WaitUser2CardResult",
                                "Data": True
                            }
                    print("sended:",message)
                    self.websocket.send_message(self.client, json.dumps(message))
                    return
                if time.time() - time_start > 60:
                    message = {
                                "Command": "WaitUser2CardResult",
                                "Data": False
                            }
                    print("sended:",message)
                    self.websocket.send_message(self.client, json.dumps(message))
                    return
                if self.cancel_test:
                    return
            except Exception as e:
                    print(f"send_wait_user_2_card_result Exception: {e}")

            time.sleep(1)

    def wait_role_on(self):
        time_start = time.time()
        while True:
            if self.cancel_test:
                return
            if self.application.ev.pid_relay_control == Relay.On:
                message = {
                                "Command": "WaitRelayOnResult",
                                "Data": True
                            }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
                return
            if time_start - time.time() > 60:
                message = {
                                "Command": "WaitRelayOnResult",
                                "Data": False
                            }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
                return
            time.sleep(1)

    def control_all_values_30_sn(self):
        time_start = time.time()
        while True:
            if self.cancel_test:
                return
            if time_start - time.time() > 30:
                return
            message = {
                        "Command": "ControlAllValues30snResult",
                        "Data": {
                            "current_L1" : self.application.ev.current_L1,
                            "current_L2" : self.application.ev.current_L2,
                            "current_L3" : self.application.ev.current_L3,
                            "voltage_L1" : self.application.ev.voltage_L1,
                            "voltage_L2" : self.application.ev.voltage_L2,
                            "voltage_L3" : self.application.ev.voltage_L3
                        }
                    }
            self.websocket.send_message(self.client, json.dumps(message))
            print("sended:",message)
            time.sleep(1)

    def over_current_test(self):
        time_start = time.time()
        while True:
            if self.cancel_test:
                return
            if len(self.application.serialPort.error_list) > 0:
                error_list = []
                for error in self.application.serialPort.error_list:
                    error_list.append(error.name)
                message = {
                        "Command": "OverCurrentTestResult",
                        "Data": error_list
                    }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
                return
            if time.time() - time_start > 4:
                message = {
                        "Command": "OverCurrentTestResult",
                        "Data": []
                    }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
                return

    def rcd_leakage_current_test(self):
        time_start = time.time()
        while True:
            if self.cancel_test:
                return
            if len(self.application.serialPort.error_list) > 0:
                error_list = []
                for error in self.application.serialPort.error_list:
                    error_list.append(error.name)
                message = {
                        "Command": "RCDLeakageCurrentTestResult",
                        "Data": error_list
                    }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
                return
            if time.time() - time_start > 4:
                message = {
                        "Command": "RCDLeakageCurrentTestResult",
                        "Data": []
                    }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
                return



    def NewClientws(self, client, server):
        self.client = client
        if client:
            try:
                print(f"New client connected and was given id {client['id']} {client['address']}")
                sys.stdout.flush()
            except Exception as e:
                print(f"could not get New Client id: {e}")
                sys.stdout.flush()

    def ClientLeftws(self, client, server):
        try:
            self.client = client
            if client:
                client['handler'].keep_alive = 0
                client['handler'].valid_client = False
                client['handler'].connection._closed = True
                print(f"Client disconnected client[id]:{client['id']} client['address']={client['address']}")
        except Exception as e:
            print(f"c['handler'] client remove problem: {e}")
    
    def MessageReceivedws(self, client, server, message):
        self.client = client
        if client['id']:
            try:
                sjon = json.loads(message)
                Command = sjon["Command"]
                Data = sjon["Data"]
                self.application.testCommand = Command
                print("Incoming:",sjon)
                # self.parse_message(client,Command,Data)
                if Command == "SaveConfig":
                    self.cancel_test = False
                    print("Cihaz bilgileri kayıt ediliyor...")
                    # Thread(target=self.save_config,args=(client,Data,),daemon=True).start()
                elif Command == "MasterCardRequest":
                    print("Master card bekleniyor...")
                    Thread(target=self.save_master_card, args=(client,),daemon=True).start()
                elif Command == "User1CardRequest":
                    print("User 1 Card bekleniyor...")
                    Thread(target=self.save_user_1_card, args=(client,),daemon=True).start()
                elif Command == "User2CardRequest":
                    print("User 2 Card bekleniyor...")
                    Thread(target=self.save_user_2_card, args=(client,),daemon=True).start()
                elif Command == "WaitUser1CardRequest":
                    print("Şarj için birinci kullanıcı kartı okutulması bekleniyor...")
                    self.application.databaseModule.set_max_current(6)
                    Thread(target=self.send_wait_user_1_card_result,daemon=True).start()
                elif Command == "WaitUser2CardRequest":
                    print("Şarj için ikinci kullanıcı kartı okutulması bekleniyor...")
                    self.application.databaseModule.set_max_current(6)
                    Thread(target=self.send_wait_user_2_card_result,daemon=True).start()
                elif Command == "WaitRelayOnRequest":
                    print("Rölenin On olması bekleniyor...")
                    Thread(target=self.wait_role_on,daemon=True).start()
                elif Command == "ControlAllValues30sn":
                    Thread(target=self.control_all_values_30_sn,daemon=True).start()
                elif Command == "OverCurrentTest":
                    Thread(target=self.over_current_test,daemon=True).start()
                elif Command == "RCDLeakageCurrentTest":
                    Thread(target=self.rcd_leakage_current_test,daemon=True).start()
                elif Command == "CancelTest":
                    print("test iptal edildi.")
                    self.cancel_test = True
                    

                # if Command == "Barkod":
                #     self.save_barkod_model_cpid(client, Data)
                # elif Command == "WifiMacReq":
                #     self.wifimac_send(client)
                # elif Command == "EthMacReq":
                #     self.eth1mac_get(client)
                # elif Command == "4gImeiReq":
                #     self.imei4g_get(client)
                # elif Command == "BluetoothSet":
                #     self.application.databaseModule.set_bluetooth_settings("Enable", "", self.application.settings.ocppSettings.chargePointId)
                #     self.application.softwareSettings.set_bluetooth_settings()
                #     self.send_bluetooth(client)
                # elif Command == "WifiControl":
                #     self.send_wifi_result(client)
                # elif Command == "setLedRed":
                #     self.application.test_led = True
                #     self.set_led_red(client)
                # elif Command == "setLedBlue":
                #     self.set_led_blue(client)
                # elif Command == "setLedGreen":
                #     self.set_led_green(client)
                # elif Command == "saveMasterCard":
                #     self.save_master_card(client)
                # elif Command == "SaveSlaveCard1":
                #     self.save_slave_card_1(client)
                # elif Command == "SaveSlaveCard2":
                #     self.save_slave_card_2(client)
                # elif Command == "MaxCurrent6":
                #     self.application.databaseModule.set_max_current(6)
                #     self.application.test_charge = True
            except (Exception, RuntimeError) as e:
                print(f"MessageReceivedws error: {e}")
                sys.stdout.flush()
                if client['handler'].connection._closed == False:
                    for c in server.clients:
                        if client["id"] == c["id"]:
                            c['handler'].keep_alive = False
                            c['handler'].valid_client = False
                            server.clients.remove(client)

    def parse_message(client,Command,Data):
        try:
            pass
        except Exception as e:
            print("parse_message Exception:",e)

    def save_barkod_model_cpid(self, client, Data):
        model = Data["model"]
        chargePointId = Data["chargePointId"]
        serialNumber = Data["serialNumber"]

        modelFind = False
        for device in DeviceModelType:
            if device.value == Data["model"]:
                modelFind = True
        message = {
            "Command": "Model",
            "Data": modelFind
        }
        self.websocket.send_message(client, json.dumps(message))
        print("sended:",message)
        if modelFind:
            modelReturn = self.application.databaseModule.set_model(model)
            chargePointIdReturn = self.application.databaseModule.set_charge_point_id(chargePointId)
            self.application.databaseModule.set_serial_number(serialNumber)

            if modelReturn and chargePointIdReturn:
                message = {
                    "Command": "ModelReturn",
                    "Data": True
                }
                self.websocket.send_message(client, json.dumps(message))
                print("sended:",message)

    def wifimac_send(self, client):
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
            print(f"wifimac_get Exception: {e}")
        message = {
            "Command": "WifiMacResult",
            "Data": mac_address
        }
        self.websocket.send_message(client, json.dumps(message))
        print("sended:",message)

    def eth1mac_get(self, client):
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
            print(f"wifimac_get Exception: {e}")
        message = {
            "Command": "EthMacResult",
            "Data": mac_address
        }
        self.websocket.send_message(client, json.dumps(message))
        print("sended:",message)

    def send_wifi_result(self, client):
        try:
            message = {
                "Command": "WifiIpResult",
                "Data": self.application.settings.networkip.wlan0
            }
            self.websocket.send_message(client, json.dumps(message))
            print("sended:",message)
        except Exception as e:
            print(f"send_wifi_result Exception: {e}")

    def set_led_red(self, client):
        try:
            self.application.led_state =LedState.Fault
        except Exception as e:
            print(f"set_led_red Exception: {e}")

    def set_led_blue(self, client):
        try:
            self.application.led_state =LedState.Connecting
        except Exception as e:
            print(f"set_led_blue Exception: {e}")

    def set_led_green(self, client):
        try:
            self.application.led_state =LedState.Connecting
            self.application.test_led = False
        except Exception as e:
            print(f"set_led_green Exception: {e}")

    def save_slave_card_1(self, client):
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None:
                    message = {
                        "Command": "SlaveCard1",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    print("sended:",message)
                    self.user_1_card = self.application.ev.card_id
                    self.application.ev.card_id = ""
                    return
            except Exception as e:
                print(f"save_slave_card_1 Exception: {e}")
            time.sleep(0.5)

    def save_slave_card_2(self, client):
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None and self.user_1_card != self.application.ev.card_id:
                    message = {
                        "Command": "SlaveCard2",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    print("sended:",message)
                    self.user_2_card = self.application.ev.card_id
                    self.application.databaseModule.set_default_local_list([self.user_1_card, self.application.ev.card_id])
                    self.application.ev.card_id = ""
                    return
            except Exception as e:
                print(f"save_slave_card_2 Exception: {e}")
            time.sleep(0.5)

    def send_bluetooth(self, client):
        try:
            process = subprocess.Popen(['hostname'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8')
            name = output.split("\n")[0]
            print(f"bluetooth name: {name}")
            message = {
                "Command": "Bluetooth",
                "Data": {
                    "error": str(self.application.bluetooth_error),
                    "name": name
                }
            }
            self.websocket.send_message(client, json.dumps(message))
            print("sended:",message)
        except Exception as e:
            print(f"send_bluetooth Exception: {e}")

    def send_socket_connected(self):
        try:
            if self.application.test_charge:
                message = {
                    "Command": "SocketConnected",
                    "Data": ""
                }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
        except Exception as e:
            print(f"send_socket_connected Exception: {e}")

    def send_socket_type(self, socketType):
        try:
            if self.application.test_charge:
                message = {
                    "Command": "SocketType",
                    "Data": socketType
                }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
        except Exception as e:
            print(f"send_socket_type Exception: {e}")

    def send_locker_state_lock(self, locker_state):
        try:
            if self.application.test_charge:
                message = {
                    "Command": "LockerStateLock",
                    "Data": locker_state
                }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
        except Exception as e:
            print(f"send_locker_state_lock Exception: {e}")

    def send_relay_control_on(self, relay):
        try:
            if self.application.test_charge:
                message = {
                    "Command": "RelayStateOn",
                    "Data": relay
                }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
        except Exception as e:
            print(f"send_relay_control_on Exception: {e}")

    def send_there_is_mid_meter(self, mid):
        try:
            if self.application.test_charge:
                message = {
                    "Command": "MidMeterKnow",
                    "Data": mid
                }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
        except Exception as e:
            print(f"send_there_is_mid_meter Exception: {e}")

    def send_mid_meter_state(self, state):
        try:
            if self.application.test_charge:
                message = {
                    "Command": "MidMeterState",
                    "Data": state
                }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
        except Exception as e:
            print(f"send_mid_meter_state Exception: {e}")

    def send_error(self, error):
        try:
            if self.application.test_charge:
                message = {
                    "Command": "Error",
                    "Data": error
                }
                self.websocket.send_message(self.client, json.dumps(message))
                print("sended:",message)
        except Exception as e:
            print(f"send_error Exception: {e}")
