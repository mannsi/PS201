"""
Demonstrates connecting to the PSP device, updating the voltage periodically and saving the results to file.
"""
import sys
sys.path.append("..")
import PspController
import time
from datetime import datetime

targetVoltage = 4.2
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
controller.setTargetVoltage(targetVoltage)

while True:
  print("Checking of voltage has reached 4.2 V")
  time.sleep(50/1000)
  realVoltage = controller.getRealVoltage()
  if (realVoltage - targetVoltage) < 0.1:
    print("Yebb, turn off output")
    controller.setOutputOnOff(False)
    break

