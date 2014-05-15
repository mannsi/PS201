# from PsController.Control.Controller import Controller
#
# controller = Controller()
#
#
# def connect():
#     if controller.connected:
#         return True
#     print("Connecting")
#     deviceUsbPort = controller.getDeviceUsbPort()
#     connected = controller.connect(deviceUsbPort)
#     if not connected:
#         print("Unable to connect")
#     else:
#         print("Connected")
#     return connected
#
#
# def setValues():
#     connected = connect()
#     if connected:
#         controller.setTargetCurrent(200)  # 200 mA
#         controller.setTargetVoltage(2)  # 2 V
#
#
# def getIndividualValues():
#     connected = connect()
#     if connected:
#         outputVoltage = controller.getOutputVoltage()
#         outputCurrent = controller.getOutputCurrent()
#         targetVoltage = controller.getTargetVoltage()
#         targetCurrent = controller.getTargetCurrent()
#         inputVoltage = controller.getInputVoltage()
#         preRegVoltage = controller.getPreRegulatorVoltage()
#         deviceOn = controller.getDeviceIsOn()
#         print(outputVoltage, outputCurrent, targetVoltage, targetCurrent, inputVoltage, preRegVoltage, deviceOn)
#
#
# def getAllValues():
#     connected = connect()
#     if connected:
#         deviceValues = controller.getAllValues()
#         outputVoltage = deviceValues.outputVoltage
#         outputCurrent = deviceValues.outputCurrent
#         targetVoltage = deviceValues.targetVoltage
#         targetCurrent = deviceValues.targetCurrent
#         inputVoltage = deviceValues.inputVoltage
#         preRegVoltage = deviceValues.preRegVoltage
#         deviceOn = deviceValues.outputOn
#         print(outputVoltage, outputCurrent, targetVoltage, targetCurrent, inputVoltage, preRegVoltage, deviceOn)
#
#
# setValues()
# getIndividualValues()
# getAllValues()