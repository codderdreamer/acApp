import subprocess
import threading
import time
import argparse


class MCUManager:
    """
    MCU güncellemeleri için yardımcı sınıf.
    """
    def __init__(self):
        self.update_failed_three_times = False

    def set_gpio(self, port, pin, value):
        try:
            command = f"gpio-test.64 w {port} {pin} {value}"
            subprocess.run(command, shell=True, check=True)
            print(f"{command}")
        except subprocess.CalledProcessError as e:
            print(f"GPIO ayarlanırken hata: {e}")

    def pe_10_set(self):
        try:
            self.set_gpio('e', 10, 1)
            self.set_gpio('e', 11, 1)
            time.sleep(0.3)
            self.set_gpio('e', 10, 0)
        except Exception as e:
            print(f"pe_10_set hatası: {e}")

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
            print(f"pe_11_set hatası: {e}")

    def update_mcu_firmware(self, firmware_path):
        """
        MCU'nun firmware'ini günceller.
        """
        try:
            print("MCU boot moduna geçiyor...")
            # GPIO ayarları için ayrı thread'ler başlat
            threading.Thread(target=self.pe_10_set, daemon=True).start()
            threading.Thread(target=self.pe_10_set, daemon=True).start()

            print(f"Firmware yolu: {firmware_path}")

            # MCU güncellemesi için 10 saniye bekle
            time.sleep(10)

            print("MCU güncelleniyor...")

            # Firmware yükleme komutu
            command = ['dfu-util', '-a', '0', '-s', '0x08020000:leave', '-D', firmware_path]
            log_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            print(f"{command}")
            log_output = log_result.stdout
            print(f"Firmware update log: {log_output}")

            # GPIO reset işlemi
            time.sleep(0.1)
            self.set_gpio('e', 10, 0)
            self.set_gpio('e', 11, 0)
            time.sleep(0.1)
            self.set_gpio('e', 10, 1)
            time.sleep(0.5)
            self.set_gpio('e', 10, 0)

            # Yükleme başarılı mı kontrol et
            if "File downloaded successfully" in log_output:
                print("Firmware başarıyla yüklendi.")
                return True
            else:
                print("Firmware yüklenirken bir hata oluştu.")
                return False

        except Exception as e:
            print(f"update_mcu_firmware hatası: {e}")
            return False



def main():
    # Komut satırı argümanlarını işlemek için argparse kullanıyoruz
    parser = argparse.ArgumentParser(description="MCU Firmware güncelleme aracı.")
    
    # Firmware dosya yolunu alacak -f veya --firmware parametresi
    parser.add_argument('-f', '--firmware', type=str, required=True, help="Güncellenecek firmware dosyasının yolu.")
    
    # Argümanları işle
    args = parser.parse_args()

    # MCUManager nesnesi oluştur
    mcu_manager = MCUManager()

    # Firmware güncelleme işlemini başlat
    if mcu_manager.update_mcu_firmware(args.firmware):
        print("MCU firmware güncellemesi başarıyla tamamlandı.")
    else:
        print("MCU firmware güncellemesi başarısız oldu.")

if __name__ == "__main__":
    main()