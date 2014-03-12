deviceWriteRealVoltage = b'\xd0'
deviceWriteRealCurrent = b'\xd1'
deviceWriteInputVoltage = b'\xd2'
deviceWritePreRegulatorVoltage = b'\xd3'
deviceReadTargetVoltage = b'\xc0'
deviceReadTargetCurrent = b'\xc1'
deviceWriteTargetVoltage = b'\xe0'
deviceWriteTargetCurrent = b'\xe1'
deviceTurnOnOutput = b'\xc2'
deviceTurnOffOutput = b'\xc3'
deviceWriteIsOutputOn = b'\xc4'
handshakeSignal = b'\xa0'
programId = b'\xa1'
deviceStartStream = b'\xa2'
deviceStopStream = b'\xa3'
deviceWriteAll = b'\xa5'
startChar = b'\x7E'
acknowledgeSignal = b'\x06'
notAcknowledgeSignal = b'\x15'