import os
import fcntl
import time
import sqlite3
import subprocess

def check_for_git_changes():
    try:
        # Doğru dizine gitmek için os.chdir kullan
        os.chdir("/root/acApp")
        # Git status komutunu çalıştır
                # Git fetch komutunu çalıştır
        fetch_result = subprocess.run(['git', 'fetch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        # Yeni commit'leri kontrol etmek için git log komutunu çalıştır
        log_result = subprocess.run(['git', 'log', 'HEAD..origin/main', '--oneline'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        log_output = log_result.stdout
        log_error = log_result.stderr
        
        if log_result.returncode != 0:
            print("Log error:", log_error)
            return
        
        if log_output:
            print("New commits:\n", log_output)
        else:
            print("No new commits.")
    except Exception as e:
        print("check_for_git_changes An error occurred:", e)
        # return True

def is_there_charge():
    file_path = "/root/Charge.sqlite"
    try:
        data_dict = {}
        with open(file_path, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            print("Dosya kilitli değil")
            
            with sqlite3.connect(file_path) as charge_database:
                cursor = charge_database.cursor()
                query = "SELECT * FROM ev"
                cursor.execute(query)
                data = cursor.fetchall()
                
                for row in data:
                    data_dict[row[0]] = row[1]
                
                print("Charge:", data_dict.get("charge", "False"))
                return data_dict.get("charge", "False") == "True"
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
    except IOError as e:
        print("Dosya kilitli")
        time.sleep(1)
        return is_there_charge()

while True:
    try:
        # Devam eden bir şarj var mı?
        if is_there_charge():
            pass # işlem yapma bekle
        else:
            # Git üzerinde değişiklik var mı kontrol et
            check_for_git_changes()
            #     print("Git üzerinde değişiklik var! Update yapılacak")
            # else:
            #     print("Git üzerinde bir değişiklik yok...")
    except Exception as e:
        print("Exception:", e)
        
    time.sleep(5)
    


