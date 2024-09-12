import os
import shutil
import subprocess
import logging
import requests
import time
import threading
import fcntl
import sqlite3
import serial
import threading
import requests
import stat 
from logging.handlers import RotatingFileHandler
from enum import Enum

INSTALL_STATUS_FILE_PATH = "/root/install_status.log"
GIT_REPO_URL = "git@github.com:codderdreamer/acApp.git"
ROOT_DIR = "/root"
BACKUP_FW_DIR = "/root/ChargePackAC_Firmware_v1.0.fwenc"
ACAPP_DIR = "/root/acApp"
ACAPP_OLD_DIR = "/root/acApp_old"
ACAPP_NEW_DIR = "/root/acApp_new"
SERIAL_PORT_PATH = "/dev/ttyS2"
OCPP_FIRMWARE_DIR = "/root/acAppFirmwareFiles"


class LedState(Enum):
    FirmwareUpdate = ">"

class InstallContext(Enum):
    """
    Kurulum veya geri yükleme işlemlerinin genel durumunu ve bilgilerini içeren sınıf.
    """
    GIT_INSTALL = "Git Install"
    OCPP_INSTALL = "OCPP Install"
    RESTORE_INSTALL = "Restore Install"
    
class InstallStatus(Enum):
    """
    Kurulum veya geri yükleme işlemlerinin genel durumunu belirten enum sınıfı.
    """
    SUCCESS = "Success"
    START_OPERATION = "Start Operation"
    SERVICE_START_FAILED = "Service Start Failed"
    SERVICE_STOP_FAILED = "Service Stop Failed"
    UPDATE_DATABASE_STARTED = "Move Database Started"
    UPDATE_DATABASE_FAILED = "Move Database Failed"
    EXTRACT_FW_FAILED = "Extract Fw Failed"
    FINAL_OPERATION_STARTED = "Final Operation Started"
    FINAL_OPERATION_FAILED = "Final Operation Failed"
    FINAL_OPERATION_SUCCESS = "Final Operation Success"
    RESTORE_ROOTPATHS_FAILED = "Restore Rootpaths Failed"
    RESTORE_REPO_FAILED = "Restore Repo Failed"
    RESTORE_MCU_FAILED = "Restore MCU Failed"
    
