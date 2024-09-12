from src.enums import *

class DeviceStateModule():
    def __init__(self,application) -> None:
        self.application = application
        self.__cardType : CardType = None

    @property
    def cardType(self):
        return self.__cardType

    @cardType.setter
    def cardType(self, value):
        if self.__cardType != value:
            print(Color.Macenta.value, "CardType:", value)