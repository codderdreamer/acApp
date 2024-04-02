import requests

response = requests.get("https://api.heracharge.com/firmware/uploads/1712068754156-312214834-firmware.zip")
if response.status_code == 200:
    filename = "/root/new_firmware.zip"
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"'{filename}' başarıyla indirildi.")