import os
import shutil
import subprocess
import logging
import requests
import time
import threading
import fcntl
import sqlite3
import zipfile
import serial
import threading
from logging.handlers import RotatingFileHandler
from enum import Enum


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



class LedState(Enum):
    FirmwareUpdate = ">"

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

class CommandRunner:
    """
    OS komutlarını çalıştırmak için yardımcı sınıf
    """
    @staticmethod
    def run_os_command(command):
        try:
            logger.info(f"Komut çalıştırılıyor: {command}")
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            return result
        except Exception as e:
            logger.error(f"Komut çalıştırma hatası: {command}\nException: {e}")
            return None

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

    def is_there_charge(self):
        """
        Veritabanındaki 'charge' durumunu kontrol eder.
        
        Returns:
            bool: Eğer 'charge' değeri 'True' ise True, aksi takdirde False döner.
        """
        try:
            data_dict = {}

            # Eğer veritabanı dosyası yoksa False döner
            if not os.path.exists(self.db_path):
                logger.error(f"Veritabanı dosyası bulunamadı: {self.db_path}")
                return False

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

        except sqlite3.Error as e:
            logger.error(f"SQLite hatası: {e}")
            return False
        except IOError as e:
            logger.error("Dosya kilitli")
            time.sleep(1)
            return self.is_there_charge()  # Tekrar deneyin
        except Exception as e:
            logger.error(f"is_there_charge Exception: {e}")
            return self.is_there_charge()  # Hata durumunda tekrar deneyin

