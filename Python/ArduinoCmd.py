import serial
import time
import struct

port='/dev/ttyUSB1'
print("--Selecting USB port %s--" % port)

greetings = "USB connected. Now what motherfucker ?\n"
directions = "\t1 = Set voltage\n\t2 = Read voltage\n\t3 = Set current\n\t4 = Read current\n\t5 = Turn on output\n\t6 = Turn off output\n\t7 = Read input voltage\n\t8 = Read preregulator voltage\n\t9 = Exit \n: "

try:
  connection = serial.Serial(port, timeout = 2)
  print(greetings)
  command = int(input(directions))
  while command is not 9:
    if command == 1:
      voltage = float(input("What is the target voltage you want ? : "))
      voltage = int(voltage * 100)
      connection.write("C0".decode('hex'))
      connection.write(struct.pack(">H",voltage))
    elif command == 2:
      print("Reading voltage")
      connection.write("D0".decode('hex'))
      voltageValue = connection.readline()
      if voltageValue:
        print("Got value: %s" % voltageValue)
      else:
        print("Got no value")
    elif command == 3:
      current = float(input("What is the target current you want ? : "))
      current = int(current * 100)
      connection.write("C1".decode('hex'))
      connection.write(struct.pack(">H",current))
    elif command == 4:
      print("Reading current")
      connection.write("D1".decode('hex'))
      currentValue = connection.readline()
      if currentValue:
        print("Got value: %s" % currentValue)
      else:
        print("Got no value")
    elif command == 5:
      connection.write("C2".decode('hex'))
    elif command == 6:
      connection.write("C3".decode('hex'))
    elif command == 7:
      print("Reading input voltage")
      connection.write("D2".decode('hex'))
      vin = connection.readline()
      if vin:
        print("Got value: %s" % vin)
      else:
        print("Got no value")
    elif command == 8:
      print("Reading preregulator voltage")
      connection.write("D3".decode('hex'))
      prereg = connection.readline()
      if prereg:
        print("Got value: %s" % prereg)
      else:
        print("Got no value")
    else:
      print("Invalid input, dumbass")

    command = int(input(directions))

except Exception as ex:
  print("Error!. Error message: %s" % ex)


