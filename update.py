import os
import fcntl
import time
import sqlite3
import subprocess

def check_for_git_changes():
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
            print("No new commits.")
            return False
    except Exception as e:
        print("check_for_git_changes An error occurred:", e)
        # burada hataya düşerse ne olcak?

def is_there_charge():
    file_path = "/root/Charge.sqlite"
    try:
        data_dict = {}
        with open(file_path, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # print("Dosya kilitli değil")
            with sqlite3.connect(file_path) as charge_database:
                cursor = charge_database.cursor()
                query = "SELECT * FROM ev"
                cursor.execute(query)
                data = cursor.fetchall()
                for row in data:
                    data_dict[row[0]] = row[1]
                return data_dict["charge"]=="True"
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
    except IOError as e:
        print("Dosya kilitli")
        time.sleep(1)
        return is_there_charge()
    except Exception as e:
        print("is_there_charge Exception:", e)
        return is_there_charge()
    
def updade_firmware():
    os.system("pwd")
    print("pwd")

charge = False
there_is_change = False
while True:
    try:
        
        charge = is_there_charge()
        if charge == False:
            there_is_change = check_for_git_changes()
        if there_is_change == True:
            updade_firmware()

    except Exception as e:
        print("Exception:", e)
        
    time.sleep(5)
    


