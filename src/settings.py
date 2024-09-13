import json
from datetime import datetime
import time
from threading import Thread
from src.enums import *
from src.modbusModule import ModbusModule
from src.logger import ac_app_logger as logger
import os
import base64 


class Settings():
    def __init__(self, application) -> None:
        self.application = application
        self.networkPriority = NetworkPriority()
        self.settings4G = Settings4G()
        self.ethernetSettings = EthernetSettings()
        self.dnsSettings = DNSSettings()
        self.wifiSettings = WifiSettings()
        self.ocppSettings = OcppSettings()
        self.functionsEnable = FunctionsEnable()
        self.bluetoothSettings = BluetoothSettings()
        self.timezoonSettings = TimeZoneSettings()
        self.firmwareVersion = FirmwareVersion()
        self.deviceSettings = DeviceSettings()
        self.deviceStatus = DeviceStatus()
        self.networkip = NeworkIP()
        self.configuration = Configuration(application)
        self.diagnosticsStatusSettings = DiagnosticsStatusSettings()
        
        self.change_ocpp = False

    def set_websocket_ip(self, ip):
        try:
            data = {"ip": ip}
            with open("/root/acApp/client/build/websocket.json", "w") as file:
                json.dump(data, file)
        except Exception as e:
            print("set_websocket_ip Exception:",e)

    def get_network_priority(self):
        command = {
            "Command": "NetworkPriority",
            "Data": {
                "enableWorkmode": bool(self.networkPriority.enableWorkmode == "True"),
                "1": self.networkPriority.first,
                "2": self.networkPriority.second,
                "3": self.networkPriority.third
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_Settings4G(self):
        command = {
            "Command": "4GSettings",
            "Data": {
                "enableModification": bool(self.settings4G.enableModification == "True"),
                "apn": self.settings4G.apn,
                "user": self.settings4G.user,
                "password": self.settings4G.password,
                "pin": self.settings4G.pin,
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_ethernet_settings(self):
        command = {
            "Command": "EthernetSettings",
            "Data": {
                "ethernetEnable": bool(self.ethernetSettings.ethernetEnable == "True"),
                "dhcpcEnable": bool(self.ethernetSettings.dhcpcEnable == "True"),
                "ip": self.ethernetSettings.ip,
                "netmask": self.ethernetSettings.netmask,
                "gateway": self.ethernetSettings.gateway
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_dns_settings(self):
        command = {
            "Command": "DNSSettings",
            "Data": {
                "dnsEnable": bool(self.dnsSettings.dnsEnable == "True"),
                "DNS1": self.dnsSettings.DNS1,
                "DNS2": self.dnsSettings.DNS2
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_wifi_settings(self):
        command = {
            "Command": "WifiSettings",
            "Data": {
                "wifiEnable": bool(self.wifiSettings.wifiEnable == "True"),
                "mod": self.wifiSettings.mod,
                "ssid": self.wifiSettings.ssid,
                "password": self.wifiSettings.password,
                "encryptionType": self.wifiSettings.encryptionType,
                "wifidhcpcEnable": bool(self.wifiSettings.wifidhcpcEnable == "True"),
                "ip": self.wifiSettings.ip,
                "netmask": self.wifiSettings.netmask,
                "gateway": self.wifiSettings.gateway
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_ocpp_settings(self):
        command = {
            "Command": "OcppSettings",
            "Data": {
                "domainName": self.ocppSettings.domainName,
                "port": self.ocppSettings.port,
                "sslEnable": self.ocppSettings.sslEnable,
                "authorizationKey": self.ocppSettings.authorizationKey,
                "path": self.ocppSettings.path,
                "chargePointId": self.ocppSettings.chargePointId,
                "certFileName": self.ocppSettings.certFileName
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_functions_enable(self):
        command = {
            "Command": "FunctionsEnable",
            "Data": {
                "card_type": self.functionsEnable.card_type,
                "whether_to_open_the_qr_code_process": self.functionsEnable.whether_to_open_the_qr_code_process,
                "local_startup_whether_to_go_ocpp_background": self.functionsEnable.local_startup_whether_to_go_ocpp_background,
                "whether_to_transfer_private_data": self.functionsEnable.whether_to_transfer_private_data
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_bluetooth_settings(self):
        command = {
            "Command": "BluetoothSettings",
            "Data": {
                "bluetooth_enable": self.bluetoothSettings.bluetooth_enable,
                "pin": self.bluetoothSettings.pin,
                "bluetooth_name": self.bluetoothSettings.bluetooth_name
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_timezoon_settings(self):
        command = {
            "Command": "TimeZoneSettings",
            "Data": {
                "timezone": self.timezoonSettings.timezone
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_firmware_version(self):
        command = {
            "Command": "FirmwareVersion",
            "Data": {
                "version": self.firmwareVersion.version
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_charging(self):
        duration = None
        if self.application.ev.start_date != None and self.application.ev.start_date != "":
            date_obj = datetime.strptime(self.application.ev.start_date, "%d-%m-%Y %H:%M")
            second = int(time.time() - time.mktime(date_obj.timetuple()))
            hour, remainder = divmod(second, 3600)
            minute, second = divmod(remainder, 60)
            duration = f"{hour:02d}:{minute:02d}:{second:02d}"
        
        command = {
            "Command": "Charging",
            "Data": {
                "charge": self.application.ev.charge,
                "start_date": self.application.ev.start_date,
                "duration": duration,
                "current_L1": self.application.ev.current_L1,
                "current_L2": self.application.ev.current_L2,
                "current_L3": self.application.ev.current_L3,
                "voltage_L1": self.application.ev.voltage_L1,
                "voltage_L2": self.application.ev.voltage_L2,
                "voltage_L3": self.application.ev.voltage_L3,
                "power": self.application.ev.power,
                "energy": self.application.ev.energy,
                "temperature": self.application.ev.temperature
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_device_status(self):
        command = {
            "Command": "DeviceStatus",
            "Data": {
                "linkStatus": self.deviceStatus.linkStatus,
                "strenghtOf4G": self.deviceStatus.strenghtOf4G,
                "networkCard": self.deviceStatus.networkCard,
                "stateOfOcpp": self.deviceStatus.stateOfOcpp
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_maxcurrent(self):
        command = {
            "Command": "ACCurrent",
            "Data": {
                "maxcurrent": self.application.max_current
            }
        }
        json_string = json.dumps(command)
        return json_string

    def get_mid_meter(self):
        command = {
            "Command": "MidMeter",
            "Data": {
                "externalMid": self.deviceSettings.externalMidMeter,
                "mid_id": int(self.deviceSettings.externalMidMeterSlaveAddress)
            }
        }
        json_string = json.dumps(command)
        return json_string

    def set_external_mid_meter(self, sjon):
        try:
            if(sjon["Command"] == "MidMeter"):
                externalMid = str(sjon["Data"]["externalMid"])
                external_mid_id = sjon["Data"]["mid_id"]
                self.application.databaseModule.set_external_mid_settings(externalMid, external_mid_id)

                if self.deviceSettings.externalMidMeter:
                    self.application.modbusModule.change_slave_address(self.deviceSettings.externalMidMeterSlaveAddress)
                elif self.deviceSettings.mid_meter:
                    self.application.modbusModule.change_slave_address(self.deviceSettings.midMeterSlaveAddress)

                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_mid_meter())
        except Exception as e:
            print("set_external_mid_meter Exception:",e)

    def set_network_priority(self, sjon):
        try:
            if(sjon["Command"] == "NetworkPriority"):
                enableWorkmode = str(sjon["Data"]["enableWorkmode"])
                first = sjon["Data"]["1"]
                second = sjon["Data"]["2"]
                third = sjon["Data"]["3"]
                self.application.databaseModule.set_network_priority(enableWorkmode, first, second, third)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_network_priority())
        except Exception as e:
            print("set_network_priority Exception:", e)

    def set_Settings4G(self, sjon):
        try:
            if(sjon["Command"] == "4GSettings"):
                enableModification = str(sjon["Data"]["enableModification"])
                apn = sjon["Data"]["apn"]
                user = sjon["Data"]["user"]
                password = sjon["Data"]["password"]
                pin = sjon["Data"]["pin"]
                self.application.databaseModule.set_settings_4g(apn, user, password, enableModification, pin)
                self.application.softwareSettings.set_4G()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_Settings4G())
        except Exception as e:
            print("set_Settings4G Exception:",e)

    def set_ethernet_settings(self, sjon):
        try:
            if (sjon["Command"] == "EthernetSettings"):
                ethernetEnable = str(sjon["Data"]["ethernetEnable"])
                dhcpcEnable = str(sjon["Data"]["dhcpcEnable"])
                ip = sjon["Data"]["ip"]
                netmask = sjon["Data"]["netmask"]
                gateway = sjon["Data"]["gateway"]
                self.application.databaseModule.set_ethernet_settings(ethernetEnable, dhcpcEnable, ip, netmask, gateway)
                self.application.softwareSettings.set_eth()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_ethernet_settings())
        except Exception as e:
            print("set_ethernet_settings Exception:",e)

    def set_dns_settings(self, sjon):
        try:
            if (sjon["Command"] == "DNSSettings"):
                dnsEnable = str(sjon["Data"]["dnsEnable"])
                dns1 = sjon["Data"]["DNS1"]
                dns2 = sjon["Data"]["DNS2"]
                self.application.databaseModule.set_dns_settings(dnsEnable, dns1, dns2)
                self.application.softwareSettings.set_dns()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_dns_settings())
        except Exception as e:
            print("set_dns_settings Exception:",e)

    def set_wifi_settings(self, sjon):
        try:
            if (sjon["Command"] == "WifiSettings"):
                wifiEnable = str(sjon["Data"]["wifiEnable"])
                mod = sjon["Data"]["mod"]
                ssid = sjon["Data"]["ssid"]
                password = sjon["Data"]["password"]
                encryptionType = sjon["Data"]["encryptionType"]
                wifidhcpcEnable = str(sjon["Data"]["wifidhcpcEnable"])
                ip = sjon["Data"]["ip"]
                netmask = sjon["Data"]["netmask"]
                gateway = sjon["Data"]["gateway"]
                self.application.databaseModule.set_wifi_settings(wifiEnable, mod, ssid, password, encryptionType, wifidhcpcEnable, ip, netmask, gateway)
                self.application.softwareSettings.set_wifi()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_wifi_settings())
        except Exception as e:
            print("set_wifi_settings Exception:",e)

    def set_ocpp_settings(self, sjon):
        try:
            if (sjon["Command"] == "OcppSettings"):
                domainName = str(sjon["Data"]["domainName"])
                port = sjon["Data"]["port"]
                sslEnable = sjon["Data"]["sslEnable"]
                authorizationKey = sjon["Data"]["authorizationKey"]
                path = sjon["Data"]["path"]
                chargePointId = sjon["Data"]["chargePointId"]
                certFileName = sjon["Data"]["certFileName"]
                self.application.databaseModule.set_ocpp_settings(domainName, port, sslEnable, authorizationKey, path, chargePointId, certFileName)
                if "certificate" in sjon["Data"]:
                    certificate_base64 = sjon["Data"]["certificate"]
                    self.save_certificate(certificate_base64)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_ocpp_settings())
                self.change_ocpp = True
        except Exception as e:
            print("set_ocpp_settings Exception:",e)

    def save_certificate(self, certificate_base64):
        try:
            certs_dir = '/etc/acApp/certs'
            create_file_name = "local_certificate.pem"
            file_path = os.path.join(certs_dir, create_file_name)
            if not os.path.exists(certs_dir):
                os.makedirs(certs_dir)
            if not certificate_base64:
                self.application.databaseModule.clear_certificate_name()
                print("Certificate name removed from the database.")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Certificate file {file_path} deleted.")
            else:
                certificate_bytes = base64.b64decode(certificate_base64)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Old certificate file {file_path} deleted.")
                with open(file_path, 'wb') as cert_file:
                    cert_file.write(certificate_bytes)
                print(f"Certificate saved as {file_path}")
        except Exception as e:
            print(f"save_certificate Exception: {e}")

    def set_functions_enable(self, sjon):
        try:
            if (sjon["Command"] == "FunctionsEnable"):
                card_type = str(sjon["Data"]["card_type"])
                whether_to_open_the_qr_code_process = sjon["Data"]["whether_to_open_the_qr_code_process"]
                local_startup_whether_to_go_ocpp_background = sjon["Data"]["local_startup_whether_to_go_ocpp_background"]
                whether_to_transfer_private_data = sjon["Data"]["whether_to_transfer_private_data"]
                self.application.databaseModule.set_functions_enable(card_type, whether_to_open_the_qr_code_process, local_startup_whether_to_go_ocpp_background, whether_to_transfer_private_data)
                self.application.softwareSettings.set_functions_enable()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_functions_enable())
        except Exception as e:
            print("set_functions_enable Exception:",e)

    def set_bluetooth_settings(self, sjon):
        try:
            if (sjon["Command"] == "BluetoothSettings"):
                bluetooth_enable = str(sjon["Data"]["bluetooth_enable"])
                pin = sjon["Data"]["pin"]
                bluetooth_name = sjon["Data"]["bluetooth_name"]
                self.application.databaseModule.set_bluetooth_settings(bluetooth_enable, pin, bluetooth_name)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_bluetooth_settings())
                self.application.softwareSettings.set_bluetooth_settings()
        except Exception as e:
            print("set_bluetooth_settings Exception:",e)

    def set_timezoon_settings(self, sjon):
        try:
            if (sjon["Command"] == "TimeZoneSettings"):
                timezone = str(sjon["Data"]["timezone"])
                self.application.databaseModule.set_timezone_settings(timezone)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_timezoon_settings())
                self.application.softwareSettings.set_timezoon()
        except Exception as e:
            print("set_timezoon_settings Exception:",e)

    def set_firmware_version(self, sjon):
        try:
            if (sjon["Command"] == "FirmwareVersion"):
                version = str(sjon["Data"]["version"])
                self.application.databaseModule.set_firmware_version(version)
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_firmware_version())
        except Exception as e:
            print("set_firmware_version Exception:",e)

    def set_maxcurrent(self, sjon):
        try:
            if (sjon["Command"] == "ACCurrent"):
                maxcurrent = str(sjon["Data"]["maxcurrent"])
                self.application.databaseModule.set_max_current(maxcurrent)
                self.application.process.set_max_current()
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_maxcurrent())
        except Exception as e:
            print("set_maxcurrent Exception:",e)

    def set_start_transaction(self, sjon):
        try:
            if (sjon["Command"] == "StartTransaction"):
                self.application.ev.start_stop_authorize = True
        except Exception as e:
            print("set_start_transaction Exception:",e)

    def set_stop_transaction(self, sjon):
        try:
            if (sjon["Command"] == "StopTransaction"):
                self.application.deviceState = DeviceState.STOPPED_BY_USER
        except Exception as e:
            print("set_stop_transaction Exception:",e)

    def set_unlock(self, sjon):
        try:
            if (sjon["Command"] == "UnlockConnector"):
                self.application.deviceState = DeviceState.STOPPED_BY_USER
        except Exception as e:
            print("set_unlock Exception:",e)

    def set_diagnostics_status(self, status: str):
        self.diagnosticsStatusSettings.set_status(status)
        self.application.databaseModule.set_diagnostics_status(status)

    def get_diagnostics_status(self) -> str:
        return self.diagnosticsStatusSettings.get_status()
    
    def get_diagnostics_last_update_time(self) -> str:
        return self.diagnosticsStatusSettings.get_last_update_time()

class NetworkPriority():
    def __init__(self) -> None:
        self.enableWorkmode = None
        self.first = None
        self.second = None
        self.third = None

class Settings4G():
    def __init__(self) -> None:
        self.apn = None
        self.user = None
        self.password = None
        self.pin = None
        self.enableModification = None
        
class EthernetSettings():
    def __init__(self) -> None:
        self.ethernetEnable = None
        self.dhcpcEnable = None
        self.ip = None
        self.netmask = None
        self.gateway = None

class DNSSettings():
    def __init__(self) -> None:
        self.dnsEnable = None
        self.DNS1 = None
        self.DNS2 = None

class WifiSettings():
    def __init__(self) -> None:
        self.wifiEnable = None
        self.mod = None
        self.ssid = None
        self.password = None
        self.encryptionType = None
        self.wifidhcpcEnable = None
        self.ip = None
        self.netmask = None
        self.gateway = None
        
class OcppSettings():
    def __init__(self) -> None:
        self.domainName = None
        self.port = None
        self.sslEnable = None
        self.authorizationKey = None
        self.path = None
        self.chargePointId = None
        self.certFileName = None
        
class FunctionsEnable():
    def __init__(self) -> None:
        self.card_type = None
        self.whether_to_open_the_qr_code_process = None
        self.local_startup_whether_to_go_ocpp_background = None
        self.whether_to_transfer_private_data = None
        
class BluetoothSettings():
    def __init__(self) -> None:
        self.bluetooth_enable = None
        self.pin = None
        self.bluetooth_name = None
        
class TimeZoneSettings():
    def __init__(self) -> None:
        self.timezone = None
        
class FirmwareVersion():
    def __init__(self) -> None:
        self.version = None
        
class DeviceStatus():
    def __init__(self) -> None:
        self.linkStatus = None
        self.strenghtOf4G = None
        self.networkCard = None
        self.stateOfOcpp = None  

class ACCurrent():
    def __init__(self) -> None:
        self.maxcurrent = None
        
class NeworkIP():
    def __init__(self) -> None:
        self.eth1 = None
        self.ppp0 = None
        self.wlan0 = None
        
class DeviceSettings():
    def __init__(self) -> None:
        self.availability = None
        self.max_current = None
        self.mid_meter = None
        self.midMeterSlaveAddress = None
        self.externalMidMeter = None
        self.externalMidMeterSlaveAddress = None
        self.username = None
        self.password = None

class Configuration():
    def __init__(self, application) -> None:
        self.application = application 
        self.AllowOfflineTxForUnknownId = None
        self.AuthorizationCacheEnabled = None
        self.AuthorizeRemoteTxRequests = None
        self.BlinkRepeat = None
        self.ClockAlignedDataInterval = None
        self.ConnectionTimeOut = None
        self.GetConfigurationMaxKeys = None
        self.HeartbeatInterval = None
        self.LightIntensity = None
        self.LocalAuthorizeOffline = None
        self.LocalPreAuthorize = None
        self.MaxEnergyOnInvalidId = None
        self.MeterValuesAlignedData = None
        self.MeterValuesAlignedDataMaxLength = None
        self.MeterValuesSampledData = None
        self.MeterValuesSampledDataMaxLength = None
        self.MeterValueSampleInterval = None
        self.MinimumStatusDuration = None
        self.NumberOfConnectors = None
        self.ResetRetries = None
        self.ConnectorPhaseRotation = None
        self.ConnectorPhaseRotationMaxLength = None
        self.StopTransactionOnEVSideDisconnect = None
        self.StopTransactionOnInvalidId = None
        self.StopTxnAlignedData = None
        self.StopTxnAlignedDataMaxLength = None
        self.StopTxnSampledData = None
        self.StopTxnSampledDataMaxLength = None
        self.SupportedFeatureProfiles = None
        self.SupportedFeatureProfilesMaxLength = None
        self.TransactionMessageAttempts = None
        self.TransactionMessageRetryInterval = None
        self.UnlockConnectorOnEVSideDisconnect = None
        self.WebSocketPingInterval = None
        self.LocalAuthListEnabled = None
        self.LocalAuthListMaxLength = None
        self.SendLocalListMaxLength = None
        self.ReserveConnectorZeroSupported = None
        self.ChargeProfileMaxStackLevel = None
        self.ChargingScheduleAllowedChargingRateUnit = None
        self.ChargingScheduleMaxPeriods = None
        self.ConnectorSwitch3to1PhaseSupported = None
        self.MaxChargingProfilesInstalled = None

    def load_configuration_from_db(self):
        try:
            config_data = self.application.databaseModule.get_configuration()
            max_keys = int(self.GetConfigurationMaxKeys)
            for index, config in enumerate(config_data):
                if index >= max_keys:
                    break
                setattr(self, config['key'], config['value'])
        except Exception as e:
            print("load_configuration_from_db Exception:", e)

class DiagnosticsStatusSettings():
    def __init__(self) -> None:
        self.status = None
        self.last_update_time = None

    def load_diagnostics_status(self, databaseModule):
        diagnostics_data = self.databaseModule.get_diagnostics_status()
        if diagnostics_data:
            self.status = diagnostics_data['status']
            self.last_update_time = diagnostics_data['last_update_time']

    def set_status(self, status: str):
        self.status = status
        self.last_update_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + "Z"
        self.databaseModule.set_diagnostics_status(self.status, self.last_update_time)

    def get_status(self) -> str:
        self.load_diagnostics_status()
        return self.status

    def get_last_update_time(self) -> str:
        self.load_diagnostics_status()
        return self.last_update_time