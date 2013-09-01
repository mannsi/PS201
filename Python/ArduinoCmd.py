import serial
import time
import struct

port='/dev/ttyUSB1'
print("--Selecting USB port %s--" % port)

greetings = "USB connected. Now what motherfucker ?\n"
directions = "\t1 = Set voltage\n"
directions +="\t2 = Read voltage\n"
directions +="\t3 = Read set voltage\n"
directions +="\t4 = Set current\n"
directions +="\t5 = Read current\n"
directions +="\t6 = Read set current\n"
directions +="\t7 = Turn on output\n"
directions +="\t8 = Turn off output\n"
directions +="\t9 = Read input voltage\n"
directions +="\t10 = Read preregulator voltage\n"
directions +="\t11 = Request handshake\n"
directions +="\t12 = Exit \n: "

try:
  connection = serial.Serial(port, timeout = 2)
  print(greetings)
  command = int(input(directions))
  while command is not 12:
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
      print("Reading set voltage")
      connection.write("E0".decode('hex'))
      voltageValue = connection.readline()
      if voltageValue:
        print("Got value: %s" % voltageValue)
      else:
        print("Got no value")
    elif command == 4:
      current = float(input("What is the target current you want ? : "))
      current = int(current * 100)
      connection.write("C1".decode('hex'))
      connection.write(struct.pack(">H",current))
    elif command == 5:
      print("Reading current")
      connection.write("D1".decode('hex'))
      currentValue = connection.readline()
      if currentValue:
        print("Got value: %s" % currentValue)
      else:
        print("Got no value")
    elif command == 6:
      print("Reading set current")
      connection.write("E1".decode('hex'))
      currentValue = connection.readline()
      if currentValue:
        print("Got value: %s" % currentValue)
      else:
        print("Got no value")
    elif command == 7:
      connection.write("C2".decode('hex'))
    elif command == 8:
      connection.write("C3".decode('hex'))
    elif command == 9:
      print("Reading input voltage")
      connection.write("D2".decode('hex'))
      vin = connection.readline()
      if vin:
        print("Got value: %s" % vin)
      else:
        print("Got no value")
    elif command == 10:
      print("Reading preregulator voltage")
      connection.write("D3".decode('hex'))
      prereg = connection.readline()
      if prereg:
        print("Got value: %s" % prereg)
      else:
        print("Got no value")
    elif command == 11:
      print("Requesting handshake...")
      connection.write("A0".decode('hex'))
      handshake = connection.readline()
      if handshake:
        print("Received!")
      else:
        print("no luck...")
    else:
      print("Invalid input, dumbass")

    command = int(input(directions))

except Exception as ex:
  print("Error!. Error message: %s" % ex)


