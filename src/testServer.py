from threading import Thread
import asyncio
import uvicorn
from pydantic import BaseSettings, BaseModel
from fastapi import FastAPI
import time
import sqlite3
import subprocess

class Settings(BaseSettings):
    OPENAPI_URL: str = ""

    class Config:
        env_file = ".env"

class Heartbeat(BaseModel):
    Status: str = None

class ChargePointId(BaseModel):
    id: str = None

class TestServer:
    def __init__(self, application) -> None:
        self.application = application
        self.db_path = "/root/Settings.sqlite"
        self.app = FastAPI(openapi_url=Settings().OPENAPI_URL)
        self.app.post("/heartbeat")(self.heartbeat_post)
        self.app.post("/chargePointId")(self.chargePointId_post)
        self.app.get("/wifimac")(self.wifimac_get)

    async def heartbeat_post(self, heartbeat: Heartbeat):
        print(heartbeat)
        return "OK"

    async def chargePointId_post(self, chargePointId: ChargePointId):
        print(chargePointId)
        try:
            self.settings_database = sqlite3.connect(self.db_path)
            self.cursor = self.settings_database.cursor()
            query = "UPDATE ocpp_settings SET key = ? WHERE value = ?"
            value = (chargePointId.id, "chargePointId")
            self.cursor.execute(query, value)
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

    async def start_uvicorn(self):
        print("******************start_uvicorn")
        config = uvicorn.Config(self.app, host="0.0.0.0", port=5000)
        server = uvicorn.Server(config)
        await server.serve()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.start_uvicorn())
        loop.run_forever()