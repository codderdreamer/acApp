from src.enums import *
from threading import Thread
import time
import asyncio
from datetime import datetime, timedelta
from ocpp.v16.datatypes import *
from ocpp.v16.enums import *
import os
from src.logger import ac_app_logger as logger

class EV():
    def __init__(self, application):
        self.application = application

        self.__control_pilot = ControlPlot.stateA.value             # A,B,C,D,E, F
        self.__proximity_pilot = None           # ProximityPilot  : N, E, 1, 2, 3, 6
        self.__proximity_pilot_current = None

        self.pid_cp_pwm = None                  # float
        self.pid_relay_control = None
        self.pid_led_control = None
        self.pid_locker_control = None

        self.current_L1 = 0
        self.current_L2 = 0
        self.current_L3 = 0
        self.voltage_L1 = 0
        self.voltage_L2 = 0
        self.voltage_L3 = 0
        self.power = 0
        self.energy = 0

        self.temperature = None

        self.start_date = None

        self.__charge = False
        self.__card_id = None
        self.__id_tag = None

        self.reservation_id = None
        self.reservation_id_tag =  None
        self.expiry_date = None

        self.send_message_thread_start = False

        self.start_stop_authorize = False
        self.__led_state = None
        Thread(target=self.control_error_list,daemon=True).start()

        self.charging_again = False

    def ocpp_offline(self):
        print(Color.Red.value, "Ocpp Offline")
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.DeviceOffline,), daemon=True).start()
        self.application.change_status_notification(ChargePointErrorCode.other_error, ChargePointStatus.faulted)

    def ocpp_online(self):
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.StandBy,), daemon= True).start()
        if self.application.availability == AvailabilityType.operative:
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.available)
        else:
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.unavailable)

    def is_there_rcd_trip_error(self):
        if PidErrorList.RcdTripError in self.application.serialPort.error_list:
            return True
        else:
            return False
        
    def is_there_other_error(self):
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value != PidErrorList.RcdTripError:
                    return True
        return False

    def control_error_list(self):
        time.sleep(10)
        while True:
            try:
                if (self.application.ocppActive == False) and (self.application.cardType == CardType.BillingCard) and (self.application.chargePointStatus != ChargePointStatus.charging) and (self.application.serialPort.error == False):
                    self.ocpp_offline()
                elif (self.control_pilot == ControlPlot.stateA.value) and (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive == True) and (self.application.chargePointStatus != ChargePointStatus.preparing) and (self.application.serialPort.error == False):
                    self.ocpp_online()
                elif self.is_there_rcd_trip_error():
                    self.application.deviceState = DeviceState.FAULT
                elif self.is_there_other_error():
                    if self.application.process.charge_try_counter > 3:
                        self.application.deviceState = DeviceState.FAULT
                    elif (self.control_pilot == ControlPlot.stateB.value) or (self.control_pilot == ControlPlot.stateC.value):
                        self.application.deviceState = DeviceState.SUSPENDED_EVSE
                    elif (self.control_pilot == ControlPlot.stateA.value):
                        self.application.deviceState = DeviceState.FAULT
                    else:
                        self.application.deviceState = DeviceState.FAULT
                self.application.serialPort.error = False
            except Exception as e:
                print("******************************************** control_error_list Exception",e)
            time.sleep(1)


    def send_message(self):
        self.send_message_thread_start = True
        while self.send_message_thread_start:
            try:
                self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_charging())
            except Exception as e:
                print("send_message Exception:", e)
            time.sleep(3)

    @property
    def led_state(self):
        return self.__led_state

    @led_state.setter
    def led_state(self, value):
        if self.__led_state != value:
            self.__led_state = value 
            print(Color.Yellow.value,value)

    @property
    def proximity_pilot_current(self):
        return self.__proximity_pilot_current

    @proximity_pilot_current.setter
    def proximity_pilot_current(self, value):
        if self.__proximity_pilot_current != value:
            self.__proximity_pilot_current = value
            print(Color.Yellow.value,"Proximity Pilot Current:",value)

    @property
    def proximity_pilot(self):
        return self.__proximity_pilot

    @proximity_pilot.setter
    def proximity_pilot(self, value):
        self.__proximity_pilot = value
        if self.__proximity_pilot == ProximityPilot.CableNotPlugged.value:
            self.proximity_pilot_current = 0
        elif self.__proximity_pilot == ProximityPilot.Error.value:
            self.proximity_pilot_current = 0
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger13Amper.value:
            self.proximity_pilot_current = 13
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger20Amper.value:
            self.proximity_pilot_current = 20
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger32Amper.value:
            self.proximity_pilot_current = 32
        elif self.__proximity_pilot == ProximityPilot.CablePluggedIntoCharger63Amper.value:
            self.proximity_pilot_current = 63

    @property
    def control_pilot(self):
        return self.__control_pilot

    @control_pilot.setter
    def control_pilot(self, value):
        if self.__control_pilot != value:
            self.__control_pilot = value
            print(Color.Yellow.value,"Control Pilot",value)
            if self.__control_pilot == ControlPlot.stateA.value:
                self.application.deviceState = DeviceState.IDLE
            elif self.__control_pilot == ControlPlot.stateB.value and self.application.deviceState != DeviceState.SUSPENDED_EVSE:
                self.application.deviceState = DeviceState.CONNECTED
            elif self.__control_pilot == ControlPlot.stateC.value:
                self.application.deviceState = DeviceState.CHARGING
            elif (self.__control_pilot == ControlPlot.stateD.value) or (self.__control_pilot == ControlPlot.stateE.value) or (self.__control_pilot == ControlPlot.stateF.value):
                self.application.deviceState = DeviceState.FAULT

    @property
    def charge(self):
        return self.__charge

    @charge.setter
    def charge(self, value):
        if self.__charge != value:
            print(Color.Yellow.value,"Charge:",value)
        self.__charge = value
        if value:
            Thread(target=self.send_message,daemon=True).start()
        else:
            self.send_message_thread_start = False
            self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_charging())

    def update_authorization_cache(self, ocpp_tag, expire_date):
        """
        Authorization Cache veritabanına yetkilendirilmiş tag'i kaydeder.
        Eğer tag zaten mevcutsa, expire_date ve updated_at alanlarını günceller.
        """
        try:
            # Önce, tag'in veritabanında mevcut olup olmadığını kontrol edin
            existing_tag = self.application.databaseModule.get_card_status_from_auth_cache(ocpp_tag)

            if existing_tag == AuthorizationStatus.expired.value:
                # Mevcut ise, expire_date ve updated_at alanlarını güncelle
                self.application.databaseModule.update_auth_cache_tag(ocpp_tag, expire_date)
                print(f"Authorization cache for {ocpp_tag} updated with new expiration date {expire_date}.")
            elif existing_tag is None:
                # Mevcut değilse, yeni kayıt ekle
                self.application.databaseModule.add_auth_cache_tag(ocpp_tag, expire_date)
                print(f"Authorization cache for {ocpp_tag} added with expiration date {expire_date}.")
            else:
                print(f"Authorization cache for {ocpp_tag} is in {existing_tag} status and will not be updated.")

        except Exception as e:
            print(f"Error updating authorization cache for {ocpp_tag}: {e}")

    def send_authorization_request(self, value):
        """
        Merkezi sisteme yetkilendirme talebi gönderir.
        """
        try:
            # Yetkilendirme talebini merkezi sisteme gönder
            request = asyncio.run_coroutine_threadsafe(
                self.application.chargePoint.send_authorize(id_tag=value), 
                self.application.loop
            )
            response = request.result()  # Asenkron sonucu bekleyin

            # Yetkilendirme talebinin yanıtını kontrol et
            id_tag_info = response.id_tag_info
            status = id_tag_info['status']

            if status == AuthorizationStatus.accepted.value:
                # Yetkilendirme başarılı ise ve AuthorizationCacheEnabled True ise
                if self.application.settings.configuration.AuthorizationCacheEnabled == "true":
                    # Merkezi sistemden gelen expire_date bilgisi
                    expiry_date = id_tag_info.get('expiry_date')
                    
                    # Eğer expiry_date merkezi sistemden gelmezse, bugünden itibaren 1 yıl sonrasını baz alarak ayarla
                    if not expiry_date:
                        expiry_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
                    
                    # authorizationCache veritabanına bu tag'i kaydet
                    self.update_authorization_cache(value, expiry_date)
                
                print("Authorized")
                return AuthorizationStatus.accepted
            else:
                # Yetkilendirme başarısız ise, Rejected olarak geri dön
                return AuthorizationStatus.rejected

        except Exception as e:
            # Hata durumunda, hata mesajını logla ve Rejected olarak geri dön
            print("Error:", e)
            return AuthorizationStatus.rejected
        
    def check_online_authorization(self, value):
        """
        Cihaz online olduğunda yetkilendirme sürecini yönetir.
        Sırasıyla LocalPreAuthorize, Local Authorization List, Authorization Cache,
        ve merkezi sistem yetkilendirme taleplerini kontrol eder.
        """
        # LocalPreAuthorize bayrağını kontrol edin
        if self.application.settings.configuration.LocalPreAuthorize == "true":
            # Eğer LocalPreAuthorize True ise, LocalAuthListEnabled bayrağını kontrol edin
            local_auth_result = self.check_local_auth_list(value)
            if local_auth_result == AuthorizationStatus.accepted:
                return local_auth_result  
            
            # Eğer ocppTag localAuthList içinde bulunmazsa ve AuthorizationCacheEnabled True ise
            if self.application.settings.configuration.AuthorizationCacheEnabled == "true":
                cache_auth_result = self.check_authorization_cache(value)
                if cache_auth_result == AuthorizationStatus.accepted:
                    return cache_auth_result  # Eğer ocppTag authorizationCache içinde bulunursa, Yetkilendirildi olarak geri dön.
            
        else:
            # Eğer LocalPreAuthorize False ise, doğrudan merkezi sisteme yetkilendirme talebi yapın.
            return self.send_authorization_request(value)

        # Merkezi Sistem Yetkilendirme Talebi
        return self.send_authorization_request(value)

    def check_offline_authorization(self, value):
        """
        Cihaz offline durumda iken yetkilendirme kontrolü yapar.
        Sırasıyla LocalAuthorizeOffline, LocalAuthList, AuthorizationCache ve bilinmeyen kimlik 
        doğrulayıcılar için izin verilmesi kontrollerini gerçekleştirir.
        """
        # LocalAuthorizeOffline bayrağını kontrol edin
        if self.application.settings.configuration.LocalAuthorizeOffline == "false":
            return AuthorizationStatus.rejected  # LocalAuthorizeOffline False ise, Red olarak geri dön.

        # LocalAuthList kontrolü
        local_auth_result = self.check_local_auth_list(value)
        if local_auth_result == AuthorizationStatus.accepted:
            return local_auth_result  # LocalAuthList içinde bulunursa ve Accepted durumundaysa, Yetkilendirildi olarak geri dön.

        # Authorization Cache kontrolü
        if self.application.settings.configuration.AuthorizationCacheEnabled == "true":
            cache_auth_result = self.check_authorization_cache(value)
            if cache_auth_result == AuthorizationStatus.accepted:
                return cache_auth_result  # AuthorizationCache içinde bulunursa, Yetkilendirildi olarak geri dön.

        # Bilinmeyen Kimlik Doğrulayıcıların Yetkilendirilmesi
        if self.application.settings.configuration.allowOfflineTxForUnknownId == "true":
            return AuthorizationStatus.accepted  # allowOfflineTxForUnknownId True ise, Bilinmeyen Kart, İzin Ver olarak geri dön.
        
        Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon=True).start()
        return AuthorizationStatus.rejected  # allowOfflineTxForUnknownId False ise, Red olarak geri dön.

    def check_local_auth_list(self, value):
        """
        Local Authorization List içinde verilen id_tag'i kontrol eder.
        Accepted durumunda "Authorized", diğer durumlarda None döner.
        """
        if self.application.settings.configuration.LocalAuthListEnabled == "true":
            card_status = self.application.databaseModule.get_card_status_from_local_list(value)
            if card_status == AuthorizationStatus.accepted.value:
                return AuthorizationStatus.accepted
            elif card_status == AuthorizationStatus.expired.value:
                print(f"Card {value} is expired.")
            elif card_status == AuthorizationStatus.blocked.value:
                print(f"Card {value} is blocked.")
            elif card_status == AuthorizationStatus.invalid.value:
                print(f"Card {value} is invalid.")
        return None

    def check_authorization_cache(self, value):
        """
        Authorization Cache içinde verilen id_tag'i kontrol eder.
        Accepted durumunda "Authorized", diğer durumlarda None döner.
        """
        cache_status = self.application.databaseModule.get_card_status_from_auth_cache(value)
        if cache_status == AuthorizationStatus.accepted.value:
            return AuthorizationStatus.accepted
        return None

    def authorize_billing_card(self, value):
        """
        BillingCard tipi için yetkilendirme kontrolü yapar.
        Cihaz online olduğunda sırasıyla LocalPreAuthorize, LocalAuthList, AuthorizationCache,
        ve merkezi sistem yetkilendirme talebi kontrolleri yapılır.
        Cihaz offline olduğunda offline yetkilendirme süreçleri kontrol edilir.
        """
        print("Billing Card Detected :", value)
        if self.application.ocppActive:  # Cihaz online ise
            print("Device is online")
            authorization_result =  self.check_online_authorization(value)
            print("Authorization Result:", authorization_result)
            if authorization_result == AuthorizationStatus.accepted:
                print("Authorized for billing card: ", value)
                self.start_stop_authorize = True
            else:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon=True).start()
                print("Unauthorized for billing card: ", value)
                self.start_stop_authorize = False

        else:  # Cihaz offline ise
            authorization_result = self.check_offline_authorization(value)
            print("Authorization Result:", authorization_result)
            if authorization_result == AuthorizationStatus.accepted:
                print("Authorized for billing card: ", value)
                self.start_stop_authorize = True
            else:
                print("Unauthorized for billing card :", value)
                self.start_stop_authorize = False
        

    @property
    def card_id(self):
        return self.__card_id
    
    @card_id.setter
    def card_id(self, value):
        if (self.__card_id != value) and (value != None) and (value != ""):
            print(Color.Yellow.value,"Card Id:",value)
        if (value != None) and (value != ""):
            if self.application.masterCard == value:
                print("Master card detected, resetting settings")
                os.system("rm -r /root/Settings.sqlite")
                os.system("cp /root/DefaultSettings.sqlite /root/Settings.sqlite")
                os.system("systemctl restart acapp.service")
            elif self.application.availability == AvailabilityType.inoperative:
                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
            elif (self.application.cardType == CardType.BillingCard):
                if self.charge:
                    if self.application.process.id_tag == value:
                        self.application.chargePoint.authorize = None
                        asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_authorize(id_tag=value), self.application.loop)
                else:
                    self.application.chargePoint.authorize = None
                    authorization_result = self.authorize_billing_card(value)
                    if authorization_result == "Authorized":
                        self.application.chargePoint.authorize = AuthorizationStatus.accepted
                        
            elif self.application.cardType == CardType.StartStopCard:
                print("Start Stop Card Detected :", value)
                finded = False
                card_id_list = self.application.databaseModule.get_default_local_list()
                for id in card_id_list:
                    if value == id:
                        if self.application.deviceState == DeviceState.STOPPED_BY_EVSE or self.application.deviceState == DeviceState.STOPPED_BY_USER or self.application.deviceState == DeviceState.FAULT:
                            self.start_stop_authorize = False
                        else:
                            self.start_stop_authorize = True
                        finded = True

                        if self.charge and (self.application.process.id_tag == value):
                            self.application.deviceState = DeviceState.STOPPED_BY_USER
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidVerified,), daemon= True).start()
                        elif self.charge == False:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidVerified,), daemon= True).start()
                            if self.__control_pilot != "B":
                                Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.WaitingPluging,), daemon=True).start()
                        else:
                            Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
                        break
                if finded == False:
                    self.start_stop_authorize = False
                    Thread(target=self.application.serialPort.set_command_pid_led_control, args=(LedState.RfidFailed,), daemon= True).start()
        
        self.__card_id = value

    @property
    def id_tag(self):
        return self.__id_tag

    @id_tag.setter
    def id_tag(self, value):
        self.__id_tag = value
