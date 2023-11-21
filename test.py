import json
# import serial
# from time import sleep

# ser = serial.Serial ("/dev/ttyS0", 9600)    #Open port with baud rate
# while True:
#     received_data = ser.read()              #read serial port
#     sleep(0.03)
#     data_left = ser.inWaiting()             #check for remaining byte
#     received_data += ser.read(data_left)
#     print (received_data)                   #print received data
#     ser.write(received_data)                #transmit data serially 


SendJson = {'Command':'SERIAL_NUMBER','Data':"dfgd"}
a = json.dumps(SendJson,indent=4).encode()
b = a.decode('utf-8')

json_object = json.loads(a)
print("")