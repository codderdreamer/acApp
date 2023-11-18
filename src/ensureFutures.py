import asyncio

class EnsureFutures():
    def __init__(self,application) -> None:
        self.application = application

    def on_authorize(self,id_tag):
        return asyncio.ensure_future(self.application.chargePoint.send_authorize(id_tag))