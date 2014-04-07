from PsController.Control.Controller import Controller

controller = Controller()

def connect():
    if controller.connected:
        return True
    print("Connecting")
    deviceUsbPort = controller.getDeviceUsbPort()
    connected = controller.connect(deviceUsbPort)
    if not connected:
        print("Unable to connect")
    else:
        print("Connected")
    return connected

def setValues():
    connected = connect()
    if connected:
        controller.setTargetCurrent(200) # 200 mA
        controller.setTargetVoltage(2) # 2 V

def getIndividualValues():
    connected = connect()
    if connected:
        outputVoltage = controller.getRealVoltage()
        outputCurrent = controller.getRealCurrent()
        targetVoltage = controller.getTargetVoltage()
        targetCurrent = controller.getTargetCurrent()
        inputVoltage = controller.getInputVoltage()
        preRegVoltage = controller.getPreRegulatorVoltage()
        deviceOn = controller.getDeviceIsOn()

def getAllValues():
    connected = connect()
    if connected:
        deviceValues = controller.getAllValues()
        outputVoltage = deviceValues.realVoltage
        outputCurrent = deviceValues.realCurrent
        targetVoltage = deviceValues.targetVoltage
        targetCurrent = deviceValues.targetCurrent
        inputVoltage = deviceValues.inputVoltage
        preRegVoltage = deviceValues.preRegVoltage
        deviceOn = deviceValues.outputOn


setValues()
getIndividualValues()
getAllValues()