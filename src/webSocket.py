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
        self.simu_test = True
        self.logger = logger
        self.client = None
        self.slave1 = None
        self.slave2 = None
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
                    self.application.ev.card_id = "123456789"
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

    # wifi'yi ayağa kaldır,
    # 4G varsa 4g'yi ayağa kaldır,
    # bluetooth adını charge point id ile değiştir,
    # Bluetooth mac numarasını al,
    # ethernet mac numarasını al,
    # 4G imei numarasını al,
    # MCU'da hata varlığını al,
    # connectorType değiştir,

    def save_config(self,client,Data):
        try:
            print("4G ayarlanıyor...")
            self.up_4g(Data)
            print("Wifi ayarlanıyor...")
            self.up_Wifi(Data)
            print("Bluetooth adı değiştiririliyor...")
            self.up_bluetooth(Data)
            print("Bluetooth mac adres alınıyor...")
            bluetooth_mac = self.get_bluetooth_mac()
            print("Ethernet mac address alınıyor...")
            eth_mac = self.get_eth_mac()
            mcu_error = self.application.serialPort.error_list # list
            # connector type değiştir
            imei_4g = None
            time_start = time.time()
            while True: 
                print("ppp0 ip bekleniyor...",self.application.settings.networkip.ppp0)
                if self.application.settings.networkip.ppp0:
                    imei_4g = self.get_4g_imei(Data)
                    print("imei_4g",imei_4g)
                    break
                if time.time() - time_start > 90:
                    print("süre doldu!")
                    break
                time.sleep(3)

            message = {
                "Command": "ConfigResult",
                "Data": {
                    "bluetooth_mac" : bluetooth_mac,
                    "eth_mac" : eth_mac,
                    "mcu_error" : mcu_error,
                    "imei_4g" : imei_4g
                    }
                }
            self.websocket.send_message(client, json.dumps(message))
            

        except Exception as e:
            print("save_config Exception:",e)

    def save_master_card(self, client):
        time_start = time.time()
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None and self.slave1 != self.application.ev.card_id and self.slave2 != self.application.ev.card_id:
                    self.application.databaseModule.set_master_card(self.application.ev.card_id)
                    message = {
                        "Command": "MasterCardResult",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    self.application.ev.card_id = ""
                    return
                if time.time() - time_start > 60:
                    message = {
                        "Command": "MasterCardResult",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    return
            except Exception as e:
                print(f"save_master_card Exception: {e}")
            time.sleep(0.5)

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
                print(f"Incoming: {sjon}")
                Command = sjon["Command"]
                Data = sjon["Data"]
                # self.parse_message(client,Command,Data)
                if Command == "SaveConfig":
                    print("Cihaz bilgileri kayıt ediliyor...")
                    Thread(target=self.save_config,args=(client,Data,),daemon=True).start()
                    # self.save_config(client,Data)
                elif Command == "MasterCardRequest":
                    print("Master card bekleniyor...")
                    Thread(target=self.save_master_card, args=(client,),daemon=True).start()
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

    

    def send_wifi_result(self, client):
        try:
            message = {
                "Command": "WifiIpResult",
                "Data": self.application.settings.networkip.wlan0
            }
            self.websocket.send_message(client, json.dumps(message))
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
                    self.slave1 = self.application.ev.card_id
                    self.application.ev.card_id = ""
                    return
            except Exception as e:
                print(f"save_slave_card_1 Exception: {e}")
            time.sleep(0.5)

    def save_slave_card_2(self, client):
        while True:
            try:
                if self.application.ev.card_id != "" and self.application.ev.card_id != None and self.slave1 != self.application.ev.card_id:
                    message = {
                        "Command": "SlaveCard2",
                        "Data": self.application.ev.card_id
                    }
                    self.websocket.send_message(client, json.dumps(message))
                    self.slave2 = self.application.ev.card_id
                    self.application.databaseModule.set_default_local_list([self.slave1, self.application.ev.card_id])
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
        except Exception as e:
            print(f"send_error Exception: {e}")
