#Missing how much 'variance' should be allowed on the target vs real values. Right now the tests are assuming 100% correctness

import sys
import time
from DataAccess import DataAccess

def VoltageInBoundsTest(DataAccess, targetVoltage, outputOn):
    DataAccess.setOutputOnOff(outputOn)
    print("Setting target voltage to ", targetVoltage,"V")
    DataAccess.setTargetVoltage(targetVoltage)
    #time.sleep(1)
    print("Reading target voltage")
    readTargetVoltage = DataAccess.getTargetVoltage()
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
    readRealVoltage = DataAccess.getRealVoltage()
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

def VoltageOutOfBoundsTest(DataAccess, targetVoltage, outputOn):
    DataAccess.setOutputOnOff(outputOn)
    print("Test setting voltage out of bounds")
    targetVoltageBeforeChanges = DataAccess.getTargetVoltage()
    realVoltageBeforeChanges = DataAccess.getRealVoltage()
    DataAccess.setTargetVoltage(targetVoltage)
    targetVoltageAfterChanges = DataAccess.getTargetVoltage()
    realVoltageAfterChanges = DataAccess.getRealVoltage()

    if targetVoltageBeforeChanges == targetVoltageAfterChanges:
        print("OK: Target voltage did not change")
    else:
        print("FAIL: Target voltage did change")

    if realVoltageBeforeChanges == realVoltageAfterChanges:
        print("OK: Real voltage did not change")
    else:
        print("FAIL: Real voltage did change")

def CurrentInBoundsTest(DataAccess, targetCurrent, outputOn):
    DataAccess.setOutputOnOff(outputOn)
    print("Setting target current to ", targetCurrent,"mA")
    DataAccess.setTargetCurrent(targetCurrent)
    print("Reading target voltage")
    readTargetCurrent = DataAccess.getTargetCurrent()
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
    readRealCurrent = DataAccess.getRealCurrent()
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

def CurrentOutOfBoundsTest(DataAccess, targetCurrent, outputOn):
    DataAccess.setOutputOnOff(outputOn)
    print("Test setting Current out of bounds")
    targetCurrentBeforeChanges = DataAccess.getTargetCurrent()
    realCurrentBeforeChanges = DataAccess.getRealCurrent()
    DataAccess.setTargetCurrent(targetCurrent)
    targetCurrentAfterChanges = DataAccess.getTargetCurrent()
    realCurrentAfterChanges = DataAccess.getRealCurrent()

    if targetCurrentBeforeChanges == targetCurrentAfterChanges:
        print("OK: Target Current did not change")
    else:
        print("FAIL: Target Current did change")

    if realCurrentBeforeChanges == realCurrentAfterChanges:
        print("OK: Real Current did not change")
    else:
        print("FAIL: Real Current did change")

def TestAllTheInBoudnsValues(DataAccess, targetCurrent, targetVoltage, outputOn):
    DataAccess.setOutputOnOff(outputOn)
    print("Setting target voltage to ", targetVoltage,"V")
    print("Setting target current to ", targetCurrent,"V")
    DataAccess.setTargetVoltage(targetVoltage)
    DataAccess.setTargetCurrent(targetCurrent)
    print("Reading all values")
    allValues = DataAccess.getAllValues()
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
    DataAccess = DataAccess()
    port = DataAccess.detectDevicePort()

    if port is None:
        print("No device found on any port")
        sys.exit()
    else:
        print("Device found on port ", port)

    connected = DataAccess.connect(port)
    if connected:
        print("Connected")
    else:
        print("Unable to connect to device")
        sys.exit()

    """
    Initalize test
    """
    print("Initalizing tests")
    DataAccess.setOutputOnOff(True)

    """
    VOLTAGE TESTS
    """
    outputOn = True
    VoltageInBoundsTest(DataAccess, 3, outputOn)
    """
    VoltageInBoundsTest(DataAccess, 5, outputOn)
    VoltageOutOfBoundsTest(DataAccess, 21, outputOn)

    outputOn = False
    VoltageInBoundsTest(DataAccess, 3, outputOn)
    VoltageInBoundsTest(DataAccess, 5, outputOn)
    VoltageOutOfBoundsTest(DataAccess, 21, outputOn)

    """
    #CURRENT TESTS
    """
    outputOn = True
    CurrentInBoundsTest(DataAccess, 0, outputOn)
    CurrentInBoundsTest(DataAccess, 3, outputOn)
    CurrentInBoundsTest(DataAccess, 5, outputOn)
    CurrentOutOfBoundsTest(DataAccess, 21, outputOn)

    outputOn = False
    CurrentInBoundsTest(DataAccess, 0, outputOn)
    CurrentInBoundsTest(DataAccess, 300, outputOn)
    CurrentInBoundsTest(DataAccess, 500, outputOn)
    CurrentOutOfBoundsTest(DataAccess, 2000, outputOn)

    """
    #Complex tests
    """
    TestAllTheInBoudnsValues(DataAccess, 200, 2 , True)
    TestAllTheInBoudnsValues(DataAccess, 300, 3 , False)
    """
Run()