# Logger yapılandırması
def setup_logger(log_file="/root/update_manager.log", log_level=logging.INFO):
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    log_handler = RotatingFileHandler(log_file, maxBytes=1 * 1024 * 1024, backupCount=0)
    log_handler.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(log_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

class LedManager:
    def __init__(self, serial_port_path, baud_rate=115200):
        """
        LedManager sınıfı, LED durumlarını günceller ve thread'i başlatıp durdurur.
        :param serial_port_path: Seri port yolu.
        :param baud_rate: Seri port hızı, varsayılan 115200.
        """
        self.serial = serial.Serial(serial_port_path, baud_rate, timeout=1)
        self.stx = b'\x02'
        self.lf = b'\n'
        self.set_command = 'S'
        self.pid_led_control = "L"
        self.led_state = LedState.FirmwareUpdate
        self.thread = None
        self.running = False  # Thread'in çalışıp çalışmadığını kontrol eden bayrak

    def calculate_checksum(self, data):
        checksum = int.from_bytes(self.stx, "big")
        for i in data:
            checksum += ord(i)
        checksum = checksum % 256
        checksum = str(checksum)
        return checksum.zfill(3)

    def set_led_state(self, led_state):
        """
        LED durumunu günceller ve seri port üzerinden gönderir.
        :param led_state: Yeni LED durumu (LedState)
        """
        try:
            parameter_data = "002"
            connector_id = "1"
            data = self.set_command + self.pid_led_control + parameter_data + connector_id + led_state.value
            checksum = self.calculate_checksum(data)
            send_data = self.stx + data.encode('utf-8') + checksum.encode('utf-8') + self.lf

            # Seri port üzerinden gönder
            self.serial.write(send_data)
        except Exception as e:
            print(f"LED durumu güncellenirken hata oluştu: {e}")

    def led_thread_function(self):
        """
        LED durumunu düzenli aralıklarla güncelleyen thread fonksiyonu.
        """
        while self.running:
            self.set_led_state(self.led_state)
            time.sleep(2)  # Her 10 saniyede bir LED durumu gönderiliyor

    def start_led_thread(self):
        """
        LED güncellemeleri için thread'i başlatır.
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.led_thread_function)
            self.thread.start()
            print("LED güncelleme thread'i başlatıldı.")

    def stop_led_thread(self):
        """
        LED güncellemeleri için thread'i durdurur.
        """
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join()
                print("LED güncelleme thread'i durduruldu.")

class ChargeManager:
    def __init__(self, db_path="/root/Charge.sqlite"):
        """
        ChargeManager sınıfı, şarj durumunu kontrol eden işlemleri yönetir.

        Args:
            db_path (str): Şarj durumunun saklandığı veritabanı yolu (default: "/root/Charge.sqlite").
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.f = None

    def connect(self):
        """
        Veritabanına bağlanır ve gerekli kilitleme işlemlerini yapar.
        
        Returns:
            bool: Eğer bağlantı başarılı olursa True, aksi takdirde False döner.
        """
        try:
            self.f = open(self.db_path, 'a+')
            fcntl.flock(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            logger.error(f"SQLite bağlantı hatası: {e}")
            return False
        except IOError as e:
            logger.error("Dosya kilitli, tekrar deneniyor...")
            time.sleep(1)
            return self.connect()
        except Exception as e:
            logger.error(f"Veritabanı bağlantısı sırasında hata: {e}")
            return False

    def disconnect(self):
        """
        Veritabanı bağlantısını ve dosya kilidini kapatır.
        """
        try:
            if self.conn:
                self.conn.close()
            if self.f:
                self.f.close()
        except sqlite3.Error as e:
            logger.error(f"Veritabanı bağlantısını kapatma hatası: {e}")
        except Exception as e:
            logger.error(f"Bağlantı sonlandırma sırasında hata: {e}")

    def is_there_charge(self, retry_attempts=3, retry_delay=1):
        """
        Veritabanındaki 'charge' durumunu kontrol eder.

        Args:
            retry_attempts (int): Bağlantı hatası durumunda kaç kere tekrar deneneceğini belirtir.
            retry_delay (int): Tekrar denemeler arasında bekleme süresi (saniye cinsinden).

        Returns:
            bool: Eğer 'charge' değeri 'True' ise True, aksi takdirde False döner.
        """
        attempt = 0
        data_dict = {}

        # Eğer veritabanı dosyası yoksa False döner
        if not os.path.exists(self.db_path):
            logger.error(f"Veritabanı dosyası bulunamadı: {self.db_path}")
            return False

        while attempt < retry_attempts:
            try:
                # Veritabanına bağlanma ve kilitleme işlemi
                if self.connect():
                    query = "SELECT * FROM ev"
                    self.cursor.execute(query)
                    data = self.cursor.fetchall()

                    # Gelen verileri sözlüğe aktar
                    for row in data:
                        data_dict[row[0]] = row[1]

                    # Veritabanı bağlantısını kapat
                    self.disconnect()

                    # 'charge' değeri kontrol edilir
                    return data_dict.get("charge", "False") == "True"
                else:
                    logger.error("Veritabanına bağlanılamadı.")
                    return False

            except sqlite3.OperationalError as e:
                logger.error(f"SQLite operasyon hatası: {e}")
                attempt += 1
                time.sleep(retry_delay)
                continue

            except sqlite3.Error as e:
                logger.error(f"SQLite hatası: {e}")
                break  # Bu tür hatalarda tekrar denemeye gerek yok

            except IOError as e:
                logger.error("Dosya kilitli. Tekrar deneniyor...")
                attempt += 1
                time.sleep(retry_delay)
                continue

            except Exception as e:
                logger.error(f"Beklenmeyen bir hata oluştu: {e}")
                break  # Beklenmeyen bir hata, sonsuz döngüye girmemek için durdur

        logger.error("Tüm denemeler başarısız oldu, işlem sonlandırıldı.")
        return False
   
class ServiceManager:
    """
    Servis durdurma, başlatma ve durum kontrolü işlemleri
    """
    @staticmethod
    def stop_service(service_name="acapp.service"):
        logger.debug(f"{service_name} servisi durduruluyor...")
        result = subprocess.run(['systemctl', 'stop', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            logger.debug(f"{service_name} servisi başarıyla durduruldu.")
            return True
        else:
            logger.error(f"{service_name} servisi durdurulamadı: {result.stderr}")
            return False

    @staticmethod
    def start_service(service_name="acapp.service"):
        subprocess.run(['systemctl', 'start', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        led_manager.stop_led_thread()
        logger.info(f"{service_name} servisi başlatıldı. Kontroller için 25 saniye bekleniyor...")
        if ServiceManager.is_service_active(service_name):
            # PID izleme sadece başlangıçtan sonra
            pid_not_changed = ServiceManager.monitor_service_pid(service_name)
            
            if pid_not_changed:
                return  True  # Başarılı
            else:
                logger.debug(f"{service_name} servisi başlatıldı ancak PID değişti! Sorun olabilir.")
                
                # LED durumunu güncelle
                led_manager.stop_led_thread()
                return False
        else:
            logger.debug(f"{service_name} servisi başlatılamadı!")
            led_manager.stop_led_thread()
            return False
    
    @staticmethod
    def is_service_active(service_name="acapp.service"):
        """
        Servisin aktif olup olmadığını ve PID durumunu kontrol eder.
        
        Args:
            service_name (str): Kontrol edilecek servis adı.
        
        Returns:
            bool: Eğer servis aktifse True, değilse False döner.
        """
        result = subprocess.run(['systemctl', 'is-active', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.stdout.strip() == "active":
            pid_info = ServiceManager.get_service_pid(service_name)
            if pid_info:
                logger.info(f"{service_name} servisi PID bilgisi: {pid_info}")
                return True
            else:
                logger.error(f"{service_name} servisi aktif ancak PID alınamadı!")
                return False
        else:
            logger.error(f"{service_name} servisi aktif değil.")
            return False

    @staticmethod
    def get_service_pid(service_name="acapp.service"):
        """
        Servisin PID bilgisini döner.
        
        Args:
            service_name (str): Kontrol edilecek servis adı.

        Returns:
            str: Servis PID bilgisi, None eğer PID alınamazsa.
        """
        try:
            result = subprocess.run(['systemctl', 'status', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout
            if result:
                for line in result.splitlines():
                    if "Main PID" in line:
                        return line.split()[2]  # PID'yi al
            return None
        except Exception as e:
            logger.error(f"{service_name} servisi için PID bilgisi alınamadı: {e}")
            return None

    @staticmethod
    def monitor_service_pid(service_name="acapp.service", wait_time=60, retry_attempts=3):
        """
        Servisin PID bilgisini izler. Eğer PID 1 dakika boyunca değişmezse uyarı verir.
        
        Args:
            service_name (str): İzlenecek servis adı.
            wait_time (int): PID değişikliği için bekleme süresi (saniye cinsinden, default: 60 saniye / 1 dakika).
            retry_attempts (int): PID alınamadığında kaç kere tekrar deneneceği (default: 3 deneme).
            
        Returns:
            bool: Eğer PID değişmemişse True, değişmişse False döner.
        """
        attempt = 0
        initial_pid = None

        # PID almayı 3 kez deneme
        while attempt < retry_attempts:
            initial_pid = ServiceManager.get_service_pid(service_name)
            if initial_pid:
                break  # PID alınabildiyse döngüden çık
            attempt += 1
            time.sleep(5)  # 5 saniye bekle ve tekrar dene

        if not initial_pid:
            logger.error(f"{service_name} servisi için PID 3 denemeden sonra alınamadı, izleme iptal edildi.")
            return False  # PID alınamadıysa False döndür

        time.sleep(wait_time)  # 1 dakika bekle
        current_pid = ServiceManager.get_service_pid(service_name)
        
        if current_pid == initial_pid:
            return True   # PID değişmediyse True döner
        else:
            logger.warning(f"{service_name} servisi PID değişti: {initial_pid} -> {current_pid}. Sorun olabilir.")
            return False   # PID değiştiyse False döner

class NetworkManager:
    """
    İnternet bağlantısını kontrol etmek için sınıf
    """
    @staticmethod
    def is_internet_available(url="http://www.google.com"):
        """
        İnternet bağlantısını kontrol eder.

        Args:
            url (str): Test edilecek URL. Varsayılan olarak Google.

        Returns:
            bool: Bağlantı başarılıysa True, aksi takdirde False döner.
        """
        try:
            response = requests.get(url, timeout=5)  # Timeout değeri 5 saniye
            if response.status_code == 200:
                return True
        except (requests.ConnectionError, requests.Timeout):
            logger.error("İnternet bağlantısı yok veya yanıt süresi doldu.")
            return False
        
        # Eğer yanıt kodu 200 değilse de False döner
        return False

class GitManager:
    def __init__(self):
        self.current_branch = None

    def set_current_branch(self):
        """
        Mevcut branch'i öğrenir ve current_branch değişkenine kaydeder.
        """
        try:
            # Git repo dizinine geç
            os.chdir(ACAPP_DIR)

            # Geçerli branch'i öğren
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if result.returncode == 0:
                self.current_branch = result.stdout.strip()
                logger.debug(f"Geçerli branch: {self.current_branch}")
            else:
                logger.debug(f"Branch öğrenilemedi: {result.stderr}")
        except Exception as e:
            logger.error(f"Branch bilgisi alınırken hata oluştu: {e}")

        # ROOT_DIR'e geri dön
        os.chdir(ROOT_DIR)

    def clean_update_directories(self):
        """
        acApp_old ve acApp_new dizinlerini kaldırır eğer mevcutlarsa.
        """
        try:
            if os.path.exists(ACAPP_OLD_DIR):
                shutil.rmtree(ACAPP_OLD_DIR)
                logger.info(f"{ACAPP_OLD_DIR} başarıyla kaldırıldı.")

            if os.path.exists(ACAPP_NEW_DIR):
                shutil.rmtree(ACAPP_NEW_DIR)
                logger.info(f"{ACAPP_NEW_DIR} başarıyla kaldırıldı.")
        except Exception as e:
            logger.error(f"Eski dizinler kaldırılırken hata oluştu: {e}")

    def backup_acapp_directory(self):
        """
        acApp dizinini acApp_old olarak yedekler.
        """
        try:
            if os.path.exists(ACAPP_DIR):
                logger.debug(f"{ACAPP_DIR} dizini {ACAPP_OLD_DIR} olarak yedekleniyor...")
                
                # Eğer hedef dizin varsa, önce eski yedeği sil
                if os.path.exists(ACAPP_OLD_DIR):
                    if os.path.isdir(ACAPP_OLD_DIR):
                        shutil.rmtree(ACAPP_OLD_DIR)
                    else:
                        os.remove(ACAPP_OLD_DIR)
                    logger.debug(f"Eski {ACAPP_OLD_DIR} silindi.")
                
                # Dizini kopyala
                shutil.copytree(ACAPP_DIR, ACAPP_OLD_DIR)
                logger.info(f"{ACAPP_DIR} başarıyla {ACAPP_OLD_DIR} olarak yedeklendi.")
                self.root_paths_backup()
            else:
                logger.error(f"{ACAPP_DIR} dizini bulunamadı, yedekleme yapılmadı.")
        except Exception as e:
            logger.error(f"acApp dizini yedeklenirken hata oluştu: {e}")

    def root_paths_backup(self):
        # acapp_old_dir+rootpaths dizinini kontrol et ve içersindeki dosya isimlerini al
        # Root dizinindeki bu dosya isimleri ile aynı olan dosyaları acapp_old_dir+rootpaths dizinine taşı
        try:
            if os.path.exists(ACAPP_OLD_DIR):
                rootpaths_dir = os.path.join(ACAPP_OLD_DIR, "rootpaths")
                if os.path.exists(rootpaths_dir):
                    logger.debug(f"{rootpaths_dir} dizini kontrol ediliyor...")
                    for filename in os.listdir(rootpaths_dir):
                        if os.path.isfile(os.path.join(ROOT_DIR, filename)):
                            shutil.copy2(os.path.join(ROOT_DIR, filename), os.path.join(rootpaths_dir, filename))
                            logger.debug(f"{filename} dosyası {rootpaths_dir} dizinine başarıyla taşındı.")
                        else:
                            logger.debug(f"{filename} dosyası {ROOT_DIR} dizininde bulunamadı.")
                else:
                    logger.error(f"{rootpaths_dir} dizini bulunamadı.")
            else:
                logger.error(f"{ACAPP_OLD_DIR} dizini bulunamadı.")

        except Exception as e:
            logger.error(f"rootpaths_backup hatası: {e}")
            
    def check_for_git_changes(self):
        """
        Mevcut branch'teki git değişikliklerini kontrol eder ve aynı branch'e geçer.
        """
        try:
            # Branch'i güncelle
            self.set_current_branch()

            if not self.current_branch:
                logger.error("Branch bilgisi alınamadı, değişiklik kontrolü yapılmadı.")
                return False

            # acApp dizinine geç
            os.chdir(ACAPP_DIR)

            # Fetch yap
            subprocess.run(['git', 'fetch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            # Mevcut branch'teki güncellemeleri kontrol et
            changes = subprocess.run(
                ['git', 'log', f'HEAD..origin/{self.current_branch}', '--oneline'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            if changes.stdout.strip():  # Eğer bir değişiklik varsa
                logger.info(f"Git'te {self.current_branch} branch'inde yeni değişiklikler mevcut:\n{changes.stdout.strip()}")
                os.chdir(ROOT_DIR)
                return True
            else:
                logger.info(f"{self.current_branch} branch'i güncel, değişiklik yok.")
                os.chdir(ROOT_DIR)
                return False
        except Exception as e:
            logger.error(f"Git değişiklik kontrolü sırasında hata oluştu: {e}")
            os.chdir(ROOT_DIR)
            return False

    def clone_new_repo(self):
        """
        Git'ten yeni repoyu acApp_new dizinine klonlar ve ilgili branch'e geçer.
        """
        try:
            logger.debug(f"Git reposu {GIT_REPO_URL} klonlanıyor...")

            # ROOT_DIR'e geç
            os.chdir(ROOT_DIR)

            # Eğer acApp_new dizini varsa, kaldır
            if os.path.exists(ACAPP_NEW_DIR):
                shutil.rmtree(ACAPP_NEW_DIR)
                logger.debug(f"{ACAPP_NEW_DIR} dizini başarıyla kaldırıldı.")

            # Repo'yu klonla
            result = subprocess.run(['git', 'clone', GIT_REPO_URL, ACAPP_NEW_DIR], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            if result.returncode == 0:
                logger.info(f"Git reposu başarıyla {ACAPP_NEW_DIR} dizinine klonlandı.")

                # Yeni klonlanan repo dizinine geç
                os.chdir(ACAPP_NEW_DIR)

                # Set branch to current_branch
                if self.current_branch:
                    checkout_result = subprocess.run(['git', 'checkout', self.current_branch], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    if checkout_result.returncode == 0:
                        logger.info(f"{self.current_branch} branch'ine geçildi.")
                    else:
                        logger.error(f"{self.current_branch} branch'ine geçilemedi: {checkout_result.stderr}")
                else:
                    logger.error("Geçerli branch bilgisi mevcut değil, branch geçişi yapılamadı.")
            else:
                logger.error(f"Git klonlama başarısız oldu: {result.stderr}")

        except Exception as e:
            logger.error(f"Git klonlama sırasında hata oluştu: {e}")
        finally:
            # İşlem sonrasında ROOT_DIR'e geri dön
            os.chdir(ROOT_DIR)

    def clean_old_directory(self):
        """
        Eski repoyu temizler.
        """
        try:
            if os.path.exists(ACAPP_OLD_DIR):
                shutil.rmtree(ACAPP_OLD_DIR)
                logger.info(f"{ACAPP_OLD_DIR} dizini başarıyla temizlendi.")
            else:
                logger.info(f"{ACAPP_OLD_DIR} dizini bulunamadı, temizleme yapılmadı.")
        except Exception as e:
            logger.error(f"Eski dizin temizlenirken hata oluştu: {e}")

class MCUManager:
    """
    MCU güncellemeleri için yardımcı sınıf.
    """
    def __init__(self, led_manager):
        self.led_manager = led_manager

    def set_gpio(self, port, pin, value):
        try:
            command = f"gpio-test.64 w {port} {pin} {value}"
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"GPIO ayarlanırken hata: {e}")

    def pe_10_set(self):
        try:
            self.set_gpio('e', 10, 1)
            self.set_gpio('e', 11, 1)
            time.sleep(0.3)
            self.set_gpio('e', 10, 0)
        except Exception as e:
            logger.error(f"pe_10_set hatası: {e}")

    def pe_11_set(self):
        try:
            time.sleep(0.5)
            self.set_gpio('e', 11, 0)
            time.sleep(0.1)
            self.set_gpio('e', 11, 1)
            time.sleep(0.1)

            self.set_gpio('e', 11, 0)
            time.sleep(0.1)
            self.set_gpio('e', 11, 1)
            time.sleep(0.1)

            self.set_gpio('e', 11, 0)
            time.sleep(0.1)
            self.set_gpio('e', 11, 1)
            time.sleep(0.1)

            self.set_gpio('e', 11, 0)
            time.sleep(0.1)
            self.set_gpio('e', 11, 1)
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"pe_11_set hatası: {e}")

    def update_mcu_firmware(self, firmware_path):
        """
        MCU'nun firmware'ini günceller.
        """
        try:
            led_manager.stop_led_thread()
            logger.info("MCU boot moduna geçiyor...")
            # GPIO ayarları için ayrı thread'ler başlat
            threading.Thread(target=self.pe_10_set, daemon=True).start()
            threading.Thread(target=self.pe_10_set, daemon=True).start()

            logger.debug(f"Firmware yolu: {firmware_path}")

            # MCU güncellemesi için 10 saniye bekle
            time.sleep(10)

            logger.info("MCU güncelleniyor...")

            # Firmware yükleme komutu
            command = ['dfu-util', '-a', '0', '-s', '0x08020000:leave', '-D', firmware_path]
            log_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            log_output = log_result.stdout
            logger.debug(f"Firmware update log: {log_output}")

            # GPIO reset işlemi
            time.sleep(0.1)
            self.set_gpio('e', 10, 0)
            self.set_gpio('e', 11, 0)
            time.sleep(0.1)
            self.set_gpio('e', 10, 1)
            time.sleep(0.5)
            self.set_gpio('e', 10, 0)

            led_manager.start_led_thread()

            # Yükleme başarılı mı kontrol et
            if "File downloaded successfully" in log_output:
                logger.info("MCU Firmware başarıyla yüklendi.")
                return True
            else:
                logger.error("Firmware yüklenirken bir hata oluştu.")
                return False

        except Exception as e:
            logger.error(f"update_mcu_firmware hatası: {e}")
            return False
    
    def retry_mcu_update(self, firmware_path, count):
        """
        MCU firmware güncellemesi başarısız olduğunda tekrar dener.
        """
        for attempt in range(0, count):  # 3 deneme yap
            logger.info(f"MCU firmware güncelleme deneme: {attempt + 1}")
            if self.update_mcu_firmware(firmware_path):
                return True
            time.sleep(60)
        logger.error("MCU güncellemesi başarısız oldu.")
        return False

    def is_firmware_different(self, old_firmware_path, new_firmware_path):
        """
        Eski ve yeni firmware dosyalarını hem isim hem boyut açısından karşılaştırır.
        Eğer eski dosya yoksa güncelleme yapılması gerektiğini belirtir.
        """

        # Dosya adı karşılaştırma
        old_firmware_name = os.path.basename(old_firmware_path)
        new_firmware_name = os.path.basename(new_firmware_path)

        if old_firmware_name != new_firmware_name:
            logger.info(f"Firmware dosya isimleri farklı: {old_firmware_name}, {new_firmware_name}")
            return True  # İsimler farklıysa güncelleme yapılmalı

        # Dosya boyutlarını karşılaştırma
        old_size = os.path.getsize(old_firmware_path)
        new_size = os.path.getsize(new_firmware_path)

        if old_size != new_size:
            logger.info(f"Firmware dosya boyutları farklı: {old_size}, {new_size}")
            return True  # Boyutlar farklıysa güncelleme yapılmalı

        return False

    def get_firmware_file(self, firmware_dir):
        """
        Firmware dosyasını `mcufirmware` dizininden alır.
        """
        try:
            firmware_files = os.listdir(firmware_dir)
            if len(firmware_files) == 1:
                return firmware_files[0]  # Tek dosya varsa döndür
            else:
                logger.error(f"Firmware dizininde birden fazla dosya veya hiç dosya bulunamadı: {firmware_files}")
                return None
        except Exception as e:
            logger.error(f"Firmware dosyasını alırken hata oluştu: {e}")
            return None
        
    def compare_and_update_firmware(self, old_firmware_dir, new_firmware_dir):
        """
        Firmware dosyalarını karşılaştırır ve gerekirse güncellemeyi gerçekleştirir.
        
        Args:
            old_firmware_dir: Eski firmware dizini.
            new_firmware_dir: Yeni firmware dizini.
        
        Returns:
            bool: Güncelleme başarılı olduysa True, olmadıysa False.
        """
        # Yeni firmware dosyasını al
        firmware_file_old = self.get_firmware_file(old_firmware_dir)
        firmware_file_new = self.get_firmware_file(new_firmware_dir)

        if firmware_file_old and firmware_file_new:
            logger.debug(f"Eski ve yeni firmware dosyaları bulundu: {firmware_file_old}, {firmware_file_new}")
            old_firmware_path = os.path.join(old_firmware_dir, firmware_file_old)
            new_firmware_path = os.path.join(new_firmware_dir, firmware_file_new)

            # Firmware dosyaları farklıysa güncelle
            if self.is_firmware_different(old_firmware_path, new_firmware_path):
                logger.info(f"Firmware dosyası farklı: {new_firmware_path}. Güncelleme yapılıyor...")
                if self.retry_mcu_update(new_firmware_path, 3):
                    return True   # Güncelleme başarılı
                else:
                    if self.retry_mcu_update(old_firmware_path, 3):
                        return False
            else:
                logger.info("Firmware dosyaları aynı, güncelleme yapılmadı.")
                return True  # Güncellemeye gerek yok
        
        return False
        
class FileManager:
    """Dosya kopyalama ve yönetim işlemleri için sınıf."""

    def __init__(self, database_manager):
        """
        FileManager sınıfının başlatıcısı. Kopyalama ve taşıma işlemleri için gerekli dizinler ayarlanır.
        
        Args:
            database_manager: Veritabanı dosyalarının taşınması sırasında kullanılacak DatabaseManager örneği.
            new_repo_path: Yeni repodaki rootpaths dizinini belirtir.
        """
        self.database_manager = database_manager
        self.target_dir = None  # Yeni repodaki rootpaths dizini
        self.python_command = "python3"  # Python komutunu burada ayarlıyoruz


    def validate_directory(self, dir_path):
        """
        Verilen dizinin varlığını ve erişilebilirliğini doğrular.
        
        Args:
            dir_path (str): Kontrol edilecek dizin yolu.
        
        Returns:
            bool: Eğer dizin mevcutsa ve erişilebilir durumdaysa True, değilse False döner.
        """
        if not os.path.exists(dir_path):
            logger.error(f"Kaynak dizin mevcut değil: {dir_path}")
            return False
        if not os.access(dir_path, os.R_OK):
            logger.error(f"Kaynak dizine erişim izni yok: {dir_path}")
            return False
        return True

    def update_database_files_in_new_repo(self, new_repo_path):
        """Eski root dizinindeki db dosyalarını yeni repodaki rootpaths dizinine göre günceller."""
        try:
            if not os.path.exists(new_repo_path):
                logger.error(f"Yeni repo dizini mevcut değil: {new_repo_path}")
                return False
            
            self.target_dir = os.path.join(new_repo_path, "rootpaths")  # Yeni repodaki rootpaths dizini
        
            # Kaynak dizin doğrulaması
            validation_status = self.validate_directory(ROOT_DIR)
            if not validation_status:
                return False
            
            validation_status = self.validate_directory(self.target_dir)
            if not validation_status:
                return False

            # Veritabanı dosyalarını taşıma işlemi
            for filename in os.listdir(ROOT_DIR):
                if filename.endswith((".sqlite", ".db")):
                    source_path = os.path.join(ROOT_DIR, filename)
                    target_path = os.path.join(self.target_dir, filename)

                    # Set the sync script path
                    self.database_manager.set_sync_script_path(os.path.join(self.target_dir, "sync_database.py"))
                    # Veritabanı taşıma işlemi database_manager kullanılarak yapılır.
                    self.database_manager.update_old_databases(source_path, target_path)
                    logger.debug(f"{source_path} dosyası {target_path} dizinine başarıyla taşındı.")
            
            return True
                
        except FileNotFoundError as fnf_error:
            logger.error(f"Dosya taşıma hatası: {fnf_error}")
            return False
        except PermissionError as perm_error:
            logger.error(f"Erişim hatası: {perm_error}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen bir hata oluştu: {e}")
            return False

    def copy_rootpaths_files_to_root(self):
        """
        rootpaths dizinindeki dosyaları root dizinine kopyalar.
        """
        try:
            rootpaths_dir = os.path.join(ACAPP_NEW_DIR, "rootpaths")
            for filename in os.listdir(rootpaths_dir):
                # update.py dosyasını hariç tut
                if filename == "update.py":
                    continue
                source_path = os.path.join(rootpaths_dir, filename)
                target_path = os.path.join(ROOT_DIR, filename)
                shutil.copy2(source_path, target_path)
            return True
        except FileNotFoundError as fnf_error:
            logger.error(f"Dosya kopyalama hatası: {fnf_error}")
            return False
        except PermissionError as perm_error:
            logger.error(f"Erişim hatası: {perm_error}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen bir hata oluştu: {e}")
            return False
        
class DatabaseManager:
    def __init__(self):
        """
        DatabaseManager sınıfının başlatıcısı.
        """
        # Veritabanı bağlantıları
        self.old_conn = None
        self.new_conn = None

        # Python script path ve python komutu
        self.sync_script_path = "./new_repo/rootpaths/sync_script.py"  # Çalıştırılacak Python betiğinin yolu
        self.python_command = "python3"  # Python komutunu burada ayarlıyoruz

        # Diğer genel değişkenler
        self.table_versions_query = "SELECT version FROM database_version LIMIT 1"  # İlk version sorgusu

        self.old_db_path = None
        self.new_db_path = None

    def set_db_paths(self, old_db_path, new_db_path):
        """
        Eski ve yeni veritabanı dosyalarının yollarını ayarlar.
        """
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path

    def set_sync_script_path(self, sync_script_path):
        """
        Python betiğinin yolunu ayarlar.
        """
        self.sync_script_path = sync_script_path

    def connect(self):
        """
        Eski ve yeni veritabanına bağlanır. Eğer bağlantı sağlanamazsa uygun bir hata mesajı verir.
        """
        if not os.path.exists(self.old_db_path):
            logger.error(f"Eski veritabanı dosyası mevcut değil: {self.old_db_path}")
            return False

        if not os.path.exists(self.new_db_path):
            logger.error(f"Yeni veritabanı dosyası mevcut değil: {self.new_db_path}")
            return False

        try:
            self.old_conn = sqlite3.connect(self.old_db_path)
            logger.debug(f"Eski veritabanına ({self.old_db_path}) başarıyla bağlanıldı.")
        except sqlite3.Error as e:
            logger.error(f"Eski veritabanına bağlanılamadı: {e}")
            return False

        try:
            self.new_conn = sqlite3.connect(self.new_db_path)
            logger.debug(f"Yeni veritabanına ({self.new_db_path}) başarıyla bağlanıldı.")
        except sqlite3.Error as e:
            logger.error(f"Yeni veritabanına bağlanılamadı: {e}")
            if self.old_conn:
                self.old_conn.close()
            return False

        return True

    def disconnect(self):
        """
        Eski ve yeni veritabanı bağlantılarını kapatır.
        """
        try:
            if self.old_conn:
                self.old_conn.close()
            if self.new_conn:
                self.new_conn.close()
            logger.debug("Veritabanı bağlantıları başarıyla kapatıldı.")
        except sqlite3.Error as e:
            logger.error(f"Veritabanı bağlantılarını kapatma hatası: {e}")

    def compare_database_versions(self):
        """
        Eski ve yeni veritabanındaki 'database_version' tablosundaki 'version' değerini karşılaştırır.
        """
        try:
            old_version = self.old_conn.execute(self.table_versions_query).fetchone()[0]
            new_version = self.new_conn.execute(self.table_versions_query).fetchone()[0]

            logger.debug(f"Eski veritabanı version: {old_version}, Yeni veritabanı version: {new_version}")

            if old_version == new_version:
                # self.copy_all_tables()  # Eşleşme varsa tüm tabloları kopyala
                self.copy_database_file_to_new_directory()  # Veritabanı dosyasını yeni dizine kopyala
            else:
                logger.warning(f"Veritabanı versiyonları uyuşmuyor! Eski: {old_version}, Yeni: {new_version}")
                self.run_sync_script()  # Versiyonlar uyuşmadığında betiği çalıştır

        except sqlite3.Error as e:
            logger.error(f"Veritabanı versiyon karşılaştırma hatası: {e}")

    def run_sync_script(self):
        """
        new_repo'daki rootpaths klasöründeki Python betiğini çalıştırır.
        """
        try:
            logger.info(f"Python betiği çalıştırılıyor: {self.sync_script_path}")
            subprocess.run([self.python_command, self.sync_script_path], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Python betiği çalıştırılırken hata oluştu: {e}")

 
    def copy_database_file_to_new_directory(self):
        """
        Eski veritabanını yeni veritabanına kopyalar.
        """
        try:
            shutil.copy2(self.old_db_path, self.new_db_path)
            logger.info("Veritabanı dosyası başarıyla kopyalandı.")
        except FileNotFoundError as fnf_error:
            logger.error(f"Veritabanı dosyası kopyalanırken hata: {fnf_error}")
        except PermissionError as perm_error:
            logger.error(f"Veritabanı dosyası kopyalanırken hata: {perm_error}")
        except Exception as e:
            logger.error(f"Veritabanı dosyası kopyalanırken beklenmeyen bir hata oluştu: {e}")


    def update_old_databases(self, old_db_path, new_db_path):
        """
        Veritabanı yollarını alarak, bağlanma, karşılaştırma ve bağlantıyı kesme işlemlerini gerçekleştirir.
        """
        self.set_db_paths(old_db_path, new_db_path)
        
        if self.connect():
            self.compare_database_versions()  # Versiyonları kıyasla
            self.disconnect()
        else:
            logger.error("Veritabanı bağlantısı başarısız oldu.")

class OcppUpdateManager:
    def __init__(self, fw_file_dir):
        self.fw_file_dir = fw_file_dir  # Fw dosyasının olduğu dizin
        self.fw_file_path = None  # Fw dosyasının yolu

    def find_firmware_file(self):
        """
        Fw dosyasını fw_file_dir içinde bulur. Sadece bir fw dosyasının olacağı varsayılır.
        """
        # Dizin mevcut değilse oluştur
        if not os.path.exists(self.fw_file_dir):
            logging.info(f"{self.fw_file_dir} dizini mevcut değil, oluşturuluyor.")
            os.makedirs(self.fw_file_dir)

        fw_files = [file for file in os.listdir(self.fw_file_dir) if file.endswith(".fwenc")]

        if len(fw_files) == 1:
            self.fw_file_path = os.path.join(self.fw_file_dir, fw_files[0])
            logging.debug(f"Fw dosyası bulundu: {self.fw_file_path}")
            return True
        elif len(fw_files) > 1:
            logging.debug("Birden fazla fw dosyası bulundu.")
            return False
        else:
            return False

    def extract_firmware_files(self, fw_file_path):
        if not fw_file_path:
            return False
        
        try:        
            # Eğer hedef dizin mevcutsa, önce onu sil
            if os.path.exists(ACAPP_NEW_DIR):
                logging.debug(f"{ACAPP_NEW_DIR} dizini mevcut, siliniyor...")
                shutil.rmtree(ACAPP_NEW_DIR)

            
            # fwenc dosyasını çıkar
            result = subprocess.run(['unarchive_secure', fw_file_path, ACAPP_NEW_DIR], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if result.returncode == 0:
                logging.info(f"{fw_file_path} dosyası {ACAPP_NEW_DIR} dizinine çıkarıldı.")
                return True
            else:
                logging.error(f"Fw dosyası çıkarılırken hata oluştu: {result.stderr}")
                return False
        except Exception as e:
            logging.error(f"Beklenmeyen bir hata oluştu: {e}")

    def clean_firmware_file(self):
        """
        Fw dosyasını temizler.
        """
        if not self.fw_file_path:
            return True
        
        try:
            os.remove(self.fw_file_path)
            logging.info(f"{self.fw_file_path} dosyası temizlendi.")
            return True
        except FileNotFoundError as e:
            return True
        except Exception as e:
            logging.error(f"Beklenmeyen bir hata oluştu: {e}")
            return False
          
class UpdateFailWaitManager:
    """
    Hata yönetimini sağlayan sınıf. Son hata zamanını takip eder ve belirli bir süre dolana kadar yeni denemelere izin vermez.
    """
    def __init__(self, wait_hours=24, wait_minutes=0):
        """
        :param wait_hours: Bekleme süresi saat cinsinden (varsayılan 24 saat).
        :param wait_minutes: Bekleme süresi dakika cinsinden (varsayılan 0 dakika).
        """
        self.error_wait_time = (wait_hours * 3600) + (wait_minutes * 60)  # Bekleme süresini saniyeye çevirir
        self.last_error_time = None  # Son hata zamanı

    def install_failed(self):
        """
        Bir hata kaydeder ve son hata zamanını günceller.
        """
        self.last_error_time = time.time()
        logger.error("Hata kaydedildi. Bekleme süresi başlamış olabilir.")

    def should_retry(self):
        """
        Yeniden denemenin gerekip gerekmediğini kontrol eder.
        :return: True (yeniden denemeye izin ver), False (beklenmeli)
        """
        if self.last_error_time is None:
            return True  # Hiç hata kaydedilmediyse denemeye izin ver
        
        elapsed_time = time.time() - self.last_error_time
        if elapsed_time >= self.error_wait_time:
            logger.info("Bekleme süresi doldu, tekrar denemeye izin veriliyor.")
            self.reset_error()
            return True
        
        remaining_time = self.error_wait_time - elapsed_time
        hours, remainder = divmod(remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        logger.warning(f"Bir önceki güncelleme başarısız olduğu için, {int(hours)} saat {int(minutes)} dakika {int(seconds)} saniye sonra tekrar denenecek.")
        return False

    def reset_error(self):
        """
        Hata zamanını sıfırlar.
        """
        self.last_error_time = None

class RestoreManager:
    """
    acApp_old dizininden projeyi ve kök dizindeki dosyaları geri yükler.
    """
    def __init__(self, old_project_dir, project_dir, led_manager, mcu_manager):
        """
        :param old_project_dir: Eski proje dizini (örneğin: acApp_old dizini).
        :param project_dir: Mevcut proje dizini (örneğin: acApp dizini).
        :param led_manager: LED işlemlerini yöneten sınıf.
        """
        self.old_project_dir = old_project_dir
        self.project_dir = project_dir
        self.led_manager = led_manager
        self.mcu_manager = mcu_manager

    def restore_project(self):
        """
        Eski proje dizinini (acApp_old) mevcut proje dizinine (acApp) geri yükler.
        """
        try:
            # Eski proje dizini kontrolü
            if not os.path.exists(self.old_project_dir):
                logging.error(f"Eski proje dizini bulunamadı: {self.old_project_dir}")
                return False

            # Mevcut proje dizinini sil ve yedekten geri yükle
            if os.path.exists(self.project_dir):
                shutil.rmtree(self.project_dir)
                logging.debug(f"Mevcut proje dizini silindi: {self.project_dir}")

            shutil.copytree(self.old_project_dir, self.project_dir)
            logging.info(f"Proje dizini eski sürümden geri yüklendi: {self.project_dir}")
            return True
        except Exception as e:
            logging.error(f"Proje geri yüklenirken hata oluştu: {e}")
            return False

    def set_executable_permission(self, file_path):
        """
        Dosyaya yürütme izni ekler.
        :param file_path: İzin eklenecek dosyanın yolu.
        """
        try:
            # Yürütme izni ekle
            os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IEXEC)
            logging.info(f"Yürütme izni verildi: {file_path}")
        except Exception as e:
            logging.error(f"{file_path} dosyasına yürütme izni eklenirken hata oluştu: {e}")

    def restore_root_files(self):
        """
        acApp_old dizinindeki kök dizin dosyalarını mevcut kök dizine (root) geri yükler.
        Kopyalanacak dosyaların boyutunu kontrol eder; boyut 0 ise kopyalama yapılmaz.
        """
        try:
            old_rootpaths_dir = os.path.join(self.old_project_dir, "rootpaths")
            if not os.path.exists(old_rootpaths_dir):
                logging.error(f"Eski sürümde 'rootpaths' dizini bulunamadı: {old_rootpaths_dir}")
                return False
            
            # Kök dizin dosyalarını güncelle
            for item in os.listdir(old_rootpaths_dir):
                
                if item in ["external_run.py", "sync_database.py", "update.py"]:
                    continue

                source = os.path.join(old_rootpaths_dir, item)
                destination = os.path.join(ROOT_DIR, item)

                # Dosya boyutunu kontrol et
                if os.path.isfile(source) and os.path.getsize(source) == 0:
                    logging.error(f"{source} dosyasının boyutu 0 bayt, kopyalama yapılmadı.")
                    continue

                # Hedefteki eski dosyaları/dizinleri kaldır
                if os.path.exists(destination):
                    if os.path.isdir(destination):
                        shutil.rmtree(destination)
                    else:
                        os.remove(destination)

                # Eski dosyaları/dizinleri geri yükle
                if os.path.isdir(source):
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
                    # Kopyalanan dosyaya yürütme izni ekle
                    self.set_executable_permission(destination)

                logging.info(f"{source} dosyası root dizine geri yüklendi: {destination}")
            return True
        except Exception as e:
            logging.error(f"Kök dizin dosyaları geri yüklenirken hata oluştu: {e}")
            return False
   
    def restore_previous_version(self):
        """
        Eski sürümü geri yükler, LED işlemlerini başlatır/durdurur ve servisi yeniden başlatır.

        :param mcu_manager: MCU güncellemelerini yöneten sınıf.
        :return: InstallStatus: İşlemin sonucunu belirten enum değeri.
        """
        # Stop service
        if not ServiceManager.stop_service():
            logging.error("Servis durdurulamadı.")
            ErrorManager.save_install_status(InstallStatus.SERVICE_STOP_FAILED, InstallContext.RESTORE_INSTALL)
            return False
        
    
        # Eski projeyi ve kök dosyalarını geri yükle
        if not self.restore_project():
            logging.error("Proje geri yüklenemedi.")
            self.led_manager.stop_led_thread()
            ErrorManager.save_install_status(InstallStatus.RESTORE_REPO_FAILED, InstallContext.RESTORE_INSTALL)
            return False
        
        # Start operation
        ErrorManager.save_install_status(InstallStatus.START_OPERATION, InstallContext.RESTORE_INSTALL)
        # LED güncellemeleri için thread'i başlat
        self.led_manager.start_led_thread()

        if not self.restore_root_files():
            logging.error("Kök dizin dosyaları geri yüklenemedi.")
            self.led_manager.stop_led_thread()
            ErrorManager.save_install_status(InstallStatus.RESTORE_ROOTPATHS_FAILED, InstallContext.RESTORE_INSTALL)
            return False

        # MCU Firmware güncelleme kontrolü
        old_firmware_dir = os.path.join(self.old_project_dir, "mcufirmware")
        firmware_file_old = os.path.join(old_firmware_dir, self.mcu_manager.get_firmware_file(old_firmware_dir))

        # Eski firmware dosyasını yükleyip güncelleme kontrolü yap
        if self.mcu_manager.retry_mcu_update(firmware_file_old, 3):
            logging.info("Eski firmware dosyası yüklendi ve güncelleme kontrolü yapıldı.")
        else:
            logging.error("Eski firmware dosyası yüklenemedi.")
            self.led_manager.stop_led_thread()
            ErrorManager.save_install_status(InstallStatus.RESTORE_MCU_FAILED, InstallContext.RESTORE_INSTALL)
            return False

        self.led_manager.stop_led_thread()
        # Servisi tekrar başlatma
        if ServiceManager.start_service():
            logging.info("Eski sürüm başarıyla başlatıldı ve sorunsuz çalışıyor.")
            ErrorManager.save_install_status(InstallStatus.SUCCESS, InstallContext.RESTORE_INSTALL)
            return True
        else:
            logging.error("Servis başlatılamadı ya da PID değişti, potansiyel repo sorunları olabilir.")
            self.led_manager.stop_led_thread()
            ErrorManager.save_install_status(InstallStatus.SERVICE_START_FAILED, InstallContext.RESTORE_INSTALL)
            return False
            
class FinalOperationsManager:
    """def save_install_status(status, context):
    Son işlemleri yöneten sınıf. Dış betiği çalıştırır, root dizinini günceller ve repoyu taşır.
    """
    def __init__(self, file_manager, git_manager, mcu_manager):
        """
        :param file_manager: Dosya yönetimini sağlayan sınıf.
        :param git_manager: Git işlemlerini yöneten sınıf.
        """
        self.file_manager = file_manager
        self.git_manager = git_manager
        self.mcu_manager = mcu_manager
        self.python_command = "python3"

    def validate_directory(self, dir_path):
        """
        Verilen dizinin varlığını ve erişilebilirliğini doğrular.
        
        Args:
            dir_path (str): Kontrol edilecek dizin yolu.
        
        Returns:
            bool: Eğer dizin mevcutsa ve erişilebilir durumdaysa True, değilse False döner.
        """
        if not os.path.exists(dir_path):
            return False
        if not os.access(dir_path, os.R_OK):
            return False
        return True

    def run_external_script(self, script_path):
        """
        Harici bir Python betiğini çalıştırır.
        
        Args:
            script_path (str): Çalıştırılacak Python betiğinin yolu.
        
        Returns:
            InstallStatus: İşlemin sonucunu belirten enum değeri.
        """
        try:
            result = subprocess.run([self.python_command, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if result.returncode == 0:
                logger.debug(f"Betik başarıyla çalıştırıldı: {script_path}")
                return True
            else:
                logger.error(f"Betik çalıştırma hatası: {script_path}\n{result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Betik çalıştırma sırasında hata: {script_path}\n{e}")
            return False

    def final_copy_for_repo(self, real_repo_path, new_repo_path):
        """
        Yeni repoyu real_repo_path dizinine taşıma işlemi.
        
        Args:
            real_repo_path (str): Mevcut repo yolu.
            new_repo_path (str): Yeni repo yolu.
        
        Returns:
            InstallStatus: İşlemin sonucunu belirten enum değeri.
        """
        try:
            # Kaynak dizin doğrulaması
            validation_status = self.validate_directory(real_repo_path)
            if not validation_status:
                return False
            
            validation_status = self.validate_directory(new_repo_path)
            if not validation_status:
                return False
            
            # Eski repoyu sil ve yeni repoyu taşı
            shutil.rmtree(real_repo_path)
            if os.path.isdir(new_repo_path):
                shutil.copytree(new_repo_path, real_repo_path)
            else:
                shutil.copy2(new_repo_path, real_repo_path)
            logger.debug(f"{new_repo_path} klasörü {real_repo_path} klasörüne başarıyla taşındı.")
            
            return True
        
        except FileNotFoundError as fnf_error:
            logger.error(f"Dosya taşıma hatası: {fnf_error}")
            return False
        except PermissionError as perm_error:
            logger.error(f"Erişim hatası: {perm_error}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen bir hata oluştu: {e}")
            return False

    def final_copy_to_root_dir(self, new_repo_path):
        """
        Yeni repodaki rootpaths dizinini mevcut kök dizine kopyalar.
        
        Args:
            new_repo_path (str): Yeni repo yolu.
        
        Returns:
            InstallStatus: İşlemin sonucunu belirten enum değeri.
        """
        try:
            if not os.path.exists(new_repo_path):
                logger.error(f"Yeni repo dizini mevcut değil: {new_repo_path}")
                return False
            
            target_dir = os.path.join(new_repo_path, "rootpaths")  # Yeni repodaki rootpaths dizini

            # Kaynak dizin doğrulaması
            validation_status = self.validate_directory(ROOT_DIR)
            if not validation_status:
                return False
            
            validation_status = self.validate_directory(target_dir)
            if not validation_status:
                return False

            # Veritabanları ve update.py hariç güncelleme işlemi
            for filename in os.listdir(target_dir):
                # filename external_run.py ve sync_database.py dosyalarını taşıma işlemi dışında bırakır
                if filename.endswith(("external_run.py", "sync_database.py", "update.py")):
                    continue
                    
                if not filename.endswith((".sqlite", ".db")):
                    source_path = os.path.join(target_dir, filename)
                    target_path = os.path.join(ROOT_DIR, filename)

                    shutil.copy2(source_path, target_path)
          
            return True
        
        except FileNotFoundError as fnf_error:
            logger.error(f"Dosya taşıma hatası: {fnf_error}")
            return False
        except PermissionError as perm_error:
            logger.error(f"Erişim hatası: {perm_error}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen bir hata oluştu: {e}")
            return False

    def perform_final_operations(self, context):
        """
        Tüm son işlemleri gerçekleştirir.
        :return: InstallStatus: Eğer tüm işlemler başarıyla tamamlandıysa SUCCESS, aksi halde ilgili hata durumu döner.
        """
        # Son işlemler başlamadan önce bir log kaydı oluştur
        ErrorManager.save_install_status(InstallStatus.FINAL_OPERATION_STARTED, context)

        # MCU Firmware güncelleme kontrolü
        old_firmware_dir = os.path.join(ACAPP_OLD_DIR, "mcufirmware")
        new_firmware_dir = os.path.join(ACAPP_NEW_DIR, "mcufirmware")


        if not mcu_manager.compare_and_update_firmware(old_firmware_dir, new_firmware_dir):
            logger.error("MCU Firmware güncelleme başarısız oldu.")
            ErrorManager.save_install_status(InstallStatus.FINAL_OPERATION_FAILED, context)
            return False

        script_path = os.path.join(ACAPP_NEW_DIR, "rootpaths", "external_run.py")
        
        status = self.run_external_script(script_path)
        if status:
            logger.info("Harici betik başarıyla çalıştırıldı.")
        else:
            logger.error("Harici betik çalıştırma hatası.")
            ErrorManager.save_install_status(InstallStatus.FINAL_OPERATION_FAILED, context)
            return False

        status = self.final_copy_to_root_dir(ACAPP_NEW_DIR)
        if status:
            logger.info("rootpaths dizini başarıyla kök dizine kopyalandı.")
        else:
            logger.error("rootpaths dizini kök dizine kopyalanamadı.")
            ErrorManager.save_install_status(InstallStatus.FINAL_OPERATION_FAILED, context)
            return False
        
        status = self.final_copy_for_repo(ACAPP_DIR, ACAPP_NEW_DIR)

        if status:
            logger.info("Yeni repo başarıyla taşındı.")
        else:
            logger.error("Yeni repo taşınamadı.")
            ErrorManager.save_install_status(InstallStatus.FINAL_OPERATION_FAILED, context)
            return False
        
        logger.info("Tüm son işlemler başarıyla tamamlandı.")

        return True

class ErrorManager:
    """
    İşlemlerin durumunu kaydeden, okuyan ve hata yönetimini sağlayan sınıf.
    """

    def __init__(self, restore_manager, final_operations_manager, mcu_manager, update_fail_wait_manager, git_manager, ocpp_update_manager):
        self.restore_manager = restore_manager
        self.final_operations_manager = final_operations_manager
        self.mcu_manager = mcu_manager
        self.update_fail_wait_manager = update_fail_wait_manager
        self.git_manager = git_manager
        self.ocpp_update_manager = ocpp_update_manager
        restore_retry_count = 0
    
    @staticmethod
    def save_install_status(status, context):
        """
        InstallStatus değerini bir dosyaya kaydeder. Her yeni kayıt geldiğinde önceki kayıtları siler.

        Args:
            status (InstallStatus): İşlemin sonucunu belirten enum değeri.
            context (str): İşlemin hangi bağlamda gerçekleştiğini belirten açıklama.
        """
        if not context:
            return 
        log_message = f"{context.value} - {status.value}\n"
        temp_file_path = f"{INSTALL_STATUS_FILE_PATH}.tmp"
        
        try:
            # Geçici bir dosyaya yazma işlemi yapıyoruz.
            with open(temp_file_path, "w") as log_file:
                log_file.write(log_message)
                log_file.flush()  # Tampondaki veriyi dosyaya yaz.
                os.fsync(log_file.fileno())  # Dosya deskriptorunu senkronize et.
            
            # Geçici dosyayı orijinal dosya ile değiştiriyoruz.
            os.replace(temp_file_path, INSTALL_STATUS_FILE_PATH)
        except Exception as e:
            logger.error(f"Install status dosyasına yazılırken hata oluştu: {e}")
            # Geçici dosya oluşturulmuşsa silinmesi için bir önlem.
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    @staticmethod
    def get_install_status():
        """
        InstallStatus değerini dosyadan okur ve döner.

        Returns:
            tuple: Dosyada en son kaydedilen context ve InstallStatus değeri,
                   eğer dosya okunamazsa (None, None) döner.
        """
        try:
            if os.path.exists(INSTALL_STATUS_FILE_PATH):
                with open(INSTALL_STATUS_FILE_PATH, "r") as log_file:
                    line = log_file.readline().strip()
                    if line:
                        context, status_value = line.split(" - ")
                        return context, status_value
            else:
                return None, None
        except Exception as e:
            logger.error(f"Install status dosyası okunurken hata oluştu: {e}")
            return None, None

    @staticmethod
    def clear_install_status():
        """
        Install status dosyasını temizler.
        """
        try:
            if os.path.exists(INSTALL_STATUS_FILE_PATH):
                os.remove(INSTALL_STATUS_FILE_PATH)
        except Exception as e:
            logger.error(f"Install status dosyası temizlenirken hata oluştu: {e}")

    def handle_initial_errors(self):
        """
        Daha önceki işlemlerin hata durumlarını kontrol eder ve duruma göre geri dönüş işlemleri yapar.
        """
        result = ErrorManager.get_install_status()
        
        # Sonuç None değilse unpack işlemi yap
        if result is not None:
            last_context, last_status = result
        else:
            # None dönerse uygun bir varsayılan değer ata
            last_context, last_status = None, None

        # Eğer hiç log kaydı yoksa işlemlere devam et
        if not last_context or not last_status:
            self.git_manager.clean_update_directories()
            return True
        
        # Context: OCPP Install
        if last_context ==  InstallContext.OCPP_INSTALL.value:
            if last_status in [InstallStatus.SUCCESS.value, 
                               InstallStatus.EXTRACT_FW_FAILED.value,
                               InstallStatus.UPDATE_DATABASE_FAILED.value,
                               ]:
                # Başarılı tüm dosyaları sil
                self.git_manager.clean_update_directories()
                self.ocpp_update_manager.clean_firmware_file()
                ErrorManager.clear_install_status()
                return False

            elif last_status in [InstallStatus.START_OPERATION.value, 
                                 InstallStatus.SERVICE_STOP_FAILED.value,
                                 InstallStatus.UPDATE_DATABASE_STARTED.value,
                                 ]:
                self.git_manager.clean_update_directories()
                return False

            elif last_status in [InstallStatus.FINAL_OPERATION_STARTED.value,
                                 InstallStatus.FINAL_OPERATION_SUCCESS.value,
                                ]:
                # Başarılı ancak geri yükleme istiyoruz, fw dosyası kalmalı
                self.restore_manager.restore_previous_version()
                return False

            elif last_status in [InstallStatus.FINAL_OPERATION_FAILED.value]:
                # İşlem başlamış ancak kesintiye uğramış, eski dosyaları geri yükle ve fw dosyası sil
                self.restore_manager.restore_previous_version()
                return False
            elif last_status == InstallStatus.SERVICE_START_FAILED.value:
                # Servis başlatılamadı, eski dosyaları geri yükle ve fw dosyası sil
                self.restore_manager.restore_previous_version()
                return False
            else:
                # Bilinmeyen bir hata durumu varsa devam et
                logger.info("Önceki işlem durumlarına göre bir hata bulunamadı, işlemlere devam ediliyor.")
                ErrorManager.clear_install_status()
                return False

        # Context: Git Install
        elif last_context == InstallContext.GIT_INSTALL.value:
            if last_status in [InstallStatus.SUCCESS.value,
                               InstallStatus.START_OPERATION.value,
                               InstallStatus.SERVICE_STOP_FAILED.value,
                               InstallStatus.UPDATE_DATABASE_STARTED.value]:
                 # Başarılı durumda eskileri sil
                 self.git_manager.clean_update_directories()
                 ErrorManager.clear_install_status()
                 return False

            elif last_status in [InstallStatus.UPDATE_DATABASE_FAILED.value]:
                # İşlem başlamış ancak database kontrol edildiktan sonra kesintiye uğramış, eski dosyaları sil ve beklemeye al
                self.restore_manager.restore_previous_version()
                self.git_manager.clean_update_directories()
                self.update_fail_wait_manager.install_failed()
                return False
            
            elif last_status in [InstallStatus.FINAL_OPERATION_FAILED.value]:
                # İşlem başlamış ancak kesintiye uğramış, eski dosyaları geri yükle ve beklemeye al
                self.restore_manager.restore_previous_version()
                return False
            
            elif last_status in [InstallStatus.FINAL_OPERATION_STARTED.value,
                                 InstallStatus.FINAL_OPERATION_SUCCESS.value,]:
                # Başarılı ancak geri yükleme istiyoruz
                self.restore_manager.restore_previous_version()
            elif last_status == InstallStatus.SERVICE_START_FAILED.value:
                # Servis başlatılamadı, eski dosyaları geri yükle
                self.restore_manager.restore_previous_version()
                self.update_fail_wait_manager.install_failed()
            else:
                # Bilinmeyen bir hata durumu varsa devam et
                logger.info("Önceki işlem durumlarına göre bir hata bulunamadı, işlemlere devam ediliyor.")
                ErrorManager.clear_install_status()
                return False
            
        # Context: Restore Install
        elif last_context == InstallContext.RESTORE_INSTALL.value:
            if last_status == InstallStatus.SUCCESS.value:
                # Başarılı durumda eskileri sil
                self.git_manager.clean_update_directories()
                ErrorManager.clear_install_status()
                self.restore_retry_count = 0
                return False
            elif last_status == InstallStatus.SERVICE_START_FAILED.value:
                # İşlem başlamış ancak servis başlatılamamış, root backup dosyalarını geri yükle
                logger.info("Servis başlatılamadı, eski dosyalar düzgün çalışmadı.")
                if self.restore_retry_count < 10:
                    self.restore_manager.restore_previous_version()
                    self.restore_retry_count += 1
                    return False
                else:
                    self.restore_retry_count = 0
                    ErrorManager.clear_install_status()
                    return False
            else:
                if self.restore_retry_count < 10:
                    self.restore_manager.restore_previous_version()
                    self.restore_retry_count += 1
                    return False
                else:
                    self.restore_retry_count = 0
                    ErrorManager.clear_install_status()
                    return False

        # clear install status
        ErrorManager.clear_install_status()
        return True  
  
def perform_ocpp_update():
    """
    OCPP güncellemelerini gerçekleştirir.

    Returns:
        InstallStatus: İşlemin sonucunu belirten enum değeri.
    """
    fw_file_path = ocpp_update_manager.find_firmware_file()
    if not fw_file_path:
        logger.debug("Fw dosyası bulunamadı.")
        return False
    
    logger.info(f"{ocpp_update_manager.fw_file_path} bulundu, fw dosyasından güncelleme yapılacak.")
    os.chdir(ROOT_DIR)
    
    # Install Context: OCPP Update
    install_context = InstallContext.OCPP_INSTALL
    # Clear Context: Git Update
    ErrorManager.clear_install_status()

    ErrorManager.save_install_status(InstallStatus.START_OPERATION, install_context)

    # Fw dosyasını çıkar
    if not ocpp_update_manager.extract_firmware_files(ocpp_update_manager.fw_file_path):
        logger.error("Fw dosyası çıkartılamadı.")
        ErrorManager.save_install_status(InstallStatus.EXTRACT_FW_FAILED, install_context)
        return True

    
    # Servisi durdur
    if not ServiceManager.stop_service():
        ServiceManager.start_service()
        ErrorManager.save_install_status(InstallStatus.SERVICE_STOP_FAILED, install_context)
        logger.error("Servis durdurulamadı.")
        return True
    

    led_manager.start_led_thread()

    git_manager.clean_old_directory()

    git_manager.backup_acapp_directory()

    ErrorManager.save_install_status(InstallStatus.UPDATE_DATABASE_STARTED, install_context)
    
    # Veritabanı güncellemesi
    if not file_manager.update_database_files_in_new_repo(ACAPP_NEW_DIR):
        logger.error("Veritabanı dosyaları güncellenirken hata oluştu.")
        ErrorManager.save_install_status(InstallStatus.UPDATE_DATABASE_FAILED, install_context)
        return True


    # Son işlemleri yap
    final_operations_status = final_operations_manager.perform_final_operations(install_context)
    if not final_operations_status:
        logger.error("Son işlemler sırasında hata oluştu:")
        return True


    # Servisi başlat ve geri dönen değeri kontrol et
    if not ServiceManager.start_service():
        logger.error("Servis başlatılamadı ya da PID değişti, yeni repo sorunlu olabilir.")
        ErrorManager.save_install_status(InstallStatus.SERVICE_START_FAILED, install_context)
        return True
    
    logger.info("Servis başarıyla başlatıldı ve sorunsuz çalışıyor. Eski repo ve dosyalar siliniyor.")

    ErrorManager.save_install_status(InstallStatus.SUCCESS, install_context)
    
    return True

def perform_roll_back():
    """
    Geri alma işlemini gerçekleştirir.
    Returns:
        InstallStatus: İşlemin sonucunu belirten enum değeri.
    """
    fw_file_path = BACKUP_FW_DIR
    if not fw_file_path:
        return False
    
    logger.info(f" Rollback işlemi başlatılıyor. {fw_file_path} bulundu, fw dosyasından geri alma yapılacak.")
    os.chdir(ROOT_DIR)
    
    # Fw dosyasını çıkar
    if not ocpp_update_manager.extract_firmware_files(fw_file_path):
        logger.debug("Fw dosyası çıkartılamadı.")

    
    # Servisi durdur
    if not ServiceManager.stop_service():
        logger.error("Servis durdurulamadı.")
        return False
    
    led_manager.start_led_thread()

    # Repoyu taşı
    final_operations_manager.final_copy_for_repo(ACAPP_DIR, ACAPP_NEW_DIR)

    # Veritabanlarını taşı
    file_manager.copy_rootpaths_files_to_root()

     # MCU Firmware güncelleme kontrolü
    new_firmware_dir = os.path.join(ACAPP_DIR, "mcufirmware")
    firmware_file = os.path.join(new_firmware_dir, mcu_manager.get_firmware_file(new_firmware_dir))

    # Eski firmware dosyasını yükleyip güncelleme kontrolü yap
    if mcu_manager.retry_mcu_update(firmware_file, 3):
        logging.info("Rollback firmware dosyası yüklendi ve güncelleme kontrolü yapıldı.")
    else:
        logging.error("Rollback firmware dosyası yüklenemedi.")

    # Servisi başlat ve geri dönen değeri kontrol et
    if not ServiceManager.start_service():
        logger.error("Rollback servicesi başlatılamadı ya da PID değişti, yeni repo sorunlu olabilir.")
    
    logger.info("Servis başarıyla başlatıldı ve sorunsuz çalışıyor.")

    return

def perform_git_update():
    """
    Git üzerinden güncellemeleri gerçekleştirir.

    Returns:
        InstallStatus: İşlemin sonucunu belirten enum değeri.
    """

    if not git_manager.check_for_git_changes():
        return False

    os.chdir(ROOT_DIR)

    # Install Context: Git Update
    install_context = InstallContext.GIT_INSTALL


    # Clear Context: Git Update
    ErrorManager.clear_install_status()


    # Servisi durdur
    if not ServiceManager.stop_service():
        logger.error("Servis durdurulamadı.")
        ErrorManager.save_install_status(InstallStatus.SERVICE_STOP_FAILED, install_context)
        return True

    ErrorManager.save_install_status(InstallStatus.START_OPERATION, install_context)

    led_manager.start_led_thread()

    git_manager.backup_acapp_directory()

    git_manager.clone_new_repo()

    ErrorManager.save_install_status(InstallStatus.UPDATE_DATABASE_STARTED, install_context)

    # Veritabanı güncellemesi
    if not file_manager.update_database_files_in_new_repo(ACAPP_NEW_DIR):
        logger.error("Veritabanı dosyaları güncellenirken hata oluştu.")
        ErrorManager.save_install_status(InstallStatus.UPDATE_DATABASE_FAILED, install_context)
        return True

    final_operations_status = final_operations_manager.perform_final_operations(install_context)
    if not final_operations_status:
        logger.error("Son işlemler sırasında hata oluştu:")
        return True

    if not ServiceManager.start_service():
        logger.error("Servis başlatılamadı ya da PID değişti, yeni repo sorunlu olabilir.")
        ErrorManager.save_install_status(InstallStatus.SERVICE_START_FAILED, install_context)
        return True
    
    logger.info("Servis başarıyla başlatıldı ve sorunsuz çalışıyor. Eski repo ve dosyalar siliniyor.")
    ErrorManager.save_install_status(InstallStatus.SUCCESS, install_context)
    return True

def should_retry_update():
    """
    Güncelleme işleminin tekrar edilip edilmeyeceğine karar verir.
    
    Returns:
        bool: Güncellemenin tekrar edilip edilmeyeceğine karar verir.
    """
    if not update_fail_wait_manager.should_retry():
        return False
    if not network_manager.is_internet_available():
        logger.error("İnternet bağlantısı yok, işlem sonlandırıldı.")
        return False
    return True

if __name__ == '__main__':
    git_manager = GitManager()
    network_manager = NetworkManager()
    database_manager = DatabaseManager()
    file_manager = FileManager(database_manager)
    led_manager = LedManager(SERIAL_PORT_PATH)
    update_fail_wait_manager = UpdateFailWaitManager(6, 0)
    mcu_manager = MCUManager(led_manager)
    charge_manager = ChargeManager()
    ocpp_update_manager = OcppUpdateManager(OCPP_FIRMWARE_DIR)
    final_operations_manager = FinalOperationsManager(file_manager, git_manager, mcu_manager)
    restore_manager = RestoreManager(ACAPP_OLD_DIR, ACAPP_DIR, led_manager, mcu_manager)
    error_manager = ErrorManager(
                                    restore_manager=restore_manager,
                                    final_operations_manager=final_operations_manager,
                                    mcu_manager=mcu_manager,
                                    update_fail_wait_manager=update_fail_wait_manager,
                                    git_manager=git_manager,
                                    ocpp_update_manager=ocpp_update_manager
                                )
    
    # Ana döngü
    while True:
        led_manager.stop_led_thread()
        sleep_time = 60  # Her döngüde 60 saniye beklet
        logger.info(f"Kontrollerden önce {sleep_time} saniye bekleniyor.")
        time.sleep(sleep_time)

        # Önceki işlemlerin hata durumlarını kontrol et
        if not error_manager.handle_initial_errors():
            continue

        # Servis kontrolü
        if not ServiceManager.is_service_active():
            ServiceManager.start_service()
            time.sleep(600)
            if not ServiceManager.is_service_active():
                perform_roll_back()
                ErrorManager.clear_install_status()
                git_manager.clean_update_directories()
                continue

        # Şarj kontrolü
        if charge_manager.is_there_charge():
            logger.info("Şarj işlemi devam ettiği için güncelleme yapılmayacak.")
            continue
        
        # OCPP güncellemesi işlemi
        ocpp_update_status = perform_ocpp_update()
        if ocpp_update_status:
            continue
      
        # Git güncellemesi kontrolü
        if should_retry_update():
            git_update_status = perform_git_update()
            if git_update_status:
                continue