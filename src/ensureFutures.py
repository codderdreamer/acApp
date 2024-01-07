import asyncio
from src.chargePoint16 import ChargePoint16
import websockets
import time

class EnsureFutures():
    def __init__(self,application) -> None:
        self.application = application


    def on_authorize(self,id_tag):
        return asyncio.ensure_future(self.application.chargePoint.send_authorize(id_tag))