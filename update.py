import os
import fcntl
import os
import time
import sqlite3
import subprocess

def check_for_git_changes():
    try:
        # İlk olarak doğru dizine git
        subprocess.run(["cd", "/root/acApp"])

        # Sonra Git status komutu ile repo durumunu kontrol et
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
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
        f = open(file_path, 'a+')
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print("Dosya kilitli değil")
        
        charge_database = sqlite3.connect('/root/Charge.sqlite')
        cursor = charge_database.cursor()
        query = "SELECT * FROM ev"
        cursor.execute(query)
        data = cursor.fetchall()
        charge_database.close()
        for row in data:
            data_dict[row[0]] = row[1]
        print("Charge:",data_dict["charge"])
        return data_dict["charge"] == "True"
    except IOError as e:
        print("Dosya kilitli")
        time.sleep(1)
        is_there_charge()

while True:
    try:
        # Devam eden bir şarj var mı?
        if is_there_charge():
            pass # işlem yapma bekle
        # Devam eden bir şarj yoksa;
        else:
            # internet var mı?
            
            if check_for_git_changes():
                print("Git üzerinde değişiklik var! Update yapılacak")
            else:
                print("Git üzerinde bir değişiklik yok...")
            
        
        
        
    except Exception as e:
        print("Exception:",e)
        
    time.sleep(5)



