import os
import fcntl
import time
import sqlite3
import subprocess
import requests
import json

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
            diff_result = subprocess.run(['git', 'diff', '--name-only', 'HEAD', 'origin/main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            diff_output = diff_result.stdout
            diff_error = diff_result.stderr
            if diff_result.returncode != 0:
                print("Diff error:", diff_error)
            if diff_output:
                print("Changed files:\n", diff_output)
                bin_files = [line for line in diff_output.splitlines() if line.endswith('.bin')]
                if bin_files:
                    print("bin_files",bin_files)
                else:
                    print("No .bin files changed.")
            return True
        else:
            print("No new commits.")
            return False
    except Exception as e:
        print("check_for_git_changes An error occurred:", e)

def is_there_charge():
    file_path = "/root/Charge.sqlite"
    try:
        data_dict = {}
        with open(file_path, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
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
    try:
        os.system("git pull")
    except Exception as e:
        print("updade_firmware Exception:",e)

def system_restart():
    try:
        os.system("systemctl restart acapp.service")
    except Exception as e:
        print("system_restart Exception:",e)

def clone_repository():
    try:
        os.chdir("/root")
        subprocess.run(['git', 'clone', 'git@github.com:codderdreamer/acApp.git'], check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to clone the repository:", e)

def ensure_repository():
    try:
        if not os.path.exists("/root/acApp"):
            print("Repository not found, cloning...")
            clone_repository()
            # clone yaptıktan sonra database'lerin açılıp açılmadığını kontrol et, açılmıyorsa kalıcı default database dönüştür.
        else:
            print("Repository found.")
    except Exception as e:
        print("ensure_repository Exception:",e)

def is_there_internet():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        return True
    except Exception as e:
        print("is_there_internet Exception:",e)
        return False
    
def read_mcu_firmware_version():
    try:
        with open("/root/version.json", "r") as file:
            data = json.load(file)
            print("data",data)
            files_and_dirs = os.listdir("/root/acApp")
            bin_files = [f for f in files_and_dirs if f.endswith('.bin')]
            for bin_file in bin_files:
                print(bin_file)

    except Exception as e:
        print("read_mcu_firmware_version Exception:",e)

charge = False
there_is_change = False
while True:
    try:
        # read_mcu_firmware_version()
        if is_there_internet():
            charge = is_there_charge()
            if charge == False:
                ensure_repository()
                there_is_change = check_for_git_changes()
            if there_is_change == True:
                updade_firmware()
                
                # system_restart()
    except Exception as e:
        print("Exception:", e)

    time.sleep(5)
    


