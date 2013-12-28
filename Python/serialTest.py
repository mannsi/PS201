import sys
import time
from DataLayer import DataLayer

portNumber = 2
baudRate = 9600
timeOut = 2

dataLayer = DataLayer()
connected = dataLayer.connect('COM4')
if connected:
    print("Connected")
else:
    print("Unable to connect")
    sys.exit()

"""
Test setting the voltage
"""
#print("Setting target voltage to 3V")
#dataLayer.setTargetVoltage(3)

"""
Test reading the voltage
"""
targetVoltage = dataLayer.getTargetVoltage()
print("Target voltage: " , targetVoltage, "V")

#print('Getting all values')
#time.sleep(1)
#allValue = dataLayer.getAllValues()
#for value in allValues:
#    print(value)
    
print("All values printed")



