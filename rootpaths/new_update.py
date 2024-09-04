import os
import fcntl
import time
import sqlite3
import subprocess
import requests
import json
import threading

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

def check_for_mcu_change():
    try:
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
                return True, bin_files[0]
            else:
                print("No .bin files changed.")
                return False, ""
    except Exception as e:
        print("check_for_mcu_change An error occurred:", e)

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
    
def update_firmware():
    try:
        create_and_write_file(0)
        os.system("git pull")
    except Exception as e:
        print("updade_firmware Exception:",e)

def update_mcu_firmware(firmware_name):
    try:
        print("MCU boot moduna geçiyor...")
        threading.Thread(target=pe_10_set,daemon=True).start()
        threading.Thread(target=pe_11_set,daemon=True).start()
        path = "/root/acApp/mcufirmware/" + firmware_name
        print("firmware path",path)
        time.sleep(10)
        print("MCU güncelleniyor...")
        run_command = "dfu-util -a 0 -s 0x08020000:leave -D " + path
        log_result = subprocess.run(['dfu-util', '-a', '0', '-s', '0x08020000:leave', '-D', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        log_output = log_result.stdout
        print("log_output",log_output)
        time.sleep(0.1)
        set_gpio('e', 10, 0)
        set_gpio('e', 11, 0)
        time.sleep(0.1)
        set_gpio('e', 10, 1)
        time.sleep(0.5)
        set_gpio('e', 10, 0)
        if "File downloaded successfully" in log_output:
            return True
        else:
            return False
        # log_error = log_result.stderr
        # if log_result.returncode != 0:
        #     print("Log error:", log_error)
        #     return False
        # return True
    except Exception as e:
        print("update_mcu_firmware Exception:",e)

def create_and_write_file(counter):
    try:
        with open("/root/reset_counter.txt", "w") as file:
            file.write(str(counter))
    except Exception as e:
        print("create_and_write_file Exception:",e)

def read_file():
    try:
        with open("/root/reset_counter.txt", "r") as file:
            content = file.read()
        return content
    except Exception as e:
        print("read_file Exception:",e)

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
    
def set_gpio(port, pin, value):
    command = f"gpio-test.64 w {port} {pin} {value}"
    subprocess.run(command, shell=True)

def pe_10_set():
    set_gpio('e', 10, 1)
    set_gpio('e', 11, 1)
    time.sleep(0.3)
    set_gpio('e', 10, 0)

def pe_11_set():
    time.sleep(0.5)
    set_gpio('e', 11, 0)
    time.sleep(0.1)
    set_gpio('e', 11, 1)
    time.sleep(0.1)

    set_gpio('e', 11, 0)
    time.sleep(0.1)
    set_gpio('e', 11, 1)
    time.sleep(0.1)

    set_gpio('e', 11, 0)
    time.sleep(0.1)
    set_gpio('e', 11, 1)
    time.sleep(0.1)

    set_gpio('e', 11, 0)
    time.sleep(0.1)
    set_gpio('e', 11, 1)
    time.sleep(0.1)

def find_name_bin_file():
    try:
        files_and_dirs = os.listdir("/root/acApp/mcufirmware")
        bin_files = [f for f in files_and_dirs if f.endswith('.bin')]
        if len(bin_files)>0:
            return bin_files[0]
    except Exception as e:
        print("list_bin_files Exception:",e)


charge = False
there_is_change = False
set_gpio('e', 10, 0)
set_gpio('e', 11, 0)
time.sleep(0.1)
set_gpio('e', 10, 1)
time.sleep(0.5)
set_gpio('e', 10, 0)
create_and_write_file(0)

# firmware_name = find_name_bin_file()
# update_mcu_firmware(firmware_name)

# time.sleep(100)

while True:
    try:
        counter = int(read_file())
        if counter != 0 and counter < 5:
            print(f"{counter + 1}. ye deneniyor ")
            firmware_name = find_name_bin_file()
            if firmware_name != None:
                if update_mcu_firmware(firmware_name) == False:
                    create_and_write_file(counter + 1)
                else:
                    create_and_write_file(0)
            else:
                create_and_write_file(0)
        if counter == 5:
            create_and_write_file(0)
            system_restart()

        if is_there_internet():
            charge = is_there_charge()
            if charge == False:
                ensure_repository()
                there_is_change = check_for_git_changes()
            if there_is_change == True:
                mcu_firmware_changed, firmware_name = check_for_mcu_change()
                update_firmware()
                create_and_write_file(1)
                if mcu_firmware_changed:
                    if update_mcu_firmware(firmware_name) == False:
                        if int(read_file()) == 1:
                            create_and_write_file(2)
                            print("Reboot ediliyor")
                            # os.system("reboot")
                    else:
                        create_and_write_file(0)
                            
                system_restart()
    except Exception as e:
        print("Exception:", e)

    time.sleep(5)
    

