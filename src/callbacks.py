


class OcppCallbacks():
    def __init__(self,application) -> None:
        self.application = application
    


    def on_authorize_callback(self,future):
        result = future.result()
        print(result)
