import serial

ser = serial.Serial('COM10', baudrate= 115200)

while True:
    line = ser.readline()
    decoded_line = line.decode('utf-8')
    print(decoded_line)






