import os
import fcntl
import time
import sqlite3
import subprocess
import requests
import json
import threading

'''
reset_counter 0 setle
mcu resetle

while;
    internet varsa;
        şarj işlemi varsa;
            pass
        şarj işlemi yoksa;
            git üzerinde değişiklik varsa;
                servisi durdur
                değişiklik olan dosya isimlerini al
                acApp_old olarak değiştir
                git clone yap, başarılıysa;
                    gitupdate.sh çalıştır başarılıysa;                                  # gitupdate.sh her zaman dosya içerisinde olcak, linux içerisinde indirme yada databse eklentileri gbi yerleri yazacağız
                        mcu üzerinde değişiklik varsa;
                            reset_counter 1 setle
                            update et, başarılıysa;
                                pass
                            update et, başarısızsa;
                                2 kere daha dene başarılıysa;
                                    pass
                                2 kere daha dene başarısızsa;
                                    pass
                            reset_counter 0 setle
                        mcu üzerinde değişiklik yoksa;
                            pass
                    gitupdate.sh çalıştır başarısızsa;
                        acApp sil
                        acApp_old u acApp olarak değiştir
                    servisi yeniden başlat
                git clone yap, başarısızsa;
                    acApp_old u acApp olarak değiştir
            git üzerinde değişiklik yoksa;
                pass
    internet yoksa;
        pass
        
    reset_counter 0 'dan farklıysa;
        3 e kadar dene
        3 olduğunda 0a eşitle
'''

class Update():
    def __init__(self):
        pass

    def is_there_internet(self):
        try:
            requests.get("http://www.google.com", timeout=5)
            print("internet var")
            return True
        except Exception as e:
            print("internet yok")
            return False
        
    def is_there_charge(self):
        try:
            data_dict = {}
            file = open("/root/Charge.sqlite", 'a+')
            fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            charge_database = sqlite3.connect("/root/Charge.sqlite")
            cursor = charge_database.cursor()
            query = "SELECT * FROM ev"
            cursor.execute(query)
            data = cursor.fetchall()
            for row in data:
                data_dict[row[0]] = row[1]
            if data_dict["charge"]=="True":
                print("Şarj işlemi var bekleniyor...")
                return True
            else:
                print("Şarj işlemi yok")
                return False
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return False
        except IOError as e:
            print("Dosya kilitli /root/Charge.sqlite")
            time.sleep(1)
            return self.is_there_charge()
        except Exception as e:
            print("is_there_charge Exception:", e)
            return False
        
    def create_and_write_file(counter):
        try:
            with open("/root/reset_counter.txt", "w") as file:
                file.write(str(counter))
        except Exception as e:
            print("create_and_write_file Exception:",e)

    def set_gpio(self, port, pin, value):
        command = f"gpio-test.64 w {port} {pin} {value}"
        subprocess.run(command, shell=True)

    def mcu_reset(self):
        self.set_gpio('e', 10, 0)
        self.set_gpio('e', 11, 0)
        time.sleep(0.1)
        self.set_gpio('e', 10, 1)
        time.sleep(0.5)
        self.set_gpio('e', 10, 0)

    def check_for_git_changes(self):
        try:
            os.chdir("/root/acApp")
            fetch_result = subprocess.run(['git', 'fetch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            log_result = subprocess.run(['git', 'log', 'HEAD..origin/main', '--oneline'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            log_output = log_result.stdout
            log_error = log_result.stderr
            if log_result.returncode != 0:
                print("Log error:", log_error)
            if log_output:
                print("New commits:\n", log_output)
                return True
            else:
                print("Yazılım güncel.")
                return False
        except Exception as e:
            print("check_for_git_changes An error occurred:", e)

    def stop_service(self):
        os.system("systemctl stop acapp.service")

    def start_service(self):
        os.system("systemctl restart acapp.service")

    def run(self):
        self.create_and_write_file(0)
        self.mcu_reset()
        while True:
            try:
                if self.is_there_internet():
                    if self.is_there_charge():
                        pass
                    else:
                        if self.check_for_git_changes():
                            self.stop_service()

                        else:
                            pass
                else:
                    pass

            except Exception as e:
                print("run Exception:",e)
            time.sleep(10)

if __name__ == '__main__':
    try:
        Update().run()
    except Exception as e:
        print("__main__ Exception",e) 