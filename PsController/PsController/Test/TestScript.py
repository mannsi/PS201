#Missing how much 'variance' should be allowed on the target vs real values. Right now the tests are assuming 100% correctness

import sys
import time
from DataLayer import DataLayer

def VoltageInBoundsTest(dataLayer, targetVoltage, outputOn):
    dataLayer.setOutputOnOff(outputOn)
    print("Setting target voltage to ", targetVoltage,"V")
    dataLayer.setTargetVoltage(targetVoltage)
    #time.sleep(1)
    print("Reading target voltage")
    readTargetVoltage = dataLayer.getTargetVoltage()
    if outputOn:
        if readTargetVoltage == targetVoltage:
            print("OK: Reading target voltage")
        else:
            print("FAIL: Expected ", targetVoltage,"V but got ", readTargetVoltage, "V")
    else:
        if readTargetVoltage == 0:
            print("OK: Reading target voltage")
        else:
            print("FAIL: Expected 0V because output is off but got ", readTargetVoltage, "V")
    print("Testing real voltage")
    readRealVoltage = dataLayer.getRealVoltage()
    if outputOn:
        if readRealVoltage == targetVoltage:
            print("OK: Reading real voltage")
        else:
            print("FAIL: Expected ", targetVoltage,"V but got ", readRealVoltage, "V")
    else:
        if readRealVoltage == 0:
            print("OK: Reading real voltage")
        else:
            print("FAIL: Expected 0V because output is off but got ", readRealVoltage, "V")

def VoltageOutOfBoundsTest(dataLayer, targetVoltage, outputOn):
    dataLayer.setOutputOnOff(outputOn)
    print("Test setting voltage out of bounds")
    targetVoltageBeforeChanges = dataLayer.getTargetVoltage()
    realVoltageBeforeChanges = dataLayer.getRealVoltage()
    dataLayer.setTargetVoltage(targetVoltage)
    targetVoltageAfterChanges = dataLayer.getTargetVoltage()
    realVoltageAfterChanges = dataLayer.getRealVoltage()

    if targetVoltageBeforeChanges == targetVoltageAfterChanges:
        print("OK: Target voltage did not change")
    else:
        print("FAIL: Target voltage did change")

    if realVoltageBeforeChanges == realVoltageAfterChanges:
        print("OK: Real voltage did not change")
    else:
        print("FAIL: Real voltage did change")

def CurrentInBoundsTest(dataLayer, targetCurrent, outputOn):
    dataLayer.setOutputOnOff(outputOn)
    print("Setting target current to ", targetCurrent,"mA")
    dataLayer.setTargetCurrent(targetCurrent)
    print("Reading target voltage")
    readTargetCurrent = dataLayer.getTargetCurrent()
    if outputOn:
        if readTargetCurrent == targetCurrent:
            print("OK: Reading target Current")
        else:
            print("FAIL: Expected ", targetCurrent,"mA but got ", readTargetCurrent, "mA")
    else:
        if readTargetCurrent == 0:
            print("OK: Reading target Current")
        else:
            print("FAIL: Expected 0mA because output is off but got ", readTargetCurrent, "mA")
    print("Testing real Current")
    readRealCurrent = dataLayer.getRealCurrent()
    if outputOn:
        if readRealCurrent == targetCurrent:
            print("OK: Reading real Current")
        else:
            print("FAIL: Expected ", targetCurrent,"mA but got ", readRealCurrent, "mA")
    else:
        if readRealCurrent == 0:
            print("OK: Reading real Current")
        else:
            print("FAIL: Expected 0V because output is off but got ", readRealCurrent, "mA")

def CurrentOutOfBoundsTest(dataLayer, targetCurrent, outputOn):
    dataLayer.setOutputOnOff(outputOn)
    print("Test setting Current out of bounds")
    targetCurrentBeforeChanges = dataLayer.getTargetCurrent()
    realCurrentBeforeChanges = dataLayer.getRealCurrent()
    dataLayer.setTargetCurrent(targetCurrent)
    targetCurrentAfterChanges = dataLayer.getTargetCurrent()
    realCurrentAfterChanges = dataLayer.getRealCurrent()

    if targetCurrentBeforeChanges == targetCurrentAfterChanges:
        print("OK: Target Current did not change")
    else:
        print("FAIL: Target Current did change")

    if realCurrentBeforeChanges == realCurrentAfterChanges:
        print("OK: Real Current did not change")
    else:
        print("FAIL: Real Current did change")

