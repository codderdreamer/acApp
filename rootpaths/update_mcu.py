import subprocess
import time
import argparse
HARDWARE_BOOT_PIN = 11
SOFTWARE_BOOT_PIN = 13
RESET_PIN = 10


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

    def mcu_boot_mode(self):
        try:
            self.set_gpio('e', HARDWARE_BOOT_PIN, 0)
            self.set_gpio('e', RESET_PIN, 1)
            self.set_gpio('e', SOFTWARE_BOOT_PIN, 1)
            time.sleep(0.3)
            self.set_gpio('e', RESET_PIN, 0)
            time.sleep(0.5)
            self.set_gpio('e', SOFTWARE_BOOT_PIN, 0)
            time.sleep(0.1)
            self.set_gpio('e', SOFTWARE_BOOT_PIN, 1)
            time.sleep(0.1)

            self.set_gpio('e', SOFTWARE_BOOT_PIN, 0)
            time.sleep(0.1)
            self.set_gpio('e', SOFTWARE_BOOT_PIN, 1)
            time.sleep(0.1)

            self.set_gpio('e', SOFTWARE_BOOT_PIN, 0)
            time.sleep(0.1)
            self.set_gpio('e', SOFTWARE_BOOT_PIN, 1)
            time.sleep(0.1)

            self.set_gpio('e', SOFTWARE_BOOT_PIN, 0)
            time.sleep(0.1)
            self.set_gpio('e', SOFTWARE_BOOT_PIN, 1)
            time.sleep(0.1)
            
        except Exception as e:
            print(f"mcu_boot_mode hatası: {e}")

    def mcu_reset_mode(self):
        try:
            # GPIO reset işlemi
            time.sleep(0.1)
            self.set_gpio('e', RESET_PIN, 0)
            self.set_gpio('e', SOFTWARE_BOOT_PIN, 0)
            time.sleep(0.1)
            self.set_gpio('e', RESET_PIN, 1)
            time.sleep(0.5)
            self.set_gpio('e', RESET_PIN, 0)
            time.sleep(0.1)
        except Exception as e:
            print(f"mcu_reset_mode hatası: {e}")

    def update_mcu_firmware(self, firmware_path):
        """
        MCU'nun firmware'ini günceller.
        """
        try:
            print("MCU boot moduna geçiyor...")
            # MCU boot moduna geç
            self.mcu_boot_mode()

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

            # MCU reset moduna geç
            self.mcu_reset_mode()

            # Yükleme başarılı mı kontrol et
            if "File downloaded successfully" in log_output:
                print("MCU Firmware başarıyla yüklendi.")
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