import asyncio
import ssl
import websockets
from base64 import b64encode, b64decode
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.routing import on
from ocpp.v16.enums import RegistrationStatus

class ChargePoint(cp):
    @on('BootNotification')
    async def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        return call_result.BootNotification(
            current_time="2023-01-01T00:00:00Z",
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on('StatusNotification')
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        print(f"StatusNotification received: connector_id={connector_id}, error_code={error_code}, status={status}")
        return call_result.StatusNotification()

async def on_connect(websocket, path):
    # Authorization kontrolü
    request_headers = websocket.request_headers
    auth_header = request_headers.get("Authorization")

    if not auth_header:
        print("Authorization header missing")
        await websocket.close()
        return

    auth_type, auth_credentials = auth_header.split()
    if auth_type != "Basic":
        print("Unsupported authorization method")
        await websocket.close()
        return

    decoded_credentials = b64decode(auth_credentials).decode("utf-8")
    charge_point_id, password = decoded_credentials.split(":")

    expected_password = "your_password"  # Gerçek şifrenizi burada belirleyin
    if password != expected_password:
        print("Authorization failed")
        await websocket.close()
        return

    # Doğru Authorization ile bağlantı kurma
    charge_point = ChargePoint(charge_point_id, websocket)
    await charge_point.start()

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile='combined.pem')

start_server = websockets.serve(
    on_connect,
    '0.0.0.0',  # WSL içindeki tüm IP adreslerinde dinlemek için
    9000,
    ssl=ssl_context
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()