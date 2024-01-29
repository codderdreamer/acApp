import sqlite3
import time
from ocpp.v16.enums import *
from datetime import datetime

local_list = ["123","23434"]

settings_database = sqlite3.connect('Settings.sqlite')
cursor = settings_database.cursor()
cursor.execute('DELETE FROM local_list;')
settings_database.commit()
for idTag in local_list:
    query = '''INSERT INTO local_list (idTag) VALUES (?);'''
    cursor.execute(query, (idTag,))
    settings_database.commit()

settings_database.close()



settings_database = sqlite3.connect('Settings.sqlite')
cursor = settings_database.cursor()
query = "SELECT * FROM local_list"
cursor.execute(query)
data = cursor.fetchall()
settings_database.close()
print("\n get_local_list",data)
for id in data:
    print(id[0])
