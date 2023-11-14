import json

class Config():
    def __init__(self):
        self.config_writed = False
        self.charge_point_model = None
        self.charge_point_vendor = None
        self.charge_point_id = None
        self.ocpp_server_url = None
        data = self.read_config_file()
        self.write_config_to_variables(data)
        self.config_writed = True

    def read_config_file(self):
        data = None
        try:
            with open("config.json", "r") as jsonfile:
                data = json.load(jsonfile)
                print("Config file readed successful")  
        except Exception as e:
            print("Config file cannot read!: ",e)
        return data
    
    def write_config_to_variables(self,data):
        self.charge_point_model = data["charge_point_model"]
        self.charge_point_vendor = data["charge_point_vendor"]
        self.charge_point_id = data["charge_point_id"]
        self.ocpp_server_url = data["ocpp_server_url"]