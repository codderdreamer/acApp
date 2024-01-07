import asyncio
from src.chargePoint16 import ChargePoint16
import websockets
import time
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16 import call_result
from ocpp.v16.enums import *
from ocpp.routing import *

class EnsureFutures():
    def __init__(self,application) -> None:
        self.application = application
        
    def on_status_notification(self,
                                connector_id:int,
                                error_code: ChargePointErrorCode,
                                status: ChargePointStatus,
                                info: str = None,
                                vendor_id: str = None,
                                vendor_error_code: str = None):
        '''
        connector_id: int
        error_code: ChargePointErrorCode
        status: ChargePointStatus
        info: Optional[str] = None
        vendor_id: Optional[str] = None
        vendor_error_code: Optional[str] = None
        '''
        return asyncio.ensure_future(self.application.chargePoint.send_status_notification(connector_id,error_code,status,info,vendor_id,vendor_error_code))
        
        
        
        


    def on_authorize(self,id_tag):
        return asyncio.ensure_future(self.application.chargePoint.send_authorize(id_tag))