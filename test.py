stx = b'\x02'

stx = int.from_bytes(stx, "big")


data = "GC0011"
# result = stx + data
checksum = 2



for i in data:
    checksum += ord(i)
checksum = checksum%256
checksum = str(checksum)
lenght = len(checksum)
if lenght < 3:
    for i in  range(0,3-lenght):
        checksum = "0" + checksum

print(checksum)
c = checksum.encode('utf-8')

bytes_object = b'\x02GC0011078\n'
decoded_string = bytes_object.decode('utf-8')

print()



hex_list = [0x03,0x47,0x43,0x30,0x30,
            0x31,0x31,0x30,0x37,
            0x39,0x0A]
data = bytes(hex_list)
print(data)








# # start_of_text = 3
# # bytes_val = start_of_text.to_bytes(1, 'big') 
# G = "G".encode("utf-8")
# C = "C".encode("utf-8")
# data = 1
# data = data.to_bytes(3, 'big') 
# connector_no = 1
# connector_no_bytes = connector_no.to_bytes(1, 'big') 
# check_1 = 0
# check_1_bytes = check_1.to_bytes(1, 'big') 
# check_2 = 7
# check_2_bytes = check_2.to_bytes(1, 'big') 
# check_3 = 9
# check_3_bytes = check_3.to_bytes(1, 'big') 
# # lf = 10
# # lf_bytes = lf.to_bytes(1, 'big') 

# sent_data = G + C + data + connector_no_bytes + check_1_bytes + check_2_bytes + check_3_bytes


# a = b'3GC001107910'
# print(type(a))


# import json
# # import serial
# # from time import sleep

# # ser = serial.Serial ("/dev/ttyS0", 9600)    #Open port with baud rate
# # while True:
# #     received_data = ser.read()              #read serial port
# #     sleep(0.03)
# #     data_left = ser.inWaiting()             #check for remaining byte
# #     received_data += ser.read(data_left)
# #     print (received_data)                   #print received data
# #     ser.write(received_data)                #transmit data serially 


# SendJson = {'Command':'SERIAL_NUMBER','Data':"dfgd"}
# a = json.dumps(SendJson,indent=4).encode()
# b = a.decode('utf-8')

# json_object = json.loads(a)
# print("")