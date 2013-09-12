"""
Demonstrates connecting to the PSP device, updating the voltage periodically and saving the results to file.
"""
import sys
sys.path.append("..")
import PspController
import time
from datetime import datetime

timeIncrement = 2
voltage = 1
finalVoltage = 1.5
voltageIncrement = 0.1
current = 500 #mA
usbPortNumber = 3
controller = PspController.Controller()
connected = controller.connect(usbPortNumber)

if connected:
  print("Connected")
else:
  print("Not able to connect. Aborting")
  exit()

print("Script running")
controller.setTargetCurrent(current)
time.sleep(50/1000)
controller.setOutputOnOff(True)
time.sleep(50/1000)
with open('VoltageIncrement.txt', 'w') as f:
  while True:
    controller.setTargetVoltage(voltage)
    time.sleep(50/1000)
    realVoltage = controller.getRealVoltage()
    realCurrent = controller.getRealCurrent()
    outputString = "%s \t %s \t %s \n" % (datetime.now(), realVoltage, realCurrent)
    f.write(outputString)

    if voltage >= finalVoltage:
      break

    voltage += voltageIncrement
    time.sleep(timeIncrement)
