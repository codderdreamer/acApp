import subprocess
import time
import threading

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

def boot():
    threading.Thread(target=pe_10_set,daemon=True).start()
    threading.Thread(target=pe_11_set,daemon=True).start()

if __name__ == "__main__":
    boot()
    time.sleep(10)