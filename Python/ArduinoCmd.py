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

  command = int(input("USB connected. Now what motherfucker ?\n\t1 = Write voltage\n\t2 = Read voltage\n\t3 = Turn on output\n\t4 = Turn off output\n\t5 = Exit \n: "))
  while command is not 5:
    if command == 1:
      voltage = int(input("What is the target voltage you want ? : "))

      connection.write(0xC0)
      connection.write(voltage)
    elif command == 2:
      print("Reading voltage")
      connection.write(0xD0)
      while connection.inWaiting() > 0:
        voltageValue = connection.readline()
      if voltageValue:
        print("Got value: %s" % voltageValue)
      else:
        print("Got no value")
    elif command == 3:
      print("Not sure what should happen here")
    elif command == 4:
      print("Not sure what should happen here")
    else:
      print("Invalid input, dumbass")

    command = int(input("Again ?\n\t1 = Write voltage\n\t2 = Read voltage\n\t3 = Turn on output\n\t4 = Turn off output\n\t5 = Exit \n: "))

except Exception as ex:
  print("Error!. Error message: %s" % ex)


