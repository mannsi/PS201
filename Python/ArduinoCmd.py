import serial
import time

print("--Scanning for available USB ports--")

for i in range(256):
  try:
    s = serial.Serial(i)
    print(" Port number: %s" % i, " (%s)" % s.portstr)
    s.close()
  except serial.SerialException:
    pass

portNumberString = input('Select the port number you wish to use: ')
portNumberInt = int(portNumberString)

try:
  connection = serial.Serial(portNumberInt, timeout = 2)
  while True:
    readValue = connection.read()
    if readValue:
      print("Got value: %s" % readValue)
    else:
      print("Got no value")
    time.sleep(1)
except Exception as ex:
    print("Error!. Error message: %s" % ex)
