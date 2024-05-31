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
        result = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output = result.stdout

        # Değişiklik var mı kontrol et
        if "nothing to commit, working tree clean" in output:
            print("No changes in the repository.")
            return False
        else:
            print("There are changes in the repository.")
            return True
    except Exception as e:
        print("check_for_git_changes An error occurred:", e)
        return True

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
            if check_for_git_changes():
                print("Git üzerinde değişiklik var! Update yapılacak")
            else:
                print("Git üzerinde bir değişiklik yok...")
    except Exception as e:
        print("Exception:", e)
        
    time.sleep(5)
