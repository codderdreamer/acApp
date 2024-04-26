import asyncio
from datetime import datetime
import time
from src.application import Application

    
if __name__ == "__main__":
    try:
        print(" ----------------------------- Hera Charge AC Application is Starting ----------------------------- ")
        loop = asyncio.get_event_loop()
        app = Application(loop)
    except Exception as e:
        print(datetime.now(),"__main__ Exception:",e)
    while True:
        time.sleep(5)
