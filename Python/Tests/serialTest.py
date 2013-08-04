import serial
import sys
import time


portNumber = 2
baudRate = 9600
timeOut = 2
"""
print("Waiting for arduino")
ser = serial.Serial(portNumber, baudRate, timeout = timeOut)
while True:
    try:
      readValue = ser.readline()
      if readValue:
        print(readValue)
        break
      else:
        print("Nothing")
        break
    except:
      print("Unexpected error:", sys.exc_info()[0])

print("Now we write to the Arduino")
ser.write(1)
print("Done writing")
print("Lets see if we can read a response from the Arduino")
time.sleep(2)
while True:
    readValue = ser.readline()
    if readValue:
      print(readValue)
      break
print("Closing the connection")
ser.close()
"""
def test1(ser):
  deviceWriteRealVoltage = 8

  data = bytearray(3)
  data[0] = 17
  data[1] = deviceWriteRealVoltage
  data[2] = 0

  try:
    ser.write(data)
  except:
    print("Unexpected error:", sys.exc_info()[0])

 # time.sleep(5)

  print("Now we try to read the response")

  try:
    #ser = serial.Serial(portNumber, 9600, timeout=2)
    readValue = ser.read()
    print(readValue)

  except:
    print("Unexpected error:", sys.exc_info()[0])

ser = serial.Serial(portNumber, baudrate = baudRate, timeout=timeOut)
handshake = ser.read()
print("handshake ", handshake)
test1(ser)
test1(ser)
test1(ser)
test1(ser)

