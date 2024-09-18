import sys

def main():
    #check if the number of arguments
    if len(sys.argv) != 3:
        print("Kullanım: python3 run_external.py old_firmware_version new_firmware_version")
        sys.exit(1)
    old_firmware_version = sys.argv[1]
    new_firmware_version = sys.argv[2]
    print("run_external.py" + old_firmware_version + "ve " + new_firmware_version + "firmware versiyonlarıyla çalıştırıldı")

    #create a new file at /root/external_run.log
    with open("/root/external_run.log", "w") as f:
        f.write("run_external.py " + old_firmware_version + " ve " + new_firmware_version + " firmware versiyonlarıyla çalıştırıldı\n")
    
    #exit with status code 0
    sys.exit(0)

if __name__ == "__main__":
    main()