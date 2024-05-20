
from threading import Thread
from functools import wraps
import uvicorn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from fastapi import FastAPI
import time
import sqlite3
import subprocess

class Settings(BaseSettings):
    OPENAPI_URL: str = ""
    model_config = SettingsConfigDict(
        env_file=".env.prod", env_file_encoding="utf-8",case_sensitive=True
    )
    
class Heartbeat(BaseModel):
    Status : str = None
    
class ChargePointId(BaseModel):
    id : str = None
    
    
    
class TestServer():
    def __init__(self,application) -> None:
        self.application = application
        # self.db_path = "/root/Settings.sqlite"
        self.db_path = "Settings.sqlite"
        self.app = FastAPI(openapi_url=Settings().OPENAPI_URL)
        self.app.post("/heartbeat")(self.heartbeat_post)
        self.app.post("/chargePointId")(self.chargePointId_post)
        self.app.get("/wifimac")(self.wifimac_get)
        Thread(target=self.run,daemon=True).start()

    async def heartbeat_post(self, heartbeat : Heartbeat):
        print(heartbeat)
        return "OK"
    
    async def chargePointId_post(self, chargePointId : ChargePointId):
        print(chargePointId)
        try:
            self.settings_database = sqlite3.connect(self.db_path)
            self.cursor = self.settings_database.cursor()
            query = "UPDATE ocpp_settings SET key = ? WHERE value = ?"
            value = (chargePointId.id,"chargePointId")
            self.cursor.execute(query,value)
            self.settings_database.commit()
            self.settings_database.close()
        except Exception as e:
            print(e)
        return "OK"
    
    async def wifimac_get(self):
        try:
            result = subprocess.run(['getmac'], capture_output=True, text=True)
            output = result.stdout
            for line in output.splitlines():
                if 'Wi-Fi' in line:
                    print(line.split()[0]) 
                    return line.split()[0]
        except Exception as e:
            print(e)
        return "OK"
    
    def run(self):
        uvicorn.run(self.app, port=5000,host="0.0.0.0")
        
# test = TestServer(None)
# while True:
#     time.sleep(1)