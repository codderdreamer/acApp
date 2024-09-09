import builtins
from datetime import datetime
import asyncio
asyncio.current_task = asyncio.Task.current_task
import time
from src.databaseModule import DatabaseModule

file = open("/root/output.txt", "a")
original_print = builtins.print
def timestamped_print(color = "",*args, **kwargs):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args = (f"[{current_time}]",) + (color,) + args + ("\033[0m",)
    original_print(*args, **kwargs)
    # file.write(" ".join(map(str, args)) + "\n")
builtins.print = timestamped_print


class Application():
    def __init__(self, loop):
        self.databaseModule = DatabaseModule(self)


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        app = Application(loop)
    except Exception as e:
        print("__main__ Exception:", e)

    while True:
        time.sleep(100)