class ServiceManager:
    """
    Servis durdurma, başlatma ve durum kontrolü işlemleri
    """
    @staticmethod
    def stop_service(service_name="acapp.service"):
        logger.info(f"{service_name} servisi durduruluyor...")
        result = subprocess.run(['systemctl', 'stop', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            logger.info(f"{service_name} servisi başarıyla durduruldu.")
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
                logger.error(f"{service_name} servisi başlatıldı ancak PID değişti! Sorun olabilir.")
                
                # LED durumunu güncelle
                led_manager.stop_led_thread()
                return False
        else:
            logger.error(f"{service_name} servisi başlatılamadı!")
            led_manager.stop_led_thread()
            return False
    
    @staticmethod
    def restart_service(service_name):
        """
        Servisi yeniden başlatır ve servisin başarılı şekilde çalıştığını kontrol eder.
        """
        subprocess.run(['systemctl', 'restart', service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        logger.info(f"{service_name} servisi yeniden başlatıldı. Kontroller için 25 saniye bekleniyor...")
        time.sleep(10)  # Kontrol öncesi 10 saniye bekle

        if ServiceManager.is_service_active(service_name):
            # PID izleme sadece başlangıçtan sonra
            pid_not_changed = ServiceManager.monitor_service_pid(service_name)
            
            if pid_not_changed:
                return True  # Başarılı
            else:
                logger.error(f"{service_name} servisi başlatıldı ancak PID değişti! Sorun olabilir.")
                return False
        else:
            logger.error(f"{service_name} servisi başlatılamadı!")
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
        try:
            logger.info("İnternet bağlantısı kontrol ediliyor...")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("İnternet bağlantısı mevcut.")
                return True
        except requests.ConnectionError:
            logger.error("İnternet bağlantısı yok.")
            return False
        return False

class GitManager:
    def __init__(self, repo_url, acapp_dir="/root/acApp"):
        self.repo_url = repo_url
        self.acapp_dir = acapp_dir
        self.acapp_old_dir = f"{self.acapp_dir}_old"
        self.acapp_new_dir = f"{self.acapp_dir}_new"
        self.root_dir = "/root"

    def clean_old_directories(self):
        """
        acApp_old ve acApp_new dizinlerini kaldırır eğer mevcutlarsa.
        """
        try:
            if os.path.exists(self.acapp_old_dir):
                shutil.rmtree(self.acapp_old_dir)
                logger.info(f"{self.acapp_old_dir} başarıyla kaldırıldı.")

            if os.path.exists(self.acapp_new_dir):
                shutil.rmtree(self.acapp_new_dir)
                logger.info(f"{self.acapp_new_dir} başarıyla kaldırıldı.")
        except Exception as e:
            logger.error(f"Eski dizinler kaldırılırken hata oluştu: {e}")

    def backup_acapp_directory(self):
        """
        acApp dizinini acApp_old olarak yedekler.
        """
        try:
            if os.path.exists(self.acapp_dir):
                logger.info(f"{self.acapp_dir} dizini {self.acapp_old_dir} olarak yedekleniyor...")
                
                # Eğer hedef dizin varsa, önce eski yedeği sil
                if os.path.exists(self.acapp_old_dir):
                    if os.path.isdir(self.acapp_old_dir):
                        shutil.rmtree(self.acapp_old_dir)
                    else:
                        os.remove(self.acapp_old_dir)
                    logger.info(f"Eski {self.acapp_old_dir} silindi.")
                
                # Dizini kopyala
                shutil.copytree(self.acapp_dir, self.acapp_old_dir)
                logger.info(f"{self.acapp_dir} başarıyla {self.acapp_old_dir} olarak yedeklendi.")
                self.root_paths_backup()
            else:
                logger.error(f"{self.acapp_dir} dizini bulunamadı, yedekleme yapılmadı.")
        except Exception as e:
            logger.error(f"acApp dizini yedeklenirken hata oluştu: {e}")


    def root_paths_backup(self):
        # acapp_old_dir+rootpaths dizinini kontrol et ve içersindeki dosya isimlerini al
        # Root dizinindeki bu dosya isimleri ile aynı olan dosyaları acapp_old_dir+rootpaths dizinine taşı
        try:
            if os.path.exists(self.acapp_old_dir):
                rootpaths_dir = os.path.join(self.acapp_old_dir, "rootpaths")
                if os.path.exists(rootpaths_dir):
                    logger.info(f"{rootpaths_dir} dizini kontrol ediliyor...")
                    for filename in os.listdir(rootpaths_dir):
                        if os.path.isfile(os.path.join(self.root_dir, filename)):
                            shutil.copy2(os.path.join(self.root_dir, filename), os.path.join(rootpaths_dir, filename))
                            logger.info(f"{filename} dosyası {rootpaths_dir} dizinine başarıyla taşındı.")
                        else:
                            logger.error(f"{filename} dosyası {self.root_dir} dizininde bulunamadı.")
                else:
                    logger.error(f"{rootpaths_dir} dizini bulunamadı.")
            else:
                logger.error(f"{self.acapp_old_dir} dizini bulunamadı.")

        except Exception as e:
            logger.error(f"rootpaths_backup hatası: {e}")
            

    def check_for_git_changes(self):
        """
        Git değişikliklerini kontrol eder.
        """
        try:
            logger.info(f"Git değişiklikleri kontrol ediliyor...")
            os.chdir(self.acapp_dir)
            subprocess.run(['git', 'fetch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            changes = subprocess.run(['git', 'log', 'HEAD..origin/main', '--oneline'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            if changes.stdout.strip():  # Eğer bir değişiklik varsa
                logger.info(f"Git'te yeni değişiklikler mevcut:\n{changes.stdout.strip()}")
                # change dir
                os.chdir(self.root_dir)
                return True
            else:
                logger.info("Yazılım güncel, değişiklik yok.")
                os.chdir(self.root_dir)
                return False
        except Exception as e:
            logger.error(f"Git değişiklik kontrolü sırasında hata oluştu: {e}")
            os.chdir(self.root_dir)
            return False

    def clone_new_repo(self):
        """
        Git'ten yeni repoyu acApp_new dizinine klonlar.
        """
        try:
            logger.info(f"Git reposu {self.repo_url} klonlanıyor...")
            # Change directory
            os.chdir(self.root_dir)

            result = subprocess.run(['git', 'clone', self.repo_url, self.acapp_new_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            if result.returncode == 0:
                logger.info(f"Git reposu başarıyla {self.acapp_new_dir} dizinine klonlandı.")
            else:
                logger.error(f"Git klonlama başarısız oldu: {result.stderr}")
        except Exception as e:
            logger.error(f"Git klonlama sırasında hata oluştu: {e}")

class MCUManager:
    """
    MCU güncellemeleri için yardımcı sınıf.
    """
    def __init__(self, led_manager):
        self.update_failed_three_times = False
        self.led_manager = led_manager

    def set_gpio(self, port, pin, value):
        try:
            command = f"gpio-test.64 w {port} {pin} {value}"
            subprocess.run(command, shell=True, check=True)
            logger.info(f"{command}")
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

            logger.info(f"Firmware yolu: {firmware_path}")

            # MCU güncellemesi için 10 saniye bekle
            time.sleep(10)

            logger.info("MCU güncelleniyor...")

            # Firmware yükleme komutu
            command = ['dfu-util', '-a', '0', '-s', '0x08020000:leave', '-D', firmware_path]
            log_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            logger.info(f"{command}")
            log_output = log_result.stdout
            logger.info(f"Firmware update log: {log_output}")

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
                logger.info("Firmware başarıyla yüklendi.")
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
            logger.info(f"MCU firmware güncelleme denemesi {attempt + 1}")
            if self.update_mcu_firmware(firmware_path):
                return True
            time.sleep(10)
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
            logger.info(f"Eski ve yeni firmware dosyaları bulundu: {firmware_file_old}, {firmware_file_new}")
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
                logger.info("Firmware dosyaları aynı, güncelleme yapılmasına gerek yok.")
                return True  # Güncellemeye gerek yok
        
        # Eski firmware var ama yeni firmware yoksa
        elif firmware_file_old and not firmware_file_new:
            logger.error(f"Yeni firmware dosyası bulunamadı: {new_firmware_dir}")
            return False
        
        # Eskisi firmaware yoksa ama yeni firmware varsa
        elif not firmware_file_old and firmware_file_new:
            logger.error(f"Eski firmware dosyası bulunamadı yeni firmware dosyası yüklenecek: {new_firmware_dir}")
            new_firmware_path = os.path.join(new_firmware_dir, firmware_file_new)

            # Firmware yükleme işlemi
            if not self.retry_mcu_update(new_firmware_path, 3):
                return True  # Güncelleme başarılı
            else:
                return False # Güncelleme başarısız
        else:
            logger.error("Firmware dosyaları bulunamadı.")
            return False
        
class FileManager:
    """Dosya kopyalama ve yönetim işlemleri için sınıf."""

    def __init__(self, database_manager, root_dir):
        """
        FileManager sınıfının başlatıcısı. Kopyalama ve taşıma işlemleri için gerekli dizinler ayarlanır.
        
        Args:
            database_manager: Veritabanı dosyalarının taşınması sırasında kullanılacak DatabaseManager örneği.
            root_dir: Eski root dizinindeki veritabanı dosyalarının bulunduğu yer.
            new_repo_path: Yeni repodaki rootpaths dizinini belirtir.
        """
        self.root_dir = root_dir  # Eski root dizini
        self.database_manager = database_manager
        self.target_dir = None  # Yeni repodaki rootpaths dizini
        self.python_command = "python3"  # Python komutunu burada ayarlıyoruz

    
    def run_external_script(self, script_path):
        """
        Harici bir Python betiğini çalıştırır.
        
        Args:
            script_path (str): Çalıştırılacak Python betiğinin yolu.
        
        Returns:
            bool: Eğer betik başarılı bir şekilde çalıştırılırsa True, aksi takdirde False döner.
        """
        try:
            logger.info(f"Harici betik çalıştırılıyor: {script_path}")
            result = subprocess.run([self.python_command, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if result.returncode == 0:
                logger.info(f"Betik başarıyla çalıştırıldı: {script_path}")
                return True
            else:
                logger.error(f"Betik çalıştırma hatası: {script_path}\n{result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Betik çalıştırma sırasında hata: {script_path}\n{e}")
            return False


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

    def restore_backup_root_paths(self, backup_root_dir):
        """Yedeklenen dizini geri yükler."""

        try:
            if not os.path.exists(backup_root_dir):
                logger.error(f"Yedek dizini mevcut değil: {backup_root_dir}")
                return False

            # Yedek dizinindeki dosyaları root dizinine kopyalama işlemi
            for filename in os.listdir(backup_root_dir):
                if os.path.isdir(os.path.join(backup_root_dir, filename)):
                    shutil.copytree(os.path.join(backup_root_dir, filename), os.path.join(self.root_dir, filename))
                    logger.info(f"{backup_root_dir} klasöründeki {filename} dosyası {self.root_dir} klasörüne başarıyla kopyalandı.")
                else:
                    shutil.copy2(os.path.join(backup_root_dir, filename), os.path.join(self.root_dir, filename))
                    logger.info(f"{backup_root_dir} klasöründeki {filename} dosyası {self.root_dir} klasörüne başarıyla kopyalandı.")
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
      
    def restore_old_repo(self, real_repo_path, old_repo_path):
        try:
            if not os.path.exists(old_repo_path):
                logger.error(f"Eski repo dizini mevcut değil: {old_repo_path}")
                return False
            
            validation_status = self.validate_directory(real_repo_path)
            if not validation_status:
                return False
            
            validation_status = self.validate_directory(old_repo_path)
            if not validation_status:
                return False

            # Eski repoyu sil ve yeni repoyu taşı
            shutil.rmtree(real_repo_path)
            if os.path.isdir(old_repo_path):
                shutil.copytree(old_repo_path, real_repo_path)
                logger.info(f"{old_repo_path} klasörü {real_repo_path} klasörüne başarıyla taşındı.")
            else:
                shutil.copy2(old_repo_path, real_repo_path)
                logger.info(f"{old_repo_path} dosyası {real_repo_path} klasörüne başarıyla taşındı.")

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
   
    def final_copy_for_repo(self, real_repo_path, new_repo_path):
        # Yeni repoyu real_repo_path dizinine taşıma işlemi
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
            logger.info(f"{new_repo_path} klasörü {real_repo_path} klasörüne başarıyla taşındı.")
            
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
        # Yeni repodaki rootpaths dizinine kopyalama işlemi
        try:
            if not os.path.exists(new_repo_path):
                logger.error(f"Yeni repo dizini mevcut değil: {new_repo_path}")
                return False
            
            self.target_dir = os.path.join(new_repo_path, "rootpaths")  # Yeni repodaki rootpaths dizini

            # Kaynak dizin doğrulaması
            validation_status = self.validate_directory(self.root_dir)
            if not validation_status:
                return False
            
            validation_status = self.validate_directory(self.target_dir)
            if not validation_status:
                return False
            

            # Veritabanı hariç rootpatsh dosyalarını taşıma işlemi
            for filename in os.listdir(self.target_dir):
                # filename external_run.py ve sync_database.py dosyalarını taşıma işlemi dışında bırakır
                if filename.endswith(("external_run.py", "sync_database.py")):
                    continue

                if not filename.endswith((".sqlite", ".db")):
                    source_path = os.path.join(self.target_dir, filename)
                    target_path = os.path.join(self.root_dir, filename)

                    shutil.copy2(source_path, target_path)
                    logger.info(f"{source_path} dosyası {target_path} dizinine başarıyla taşındı.")
          
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
   
    def update_database_files_in_new_repo(self, new_repo_path):
        """Eski root dizinindeki db dosyalarını yeni repodaki rootpaths dizinine göre günceller."""
        try:
            if not os.path.exists(new_repo_path):
                logger.error(f"Yeni repo dizini mevcut değil: {new_repo_path}")
                return False
            
            self.target_dir = os.path.join(new_repo_path, "rootpaths")  # Yeni repodaki rootpaths dizini
           
            # Kaynak dizin doğrulaması
            validation_status = self.validate_directory(self.root_dir)
            if not validation_status:
                return False
            
            validation_status = self.validate_directory(self.target_dir)
            if not validation_status:
                return False

            # Veritabanı dosyalarını taşıma işlemi
            for filename in os.listdir(self.root_dir):
                if filename.endswith((".sqlite", ".db")):
                    source_path = os.path.join(self.root_dir, filename)
                    target_path = os.path.join(self.target_dir, filename)

                    # Set the sync script path
                    self.database_manager.set_sync_script_path(os.path.join(self.target_dir, "sync_database.py"))
                    # Veritabanı taşıma işlemi database_manager kullanılarak yapılır.
                    self.database_manager.update_old_databases(source_path, target_path)
                    logger.info(f"{source_path} dosyası {target_path} dizinine başarıyla taşındı.")
            
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
            logger.info(f"Eski veritabanına ({self.old_db_path}) başarıyla bağlanıldı.")
        except sqlite3.Error as e:
            logger.error(f"Eski veritabanına bağlanılamadı: {e}")
            return False

        try:
            self.new_conn = sqlite3.connect(self.new_db_path)
            logger.info(f"Yeni veritabanına ({self.new_db_path}) başarıyla bağlanıldı.")
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
            logger.info("Veritabanı bağlantıları başarıyla kapatıldı.")
        except sqlite3.Error as e:
            logger.error(f"Veritabanı bağlantılarını kapatma hatası: {e}")

    def compare_database_versions(self):
        """
        Eski ve yeni veritabanındaki 'database_version' tablosundaki 'version' değerini karşılaştırır.
        """
        try:
            old_version = self.old_conn.execute(self.table_versions_query).fetchone()[0]
            new_version = self.new_conn.execute(self.table_versions_query).fetchone()[0]

            logger.info(f"Eski veritabanı version: {old_version}, Yeni veritabanı version: {new_version}")

            if old_version == new_version:
                logger.info("Veritabanı versiyonları eşleşiyor. Veritabanı yeni dizine kopyalanacak...")
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
            logger.info("Python betiği başarıyla çalıştırıldı.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Python betiği çalıştırılırken hata oluştu: {e}")

    def copy_all_tables(self):
        """
        Eski veritabanındaki tüm tabloları yeni veritabanına kopyalar.
        """
        try:
            # Tüm tablo adlarını al
            old_cursor = self.old_conn.cursor()
            old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = old_cursor.fetchall()

            for table in tables:
                table_name = table[0]
                self.copy_all_data(table_name)

        except sqlite3.Error as e:
            logger.error(f"Tablo kopyalama işlemi sırasında hata: {e}")

    def copy_database_file_to_new_directory(self):
        """
        Eski veritabanını yeni veritabanına kopyalar.
        """
        try:
            logger.info("Veritabanı dosyası kopyalanıyor...")
            shutil.copy2(self.old_db_path, self.new_db_path)
            logger.info("Veritabanı dosyası başarıyla kopyalandı.")
        except FileNotFoundError as fnf_error:
            logger.error(f"Veritabanı dosyası kopyalanırken hata: {fnf_error}")
        except PermissionError as perm_error:
            logger.error(f"Veritabanı dosyası kopyalanırken hata: {perm_error}")
        except Exception as e:
            logger.error(f"Veritabanı dosyası kopyalanırken beklenmeyen bir hata oluştu: {e}")

    def copy_all_data(self, table_name):
        """
        Eski veritabanındaki tüm verileri yeni veritabanına kopyalar. 
        Yeni veritabanındaki tabloyu önce boşaltır, ardından tüm verileri ekler.
        
        Args:
            table_name: Kopyalanacak tablo adı.
        """
        try:
            old_cursor = self.old_conn.cursor()
            new_cursor = self.new_conn.cursor()

            # Yeni veritabanındaki tabloyu boşalt
            logger.info(f"{table_name} tablosu yeni veritabanında boşaltılıyor...")
            new_cursor.execute(f"DELETE FROM {table_name}")

            # Eski veritabanından tüm verileri çek
            old_cursor.execute(f"SELECT * FROM {table_name}")
            rows = old_cursor.fetchall()

            # Tablonun sütun sayısını öğren
            old_cursor.execute(f"PRAGMA table_info({table_name})")
            column_count = len(old_cursor.fetchall())

            # Yeni veritabanına tüm verileri ekle
            placeholders = ", ".join("?" * column_count)  # Sütun sayısına göre placeholder oluştur
            for row in rows:
                new_cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

            # Değişiklikleri kaydet
            self.new_conn.commit()
            logger.info(f"{table_name} tablosundaki tüm veriler başarıyla kopyalandı.")
        except sqlite3.Error as e:
            logger.error(f"{table_name} tablosu kopyalanırken hata: {e}")

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

class ZipManager:
    def __init__(self, zip_file_dir, root_dir):
        self.zip_file_dir = zip_file_dir  # Zip dosyasının olduğu dizin
        self.zip_file_path = None  # Zip dosyasının yolu
        self.root_dir = root_dir  # Zip dosyasının çıkarılacağı dizin

    def find_zip_file(self):
        """
        Zip dosyasını zip_file_dir içinde bulur. Sadece bir zip dosyasının olacağı varsayılır.
        """
        logger.info(f"Zip dosyası aranıyor: {self.zip_file_dir}")
        # Dizin mevcut değilse oluştur
        if not os.path.exists(self.zip_file_dir):
            logging.info(f"{self.zip_file_dir} dizini mevcut değil, oluşturuluyor.")
            os.makedirs(self.zip_file_dir)

        zip_files = [file for file in os.listdir(self.zip_file_dir) if file.endswith(".zip")]

        if len(zip_files) == 1:
            self.zip_file_path = os.path.join(self.zip_file_dir, zip_files[0])
            logging.info(f"Zip dosyası bulundu: {self.zip_file_path}")
            return True
        elif len(zip_files) > 1:
            logging.error("Birden fazla zip dosyası bulundu, yalnızca bir zip dosyasının olması bekleniyor.")
            return False
        else:
            logging.warning("Zip dosyası bulunamadı.")
            return False

    def extract_rename_zip(self):
        """
        Zip dosyasını extracted_zip_dir "extracted_temp_zip" adıyla çıkarır.ve o dosyanın adını acapp_new_dir olarak değiştirir.
        """
        if not self.zip_file_path:
            logging.warning("Zip dosyası bulunamadı.")
            return False
        
        try:

            # Zip için geçici bir dizin oluştur
            extracted_zip_dir = os.path.join(self.root_dir, "extracted_temp_zip")
            if not os.path.exists(extracted_zip_dir):
                os.makedirs(extracted_zip_dir)
            
            # Zip dosyasını çıkar
            with zipfile.ZipFile(self.zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_zip_dir)
                logging.info(f"{self.zip_file_path} dosyası {extracted_zip_dir} dizinine çıkarıldı.")

            # extracted_zip_dir'in içersindeki acApp dizinini acapp_new_dir olarak değiştir ve /root dizinine taşı
            extracted_acapp_dir = os.path.join(extracted_zip_dir, "acApp")
            self.acapp_new_dir = os.path.join(self.root_dir, "acApp_new")
            
            # "acApp" klasörünün varlığını kontrol et
            if not os.path.exists(extracted_acapp_dir):
                logging.error(f"{extracted_acapp_dir} dizini bulunamadı. Dosya yapısı beklendiği gibi değil.")
                return False
            
            # Eğer hedef dizin mevcutsa, önce onu sil
            if os.path.exists(self.acapp_new_dir):
                logging.info(f"{self.acapp_new_dir} dizini mevcut, siliniyor...")
                shutil.rmtree(self.acapp_new_dir)


            # Klasörü taşı (rename yerine move kullanıyoruz)
            shutil.move(extracted_acapp_dir, self.acapp_new_dir)
            logging.info(f"{extracted_acapp_dir} dizini başarıyla {self.acapp_new_dir} olarak taşındı.")
                
            # extracted_zip_dir'i sil
            shutil.rmtree(extracted_zip_dir)
            logging.info(f"{extracted_zip_dir} dizini temizlendi.")

            return True
        except zipfile.BadZipFile as e:
            logging.error(f"Zip dosyası çıkarılırken hata oluştu: {e}")
            return False
        except Exception as e:
            logging.error(f"Beklenmeyen bir hata oluştu: {e}")
            return False
        
    def clean_zip_file(self):
        """
        Zip dosyasını temizler.
        """
        if not self.zip_file_path:
            logging.warning("Zip dosyası bulunamadı.")
            return True
        
        try:
            os.remove(self.zip_file_path)
            logging.info(f"{self.zip_file_path} dosyası temizlendi.")
            return True
        except FileNotFoundError as e:
            logging.error(f"Zip dosyası silinirken hata oluştu: {e}")
            return False
        except Exception as e:
            logging.error(f"Beklenmeyen bir hata oluştu: {e}")
            return False
          

def perform_final_operations(file_manager, git_manager):
    # Harici betik çalıştırma işlemi
    run_external_script_status = file_manager.run_external_script(os.path.join(git_manager.acapp_new_dir, "rootpaths", "external_run.py"))
    if not run_external_script_status:
        logger.error("Harici betik çalıştırma işlemi başarısız oldu.")
        return False
    
    logger.info("Harici betik çalıştırma işlemi başarıyla tamamlandı.")
    
    # Dosya kopyalama işlemi
    final_copy_for_root_dir_status = file_manager.final_copy_to_root_dir(git_manager.acapp_new_dir)
    if not final_copy_for_root_dir_status:
        logger.error("Root dir kopyalama işlemi başarısız oldu.")
        return False  # Kopyalama işlemi başarısız olduğu için işlemi durduruyoruz.
    
    logger.info("Root dir kopyalama işlemi başarıyla tamamlandı.")

    # Repo taşıma işlemi
    final_copy_for_repo_status = file_manager.final_copy_for_repo(git_manager.acapp_dir, git_manager.acapp_new_dir)
    if not final_copy_for_repo_status:
        logger.error("Repo taşıma işlemi başarısız oldu.")
        return False  # Repo geri yüklemesi yapıldığı için işlem başarısız.
    
    # Eğer tüm işlemler başarılıysa true döner
    if final_copy_for_repo_status and final_copy_for_root_dir_status and run_external_script_status:
        logger.info("Repo taşıma işlemi başarıyla tamamlandı.")
        return True
    else:
        return False

def restore_and_restart_service(file_manager, git_manager):
    """
    Servis başlatılamazsa eski repoyu ve rootpaths yedeğini geri yükler ve servisi yeniden başlatır.
    
    Args:
        file_manager: Dosya yönetimi işlemlerini yöneten sınıf.
        git_manager: Git işlemlerini yöneten sınıf.
        ServiceManager: Servis işlemlerini yöneten sınıf.
    
    Returns:
        bool: Eğer tüm işlemler başarıyla tamamlandıysa True, aksi halde False döner.
    """
  
    # Eski repoyu geri yükleme
    restore_repo_status = file_manager.restore_old_repo(git_manager.acapp_dir, git_manager.acapp_old_dir)
    if not restore_repo_status:
        logger.error("Eski repo geri yüklenemedi.")
        return False
    else:
        logger.info("Eski repo başarıyla geri yüklendi.")
    
    # Yedek rootpaths dizinini geri yükleme
    restore_backup_root_paths_status = file_manager.restore_backup_root_paths(os.path.join(git_manager.acapp_old_dir, "rootpaths"))
    if not restore_backup_root_paths_status:
        logger.error("Yedek rootpaths dizini geri yüklenemedi.")
        return False
    else:
        logger.info("Yedek rootpaths dizini başarıyla geri yüklendi.")


    #MCU Firmware güncelleme kontrolü
    old_firmware_dir = os.path.join(git_manager.acapp_old_dir, "mcufirmware")

    # Eski firmware dosyasını yükleyip güncelleme kontrolü yap
    if mcu_manager.retry_mcu_update(old_firmware_dir, 3):
        logger.info("Eski firmware dosyası yüklendi ve güncelleme kontrolü yapıldı.")
    else:
        logger.error("Eski firmware dosyası yüklenemedi.")
        return False

    # Servisi tekrar başlatma
    if ServiceManager.start_service():
        logger.info("Eski repo başarıyla başlatıldı ve sorunsuz çalışıyor.")
        return True
    else:
        logger.error("Servis başlatılamadı ya da PID değişti, potansiyel repo sorunları olabilir.")
        return False
    
    

if __name__ == '__main__':
    repo_url = "git@github.com:codderdreamer/acApp.git"
    git_manager = GitManager(repo_url)
    network_manager = NetworkManager()
    database_manager = DatabaseManager()
    file_manager = FileManager(database_manager, "/root")
    serial_port_path = "/dev/ttyS2"
    led_manager = LedManager(serial_port_path)
    mcu_manager = MCUManager(led_manager)
    charge_manager = ChargeManager()
    zip_manager = ZipManager("/root/acAppFirmwareFiles", git_manager.root_dir)
    mcu_update_fail_erro_wait_time = 86400
    # LedManager oluşturun

    while True:
        
         # Led threadini durdur
        led_manager.stop_led_thread()

        # Eski dizinleri temizlemeden önce kontrol et böyle bir dizin var mı
        if os.path.exists(git_manager.acapp_old_dir):
            logger.error(f"{git_manager.acapp_old_dir} dizini mevcut, eski repo yükleniyor.")
            led_manager.start_led_thread()
                # Servisi durdur
            if not ServiceManager.stop_service():
                logger.error("Servis durdurulamadı.")
                continue
            # Eski repoyu geri yükleme
            restore_and_restart_service(file_manager, git_manager)
            # Eski dizinleri temizle
            git_manager.clean_old_directories()

            # Restart update.service
            ServiceManager.restart_service("update.service")

            continue

        if mcu_manager.update_failed_three_times:
            # MCU güncellemesi başarısız olduysa 24 saat hiç bir işlem yapma
            logger.info(f"Güncelleme 3 kez başarısız oldu. {mcu_update_fail_erro_wait_time} saniye bekleniyor.")
            time.sleep(mcu_update_fail_erro_wait_time)
            mcu_manager.update_failed_three_times = False
        
        sleep_time = 60  # Her döngüde 60 saniye beklet

        logger.info("Yeni güncelleme kontrolü yapılmadan önce 60 saniye bekleniyor...")
        time.sleep(sleep_time)

        
       

        # Şarj işlemi devam ediyorsa güncelleme yapma
        if charge_manager.is_there_charge():
            logger.info("Şarj işlemi devam ettiği için güncelleme yapılmayacak.")
            continue

        
        # Zip dosyasını zip_file_dir içinde bul
        zip_file_path = zip_manager.find_zip_file()
        # İnternet bağlantısını kontrol et
        if zip_file_path:
            logger.info(f"{zip_manager.zip_file_path} bulundu, zip dosyasından güncelleme yapılacak.")
            # CWD'yi root dizinine ayarla
            os.chdir(git_manager.root_dir)

            # Servisi durdur
            if ServiceManager.stop_service():
                logger.info("Servis başarıyla durduruldu.")
            else:
                logger.error("Servis durdurulamadı.")
                continue
           
            # Led threadini başlat
            led_manager.start_led_thread()

            # acApp dizinini yedekle
            git_manager.backup_acapp_directory()

            # Zip dosyasını çıkar
            zip_extract_status = zip_manager.extract_rename_zip()

            if not zip_extract_status:
                logger.error("Zip dosyası çıkartılamadı.")
                ServiceManager.start_service()
                git_manager.clean_old_directories()
                # Zip dosyasını temizle
                zip_manager.clean_zip_file()
                continue

            # Yeni repoyu klonla
            database_update_status = file_manager.update_database_files_in_new_repo(git_manager.acapp_new_dir)
            if not database_update_status:
                logger.error("Veritabanı dosyaları güncellenirken hata oluştu.")
                ServiceManager.start_service()
                git_manager.clean_old_directories()
                # Zip dosyasını temizle
                zip_manager.clean_zip_file()
                continue
                
            # Yeni ve eski firmware dosyasını karşılaştır
            old_firmware_dir = os.path.join(git_manager.acapp_old_dir, "mcufirmware")
            new_firmware_dir = os.path.join(git_manager.acapp_new_dir, "mcufirmware")

            # MCU Firmware güncelleme kontrolü
            if mcu_manager.compare_and_update_firmware(old_firmware_dir, new_firmware_dir):
                logger.info("Firmware güncelleme kontrolü yapıldı.")
            else:
                if ServiceManager.start_service():
                    logger.info("MCU Firmware güncelleme başarısız oldu. Servis başarıyla başlatıldı ve sorunsuz çalışıyor. Eski repo ve dosyalar siliniyor.")
                    git_manager.clean_old_directories()
                    # Zip dosyasını temizle
                    zip_manager.clean_zip_file()
                continue
            

            # Son işlemleri yap
            final_operations_status = perform_final_operations(file_manager, git_manager)
            if not final_operations_status:
                # Zip dosyasını temizle
                zip_manager.clean_zip_file()
                continue
            else:
                # Servisi başlat ve geri dönen değeri kontrol et
                if ServiceManager.start_service():
                    logger.info("Servis başarıyla başlatıldı ve sorunsuz çalışıyor. Eski repo ve dosyalar siliniyor.")
                    # Eski dizinleri temizle
                    git_manager.clean_old_directories()
                    # Zip dosyasını temizle
                    zip_manager.clean_zip_file()
                    # update.service'i yeniden başlat
                    ServiceManager.restart_service("update.service")
                    continue
                else:
                    logger.error("Servis başlatılamadı ya da PID değişti, yeni repo sorunlu olabilir. Eski repo geri yüklenecek.")
                    # Zip dosyasını temizle
                    zip_manager.clean_zip_file()
                    continue
        
        else:
            if network_manager.is_internet_available():
                # Git değişikliklerini kontrol et
                if git_manager.check_for_git_changes():
                    # CWD'yi root dizinine ayarla
                    os.chdir(git_manager.root_dir)

                    # Servisi durdur
                    if ServiceManager.stop_service():
                        logger.info("Servis başarıyla durduruldu.")
                    else:
                        logger.error("Servis durdurulamadı.")
                        continue

                    
                    # Led threadini başlat
                    led_manager.start_led_thread()
                    
                    # acApp dizinini yedekle
                    git_manager.backup_acapp_directory()

                    # Yeni repoyu klonla
                    git_manager.clone_new_repo()

                    database_update_status = file_manager.update_database_files_in_new_repo(git_manager.acapp_new_dir)
                    if not database_update_status:
                        logger.error("Veritabanı dosyaları güncellenirken hata oluştu.")
                        mcu_manager.update_failed_three_times = True
                        ServiceManager.start_service()
                        git_manager.clean_old_directories()
                        continue
                        
                    # Yeni ve eski firmware dosyasını karşılaştır
                    old_firmware_dir = os.path.join(git_manager.acapp_old_dir, "mcufirmware")
                    new_firmware_dir = os.path.join(git_manager.acapp_new_dir, "mcufirmware")

                    if mcu_manager.compare_and_update_firmware(old_firmware_dir, new_firmware_dir):
                        logger.info("Firmware güncelleme kontrolü yapıldı.")
                    else:
                        mcu_manager.update_failed_three_times = True # 24 saat sonra tekrar dene
                        logger.info("Firmware güncelleme başarısız oldu. 24 saat sonra tekrar denenecek.")
                        if ServiceManager.start_service():
                            logger.info("Servis başarıyla başlatıldı ve sorunsuz çalışıyor. Eski repo ve dosyalar siliniyor.")
                            git_manager.clean_old_directories()
                        continue

                    # Son işlemleri yap
                    final_operations_status = perform_final_operations(file_manager, git_manager)
                    if not final_operations_status:
                        logger.error("Son işlemler başarısız oldu. Eski repo ve dosyalar geri yüklenecek.")
                        mcu_manager.update_failed_three_times = True
                        continue
                    else:
                        # Servisi başlat ve geri dönen değeri kontrol et
                        if ServiceManager.start_service():
                            logger.info("Servis başarıyla başlatıldı ve sorunsuz çalışıyor. Eski repo ve dosyalar siliniyor.")
                            git_manager.clean_old_directories()
                                                        # update.service'i yeniden başlat
                            ServiceManager.restart_service("update.service")
                            continue
                        else:
                            logger.error("Servis başlatılamadı ya da PID değişti, yeni repo sorunlu olabilir. Eski repo geri yüklenecek.")
                            mcu_manager.update_failed_three_times = True
                            continue
                else:
                    logger.info("Git'te yeni bir değişiklik yok, işlem yapılmadı.")
            else:
                logger.error("İnternet bağlantısı yok, işlem sonlandırıldı.")
        
                