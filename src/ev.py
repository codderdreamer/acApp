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
        self.__pid_locker_control = None

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
        self.parent_id = None
        self.check_and_clear_expired_reservation()

        self.start_stop_authorize = False
        self.__led_state = None
        Thread(target=self.control_error_list,daemon=True).start()
        Thread(target=self.send_message,daemon=True).start()

        self.charging_again = False

    def load_reservations(self):
        """
        Rezervasyonları yükler ve rezervasyon süresi dolmuş olanları siler.
        """
        reservation = self.application.databaseModule.get_current_reservation()
        if reservation:
            self.reservation_id = reservation.get('reservation_id')
            self.reservation_id_tag = reservation.get('id_tag')
            self.expiry_date = reservation.get('expiry_date')
            self.parent_id = reservation.get('parent_id')
            self.application.change_status_notification(ChargePointErrorCode.other_error, ChargePointStatus.reserved)

            
    def ocpp_offline(self):
        print(Color.Red.value, "Ocpp Offline")
        self.application.deviceState = DeviceState.OFFLINE
        self.application.change_status_notification(ChargePointErrorCode.other_error, ChargePointStatus.faulted,"Offline")

    def ocpp_online(self):
        if self.application.availability == AvailabilityType.operative:
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.available)
        else:
            self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.unavailable)

    def is_there_rcd_error(self):
        if PidErrorList.RcdTripError in self.application.serialPort.error_list:
            return True
        elif PidErrorList.RcdInitializeError in self.application.serialPort.error_list:
            return True
        else:
            return False
        
    def is_there_locker_initialize_error(self):
        if PidErrorList.LockerInitializeError in self.application.serialPort.error_list:
            return True
        else:
            return False
        
    def is_there_other_error(self):
        if len(self.application.serialPort.error_list) > 0:
            for value in self.application.serialPort.error_list:
                if value != PidErrorList.RcdTripError:
                    return True
        return False

    def is_reservation_expired(self):
        """
        Rezervasyonun süresinin dolup dolmadığını kontrol eder.
        """
        try:
            # Mikro saniyeli formatı kullanarak datetime nesnesine dönüştür
            expiry = datetime.strptime(self.expiry_date, '%Y-%m-%dT%H:%M:%S.%fZ')
            now = datetime.now()
            return now > expiry
        except ValueError:
            try:
                # Mikro saniyesiz formatı kullanarak datetime nesnesine dönüştür
                expiry = datetime.strptime(self.expiry_date, '%Y-%m-%dT%H:%M:%SZ')
                now = datetime.now()
                return now > expiry
            except ValueError as e:
                print(f"Error parsing expiry_date: {e}")
                return True

    def check_and_clear_expired_reservation(self):
        """
        Mevcut rezervasyonun süresinin dolup dolmadığını kontrol eder.
        Eğer süresi dolmuşsa, rezervasyonu temizler.
        """
        if self.reservation_id is not None:
            if self.is_reservation_expired():
                self.application.databaseModule.delete_reservation(self.reservation_id)
                self.reservation_id = None
                self.reservation_id_tag = None
                self.expiry_date = None
                self.parent_id = None
                # ChargePoint'i kullanılabilir hale getir
                self.application.change_status_notification(ChargePointErrorCode.noError,ChargePointStatus.available)
                # Set device state to IDLE
                self.application.deviceState = DeviceState.IDLE

                # Set LED state to StandBy
                self.application.led_state = LedState.StandBy


                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reservation expired and has been cleared.")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reservation is still valid.")

    def remote_start_thread(self):
        # Eğer kablo bağlı değilse
        # Waiting plug led yak
        # ConnectionTimeOut saniye içinde kablo bağlanmazsa idle
        connection_timeout = int(self.application.settings.configuration.ConnectionTimeOut)
        time_start = time.time()
        if self.application.ev.control_pilot != "B":
            print("self.application.ev.control_pilot", self.application.ev.control_pilot)
            while True:
                print(f"{connection_timeout} sn içinde kablo bağlantısı bekleniyor! control pilot:", self.application.ev.control_pilot)
                if self.application.ev.control_pilot == "B" or self.application.ev.control_pilot == "C":
                    print("Kablo bağlantısı sağlandı.")
                    break
                elif time.time() - time_start > connection_timeout:
                    print(f"Kablo bağlantısı sağlanamadı {connection_timeout} saniye süre doldu!")
                    if self.reservation_id:
                        self.application.change_status_notification(ChargePointErrorCode.other_error, ChargePointStatus.reserved)
                    else:
                        self.application.change_status_notification(ChargePointErrorCode.no_error, ChargePointStatus.available)
                        self.clean_charge_variables()
                    break
                time.sleep(0.2)

    def clean_charge_variables(self):
        try:
            # Eğer program ilk açılıyorsa ve billing cardda ise verileri temizleme, ocppye bağlanınca temizlencek
            if self.application.initilly and (self.application.cardType == CardType.BillingCard):
                return
            
            if (self.application.cardType == CardType.BillingCard) and self.application.ocppActive:
                if self.application.process.transaction_id != None:
                    print(Color.Yellow.value,"Stop transaction gönderiliyor...")
                    asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_stop_transaction(),self.application.loop)
                    if not self.application.initilly:
                        self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.finishing)
                self.application.meter_values_on = False
                time.sleep(3)
            print(Color.Yellow.value,"**************** şarj geçmişi siliniyor ...")
            self.application.ev.start_stop_authorize = False
            self.application.ev.card_id = ""
            self.application.ev.id_tag = None
            self.application.ev.charge = False
            if (self.application.cardType == CardType.BillingCard):
                self.application.chargePoint.authorize = None
            self.application.process.transaction_id = None
            self.application.process.id_tag = None
            self.application.process.initially_charge = False
            self.application.process.there_is_transaction = False
            self.application.databaseModule.set_charge("False", "", "")
        except Exception as e:
            print(Color.Red.value,"clean_charge_variables Exception:",e)

    def stop_pwm_off_relay(self):
        try:
            time_start = time.time()
            while True:
                print(Color.Yellow.value,"pwm 0 setleniyor...")
                self.application.serialPort.set_command_pid_cp_pwm(0)
                time.sleep(0.5)
                self.application.serialPort.get_command_pid_cp_pwm()
                time.sleep(0.5)
                if self.application.ev.pid_cp_pwm == 0:
                    print(Color.Green.value,"pwm 0 setlendi")
                    break
                if time.time() - time_start > 10:
                    print(Color.Red.value, "Pwm 0'a düşürülemedi! Pwm:",self.application.ev.pid_cp_pwm)
                    break
                time.sleep(1)
            if self.application.process.relay_control(Relay.Off):
                print(Color.Green.value,"Röle başarılı Off")
            else:
                print(Color.Red.value,"Röle Off başarısız.")
            if self.application.socketType == SocketType.Type2:
                self.application.process.unlock()
        except Exception as e:
            print("stop_pwm_off_relay Exception:",e)

    def control_error_list(self):
        time.sleep(15)
        time_start = time.time()
        while True:
            try:
                # Rezervasyon süresinin dolup dolmadığını kontrol et
                self.check_and_clear_expired_reservation()
                
                if (self.application.ocppActive == False) and (self.application.cardType == CardType.BillingCard) and (self.application.chargePointStatus != ChargePointStatus.charging) and (self.application.serialPort.error == False):
                    self.ocpp_offline()
                elif self.is_there_rcd_error():
                    self.application.process.rcd_trip_error = True
                    self.application.deviceState = DeviceState.FAULT
                    self.application.change_status_notification(ChargePointErrorCode.ground_failure,ChargePointStatus.faulted,"RcdTripError")
                    self.clean_charge_variables()
                elif self.is_there_locker_initialize_error():
                    self.application.process.locker_initialize_error = True
                    self.application.deviceState = DeviceState.FAULT
                    self.application.change_status_notification(ChargePointErrorCode.connector_lock_failure,ChargePointStatus.faulted,"LockerInitializeError")
                    self.clean_charge_variables()
                elif self.is_there_other_error():
                    if self.application.process.charge_try_counter > 3:
                        self.application.deviceState = DeviceState.FAULT
                    elif (self.control_pilot == ControlPlot.stateB.value) or (self.control_pilot == ControlPlot.stateC.value):
                        if self.application.process.charge_try_counter < 4:
                            self.application.deviceState = DeviceState.SUSPENDED_EVSE
                        else:
                            self.application.deviceState = DeviceState.FAULT
                    elif (self.control_pilot == ControlPlot.stateA.value):
                        self.application.deviceState = DeviceState.FAULT
                    else:
                        self.application.deviceState = DeviceState.FAULT
                elif self.application.deviceState == DeviceState.WAITING_AUTH and self.application.cardType == CardType.BillingCard and self.application.ocppActive == True:
                    self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.preparing)
                elif (self.control_pilot == ControlPlot.stateA.value) and (self.application.cardType == CardType.BillingCard) and (self.application.ocppActive == True) and (self.application.chargePointStatus != ChargePointStatus.preparing) and (self.application.chargePointStatus != ChargePointStatus.reserved) and (self.application.serialPort.error == False):
                    self.ocpp_online()
                elif (self.control_pilot == ControlPlot.stateA.value) and (self.application.cardType == CardType.LocalPnC or self.application.cardType == CardType.StartStopCard):
                    self.application.change_status_notification(ChargePointErrorCode.no_error,ChargePointStatus.available)
                if self.application.ocppActive:
                    if self.application.settings.configuration.MinimumStatusDuration:
                        if time.time() - time_start > int(self.application.settings.configuration.MinimumStatusDuration):
                            asyncio.run_coroutine_threadsafe(self.application.chargePoint.send_status_notification(connector_id=1,error_code=self.application.error_code,status=self.application.chargePointStatus,info=None),self.application.loop)
                            time_start = time.time()
                self.application.serialPort.error = False
            except Exception as e:
                print("******************************************** control_error_list Exception", e)
            time.sleep(1)

    def send_message(self):
        while True:
            if self.charge:
                try:
                    self.application.webSocketServer.websocketServer.send_message_to_all(msg=self.application.settings.get_charging())
                except Exception as e:
                    print("send_message Exception:", e)
                time.sleep(3)

    @property
    def pid_locker_control(self):
        return self.__pid_locker_control

    @pid_locker_control.setter
    def pid_locker_control(self, value):
        print(Color.Yellow.value,"MCU gelen response:",value)
        if self.__pid_locker_control != value:
            self.__pid_locker_control = value 
            

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
            if self.__control_pilot == ControlPlot.stateC.value and value == ControlPlot.stateB.value:
                self.application.control_C_B = True
            else:
                self.application.control_C_B = False
            if self.__control_pilot == ControlPlot.stateB.value and value == ControlPlot.stateC.value:
                self.application.control_A_B_C = True
            else:
                self.application.control_A_B_C = False
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
   
    def send_authorization_request(self, value):
        """
        Merkezi sisteme yetkilendirme talebi gönderir.
        """
        try:
            print("Yetkilendirme talebi gönderiliyor", value)
            # Merkezi sisteme yetkilendirme talebi gönder
            request = asyncio.run_coroutine_threadsafe(
                self.application.chargePoint.send_authorize(id_tag=value), 
                self.application.loop
            )
            response = request.result()  # Asenkron sonucu bekleyin

            # Merkezi sistem yanıtını kontrol et
            id_tag_info = response.id_tag_info
            status = id_tag_info['status']

            if status == AuthorizationStatus.accepted.value:
                # Yetkilendirme başarılıysa ve AuthorizationCacheEnabled True ise
                if self.application.settings.configuration.AuthorizationCacheEnabled.lower() == "true":
                    # Merkezi sistem yanıtından expiry_date ve parent_id bilgilerini al
                    expiry_date = id_tag_info.get('expiry_date')
                    parent_id = id_tag_info.get('parent_id')

                    # expiry_date sağlanmışsa, datetime nesnesine dönüştür
                    if expiry_date:
                        try:
                            # expire_date bir dize ise, datetime nesnesine dönüştür
                            if isinstance(expiry_date, str):
                                # Eğer Z harfi varsa UTC olduğunu belirtiyor, bu yüzden kaldırıyoruz
                                if expiry_date.endswith('Z'):
                                    expiry_date = expiry_date[:-1]
                                # Dizeyi datetime nesnesine dönüştür
                                print(f"expiry_date ayrıştırıldı: {expiry_date}")
                        except ValueError:
                            print(f"expiry_date ayrıştırılamadı: {expiry_date}, geçerli tarih + 1 yıl kullanılıyor.")
                            expiry_date = datetime.now() + timedelta(days=365)
                    else:
                        expiry_date = datetime.now() + timedelta(days=365)
                    
                    expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S.%f')
                    
                    self.application.databaseModule.update_auth_cache_tag(value, expiry_date, parent_id)

                print("Merkezi Sistem tarafından yetkilendirildi")
                return AuthorizationStatus.accepted
            else:
                print("Merkezi Sistem tarafından yetkilendirme geçersiz")
                # Yetkilendirme başarısızsa, invalid olarak geri dön
                return AuthorizationStatus.invalid

        except Exception as e:
            # Hata durumunda, hata mesajını logla ve invalid olarak geri dön
            print("Hata:", e)
            return AuthorizationStatus.invalid

    def check_online_authorization(self, value):
        """
        Cihaz online olduğunda yetkilendirme sürecini yönetir.
        Sırasıyla LocalPreAuthorize, Local Authorization List, Authorization Cache,
        ve merkezi sistem yetkilendirme taleplerini kontrol eder.
        """
        if self.reservation_id_tag:
            if self.reservation_id_tag == value:
                return AuthorizationStatus.accepted
            else:
                return AuthorizationStatus.invalid
        # LocalPreAuthorize bayrağını kontrol edin
        if self.application.settings.configuration.LocalPreAuthorize.lower() == "true":
            # Eğer LocalPreAuthorize True ise, LocalAuthListEnabled bayrağını kontrol edin
            print("LocalPreAuthorize is True")
            local_auth_result = self.check_local_auth_list(value)
            if local_auth_result == AuthorizationStatus.accepted:
                print("Authorized from LocalAuthList")
                return local_auth_result  
            
            # Eğer ocppTag localAuthList içinde bulunmazsa ve AuthorizationCacheEnabled True ise
            if self.application.settings.configuration.AuthorizationCacheEnabled.lower() == "true":
                print("AuthorizationCacheEnabled is True")
                cache_auth_result = self.check_authorization_cache(value)
                if cache_auth_result == AuthorizationStatus.accepted:
                    print("Authorized from AuthorizationCache")
                    return cache_auth_result  # Eğer ocppTag authorizationCache içinde bulunursa, Yetkilendirildi olarak geri dön.
            
            # Merkezi Sistem Yetkilendirme Talebi
            print("Sending authorization request to Central System 1")
            return self.send_authorization_request(value)
        
        else:
            print("LocalPreAuthorize is False")
            # Eğer LocalPreAuthorize False ise, doğrudan merkezi sisteme yetkilendirme talebi yapın.
            print("Sending authorization request to Central System 2")
            return self.send_authorization_request(value)
    

    def check_offline_authorization(self, value):
        """
        Cihaz offline durumda iken yetkilendirme kontrolü yapar.
        Sırasıyla LocalAuthorizeOffline, LocalAuthList, AuthorizationCache ve bilinmeyen kimlik 
        doğrulayıcılar için izin verilmesi kontrollerini gerçekleştirir.
        """
        if self.card_id == self.application.process.id_tag:
            print("Authorized for active card")
            return AuthorizationStatus.accepted
        
        # LocalAuthorizeOffline bayrağını kontrol edin
        if self.application.settings.configuration.LocalAuthorizeOffline.tolower() == "false":
            print("LocalAuthorizeOffline is False so Unauthorized")
            return AuthorizationStatus.invalid  # LocalAuthorizeOffline False ise, Red olarak geri dön.

        # LocalAuthList kontrolü
        local_auth_result = self.check_local_auth_list(value)
        if local_auth_result == AuthorizationStatus.accepted:
            print("Authorized from LocalAuthList")
            return local_auth_result  # LocalAuthList içinde bulunursa ve Accepted durumundaysa, Yetkilendirildi olarak geri dön.

        # Authorization Cache kontrolü
        if self.application.settings.configuration.AuthorizationCacheEnabled.lower() == "true":
            cache_auth_result = self.check_authorization_cache(value)
            if cache_auth_result == AuthorizationStatus.accepted:
                print("Authorized from AuthorizationCache")
                return cache_auth_result  # AuthorizationCache içinde bulunursa, Yetkilendirildi olarak geri dön.

        # Bilinmeyen Kimlik Doğrulayıcıların Yetkilendirilmesi
        if self.application.settings.configuration.AllowOfflineTxForUnknownId.lower() == "true":
            print("Authorized for unknown id")
            return AuthorizationStatus.accepted  # allowOfflineTxForUnknownId True ise, Bilinmeyen Kart, İzin Ver olarak geri dön.
        
        self.application.process.rfid_verified = False
        return AuthorizationStatus.invalid  # allowOfflineTxForUnknownId False ise, Red olarak geri dön.

    def check_local_auth_list(self, value):
        """
        Local Authorization List içinde verilen id_tag'i kontrol eder.
        AuthorizationStatus ve diğer bilgileri içeren idTagInfo yapısını döner.
        """
        if self.application.settings.configuration.LocalAuthListEnabled.lower() == "true":
            id_tag_info = self.application.databaseModule.get_card_status_from_local_list(value)

            status = id_tag_info.get('status')
            expiry_date = id_tag_info.get('expiry_date')

            # Expiry date kontrolü
            if expiry_date:
                try:
                    # Convert expiry_date to a datetime object if it's a string
                    expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    print(f"Failed to parse expiry_date: {expiry_date}, using current date + 1 year.")
                    expiry_date = datetime.now() + timedelta(days=365)
            else:
                expiry_date = datetime.now() + timedelta(days=365)

            if status == AuthorizationStatus.accepted.value:
                return AuthorizationStatus.accepted
            elif status == AuthorizationStatus.expired.value:
                print(f"Card {value} is expired.")
                return AuthorizationStatus.expired
            elif status == AuthorizationStatus.blocked.value:
                print(f"Card {value} is blocked.")
                return AuthorizationStatus.blocked
            elif status == AuthorizationStatus.invalid.value:
                print(f"Card {value} is invalid.")
                return AuthorizationStatus.invalid
            else:
                print(f"Unknown status for card {value}: {status}")

        return AuthorizationStatus.invalid

    def check_authorization_cache(self, value):
        """
        Authorization Cache içinde verilen id_tag'i kontrol eder.
        AuthorizationStatus ve diğer bilgileri içeren idTagInfo yapısını döner.
        """
        if self.application.settings.configuration.AuthorizationCacheEnabled.lower() == "true":

            id_tag_info = self.application.databaseModule.get_card_status_from_auth_cache(value)
            print("id_tag_info:", id_tag_info)
            if not id_tag_info:
                print(f"Card {value} is not in authorization cache.")
                return AuthorizationStatus.invalid
            status = id_tag_info.get('status')

            if status == AuthorizationStatus.accepted.value:
                print(f"Card {value} is accepted.")
                return AuthorizationStatus.accepted
            elif status == AuthorizationStatus.expired.value:
                print(f"Card {value} is expired.")
                return AuthorizationStatus.expired
            elif status == AuthorizationStatus.blocked.value:
                print(f"Card {value} is blocked.")
                return AuthorizationStatus.blocked
            elif status == AuthorizationStatus.invalid.value:
                print(f"Card {value} is invalid.")
                return AuthorizationStatus.invalid
            else:
                print(f"Unknown status for card {value}: {status}")

        return AuthorizationStatus.invalid
    
    def authorize_billing_card(self, value):
        """
        BillingCard tipi için yetkilendirme kontrolü yapar.
        Cihaz online olduğunda sırasıyla LocalPreAuthorize, LocalAuthList, AuthorizationCache,
        ve merkezi sistem yetkilendirme talebi kontrolleri yapılır.
        Cihaz offline olduğunda offline yetkilendirme süreçleri kontrol edilir.
        """
        authorization_result = None
        if self.application.ocppActive:  # Cihaz online ise
            print("Device is online")
            authorization_result =  self.check_online_authorization(value)
            print("Authorization Result:", authorization_result)
            if authorization_result == AuthorizationStatus.accepted:
                print("Authorized for billing card: ", value)
                self.application.process.id_tag = value
                self.application.chargePoint.authorize = AuthorizationStatus.accepted
                self.application.chargePoint.handle_authorization_accepted()
                self.start_stop_authorize = True
            else:
                self.application.chargePoint.handle_authorization_failed()
                print("Unauthorized for billing card: ", value)
                self.start_stop_authorize = False

        else:  # Cihaz offline ise
            print("Device is offline")
            authorization_result = self.check_offline_authorization(value)
            print("Authorization Result:", authorization_result)
            if authorization_result == AuthorizationStatus.accepted:
                self.authorize = AuthorizationStatus.accepted
                self.application.chargePoint.handle_authorization_accepted()
                print("Authorized for billing card: ", value)
                self.application.process.id_tag = value
                self.start_stop_authorize = True
            else:
                print("Unauthorized for billing card :", value)
                self.application.chargePoint.handle_authorization_failed()
                self.start_stop_authorize = False

        return authorization_result
        

    @property
    def card_id(self):
        return self.__card_id
    
    @card_id.setter
    def card_id(self, value):
        if (value != None) and (value != ""):
            if self.application.masterCard == value:
                print("Master card detected, resetting settings")
                os.system("rm -r /root/Settings.sqlite")
                os.system("cp /root/DefaultSettings.sqlite /root/Settings.sqlite")
                os.system("systemctl restart acapp.service")
            elif self.application.availability == AvailabilityType.inoperative:
                if self.charge:
                    if self.application.process.id_tag == value:
                        self.application.chargePoint.authorize = None
                        authorization_result = self.authorize_billing_card(value)
                        if authorization_result == AuthorizationStatus.accepted:
                            self.application.deviceState = DeviceState.STOPPED_BY_USER
                    else:
                        self.application.chargePoint.handle_authorization_failed()
                else:
                    self.application.process.rfid_verified = False
                    
            elif (self.application.cardType == CardType.BillingCard):
                print("Billing Card Detected :", value)
                
                if self.application.chargePoint is None:
                    print("Error: chargePoint is None. Cannot proceed with authorization.")
                    return  # Or handle the error as appropriate for your application

                if self.charge:
                    print("şarj aktif, transaction stopped")
                    if self.application.process.id_tag == value:
                        print("self.application.process.id_tag == value")
                        self.application.chargePoint.authorize = None
                        authorization_result = self.authorize_billing_card(value)
                        if authorization_result == AuthorizationStatus.accepted:
                            self.application.process.there_is_transaction = False
                            self.application.deviceState = DeviceState.STOPPED_BY_USER
                    else:
                        print("self.application.process.id_tag != value")
                        self.application.chargePoint.handle_authorization_failed()
                elif self.application.process.there_is_transaction:
                    print("transaction stopped")
                    if self.application.process.id_tag == value:
                        print("self.application.process.id_tag == value")
                        self.application.chargePoint.authorize = None
                        authorization_result = self.authorize_billing_card(value)
                        if authorization_result == AuthorizationStatus.accepted:
                            self.application.process.there_is_transaction = False
                            if self.control_pilot == ControlPlot.stateA.value:
                                self.application.deviceState = DeviceState.IDLE
                            else:
                                self.application.deviceState = DeviceState.STOPPED_BY_USER
                    else:
                        print("self.application.process.id_tag != value")
                        self.application.chargePoint.handle_authorization_failed()
                else:
                    print("transaction started")
                    self.application.chargePoint.authorize = None
                    authorization_result = self.authorize_billing_card(value)
                    if authorization_result == AuthorizationStatus.accepted:
                        self.application.process.there_is_transaction = True
                        self.application.process.id_tag = value
                        self.application.chargePoint.authorize = AuthorizationStatus.accepted
                        if self.control_pilot == ControlPlot.stateA.value:
                            Thread(target=self.remote_start_thread,daemon=True).start()
                    else :
                        self.application.chargePoint.authorize = None
                        print(Color.Red.value,"Autorize başarısız!")
                        
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
                            self.application.process.rfid_verified = True
                        elif self.charge == False:
                            self.application.process.rfid_verified = True
                            self.start_stop_authorize = True
                        else:
                            self.application.process.rfid_verified = False
                            self.start_stop_authorize = False
                        break
                if finded == False:
                    self.start_stop_authorize = False
                    self.application.process.rfid_verified = False
        
        self.__card_id = value

    @property
    def id_tag(self):
        return self.__id_tag

    @id_tag.setter
    def id_tag(self, value):
        self.__id_tag = value
