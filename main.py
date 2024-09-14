from application import Application
import asyncio
import time

import signal

def shutdown_handler(signum, frame):
    with open('/path/to/your/file.txt', 'a') as f:
        f.write('Sistem kapanıyor...\n')

# SIGTERM sinyalini yakala
signal.signal(signal.SIGTERM, shutdown_handler)



if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
        app.run()
        # app.ocpp_task()
    except Exception as e:
        print("__main__ Exception:", e)
    while True:
        time.sleep(5)