def TestAllTheInBoudnsValues(dataLayer, targetCurrent, targetVoltage, outputOn):
    dataLayer.setOutputOnOff(outputOn)
    print("Setting target voltage to ", targetVoltage,"V")
    print("Setting target current to ", targetCurrent,"V")
    dataLayer.setTargetVoltage(targetVoltage)
    dataLayer.setTargetCurrent(targetCurrent)
    print("Reading all values")
    allValues = dataLayer.getAllValues()
    listOfValues = allValues.split(";") 
    realVoltage = listOfValues[0]
    realCurrent = listOfValues[1]
    readTargetVoltage = listOfValues[2]
    readTargetCurrent = listOfValues[3]
    preReqVoltage = listOfValues[4]
    outputIsOn = listOfValues[5]
    
    if outputOn:
        if not outputIsOn:
            print("FAIL: Output was set to ON but it is read as OFF")
        if readTargetVoltage == targetVoltage:
            print("OK: Reading target voltage")
        else:
            print("FAIL: Expected ", targetVoltage, "V but got ", readTargetVoltage, "V")
        if realVoltage == targetVoltage:
            print("OK: Reading real voltage")
        else:
            print("FAIL: Expected ", targetVoltage, "V but got ", realVoltage, "V")
        if readTargetCurrent == targetCurrent:
            print("OK: Reading target Current")
        else:
            print("FAIL: Expected " , targetCurrent,"mA but got ", readTargetCurrent, "mA")
        if realCurrent == targetCurrent:
            print("OK: Reading real Current")
        else:
            print("FAIL: Expected " , targetCurrent,"mA but got ", realCurrent, "mA")
    else:
        if outputIsOn:
            print("FAIL: Output was set to OFF but it is read as ON")
        if readTargetVoltage == 0:
            print("OK: Reading target voltage")
        else:
            print("FAIL: Expected 0V because output is off but got ", readTargetVoltage, "V")
        if realVoltage == 0:
            print("OK: Reading real voltage")
        else:
            print("FAIL: Expected 0V because output is off but got ", realVoltage, "V")
        if readTargetCurrent == 0:
            print("OK: Reading target Current")
        else:
            print("FAIL: Expected 0mA because output is off but got ", readTargetCurrent, "mA")
        if realCurrent == 0:
            print("OK: Reading real Current")
        else:
            print("FAIL: Expected 0mA because output is off but got ", realCurrent, "mA")

def Run():
    dataLayer = DataLayer()
    port = dataLayer.detectDevicePort()

    if port is None:
        print("No device found on any port")
        sys.exit()
    else:
        print("Device found on port ", port)

    connected = dataLayer.connect(port)
    if connected:
        print("Connected")
    else:
        print("Unable to connect to device")
        sys.exit()

    """
    Initalize test
    """
    print("Initalizing tests")
    dataLayer.setOutputOnOff(True)

    """
    VOLTAGE TESTS
    """
    outputOn = True
    VoltageInBoundsTest(dataLayer, 3, outputOn)
    """
    VoltageInBoundsTest(dataLayer, 5, outputOn)
    VoltageOutOfBoundsTest(dataLayer, 21, outputOn)

    outputOn = False
    VoltageInBoundsTest(dataLayer, 3, outputOn)
    VoltageInBoundsTest(dataLayer, 5, outputOn)
    VoltageOutOfBoundsTest(dataLayer, 21, outputOn)

    """
    #CURRENT TESTS
    """
    outputOn = True
    CurrentInBoundsTest(dataLayer, 0, outputOn)
    CurrentInBoundsTest(dataLayer, 3, outputOn)
    CurrentInBoundsTest(dataLayer, 5, outputOn)
    CurrentOutOfBoundsTest(dataLayer, 21, outputOn)

    outputOn = False
    CurrentInBoundsTest(dataLayer, 0, outputOn)
    CurrentInBoundsTest(dataLayer, 300, outputOn)
    CurrentInBoundsTest(dataLayer, 500, outputOn)
    CurrentOutOfBoundsTest(dataLayer, 2000, outputOn)

    """
    #Complex tests
    """
    TestAllTheInBoudnsValues(dataLayer, 200, 2 , True)
    TestAllTheInBoudnsValues(dataLayer, 300, 3 , False)
    """
Run()