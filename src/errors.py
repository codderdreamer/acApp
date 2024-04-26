import time
from threading import Thread

class Errors():
    def __init__(self, application) -> None:
        from src.application import Application
        self.application : Application = application
        self.connected_database = True                  # Bağlanamazsa False
        self.connected_bluetooth = False
        self.network_connected = False
        self.mid_meter_connected = False
        Thread(target=self.control_errors,daemon=True).start()
        
    def control_errors(self):
        while True:
            print("self.connected_database",self.connected_database)
            print("self.connected_bluetooth",self.connected_bluetooth)
            print("self.network_connected",self.network_connected)
            print("self.mid_meter_connected",self.mid_meter_connected)
            time.sleep(5)