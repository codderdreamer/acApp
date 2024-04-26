

class Errors():
    def __init__(self, application) -> None:
        from src.application import Application
        self.application : Application = application
        self.connected_database = True                  # Bağlanamazsa False
        self.connected_bluetooth = False
        self.network_connected = False
        self.mid_meter_connected = False