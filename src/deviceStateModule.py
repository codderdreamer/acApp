from src.enums import *

class DeviceStateModule():
    def __init__(self,application) -> None:
        self.application = application

        self.cardType : CardType = None