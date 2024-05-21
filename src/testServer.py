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
            result = subprocess.run(['ip', 'link'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output = result.stdout
            for line in output.splitlines():
                if 'wl' in line:  # 'wl' is a common prefix for Wi-Fi interfaces, adjust if necessary
                    interface = line.split()[1].strip(':')
                    mac_result = subprocess.run(['cat', f'/sys/class/net/{interface}/address'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    mac_address = mac_result.stdout.strip()
                    print(mac_address)
                    return mac_address
        except Exception as e:
            print(e)
        return "Error"

    async def start_uvicorn(self,loop):
        logging_config = {
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {
                        "default": {
                            "()": "uvicorn.logging.DefaultFormatter",
                            "fmt": "%(levelprefix)s %(message)s",
                            "use_colors": None,
                        },
                    },
                    "handlers": {
                        "default": {
                            "formatter": "default",
                            "class": "logging.StreamHandler",
                            "stream": "ext://sys.stdout",
                        },
                    },
                    "loggers": {
                        "uvicorn": {
                            "handlers": ["default"],
                            "level": "WARNING",  # Change this to WARNING to suppress INFO logs
                        },
                        "uvicorn.error": {
                            "handlers": ["default"],
                            "level": "WARNING",
                            "propagate": True,
                        },
                        "uvicorn.access": {
                            "handlers": ["default"],
                            "level": "WARNING",
                            "propagate": False,
                        },
                    },
                }
        print("******************start_uvicorn")
        config = uvicorn.Config(self.app, host="0.0.0.0", port=5000, loop=loop, log_config=logging_config)
        server = uvicorn.Server(config)
        await server.serve()

    def run(self,loop):
        loop.create_task(self.start_uvicorn(loop))
        loop.run_forever()