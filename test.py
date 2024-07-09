import subprocess
import time
import threading

def set_gpio(port, pin, value):
    command = f"gpio-test.64 w {port} {pin} {value}"
    subprocess.run(command, shell=True)

def main():
    # Linux kartı ilk açıldığında E 10 portu 1 de duracak, E 11 portu 0'a set edilecek
    set_gpio('e', 10, 0)
    set_gpio('e', 11, 0)

    # 2 saniye boyunca bekle
    time.sleep(2)

    # E 10 1, E 11 1 olacak
    set_gpio('e', 11, 1)

    # 500ms bekle
    time.sleep(0.5)

    # E 10 0, E 11 1 olacak
    set_gpio('e', 10, 1)

    # 300ms bekle
    time.sleep(0.3)

    # E 10 1 olacak
    set_gpio('e', 10, 0)

    # 300ms bekle
    time.sleep(0.3)

    # 100ms aralıklarla toplam 4 kez E 11 ard arda 0 ve 1 olacak
    for _ in range(4):
        set_gpio('e', 11, 0)
        time.sleep(0.1)
        set_gpio('e', 11, 1)
        time.sleep(0.1)

    set_gpio('e', 11, 0)




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