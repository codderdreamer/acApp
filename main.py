from application import Application
import asyncio
import time




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
