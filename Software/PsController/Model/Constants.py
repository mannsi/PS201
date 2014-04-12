"""
Special device function constants
"""
HANDSHAKE = int('0xa0', 16) # Send this to device as command and get PROGRAMID back as command if device responds
PROGRAMID = int('0xa1', 16) # The command that device repsonds with if given HANDSHAKE command
START = int('0x7e', 16) # This is the first and last part of the device serial response
ACKNOWLEDGE = int('0x06', 16) # Device send this as command if it acknowledged the last command
NOTACKNOWLEDGE = int('0x15', 16) # Device send this as command if it did not acknowledged the last command
ESCAPE = int('0x7d', 16) # Indicates that the next char is an escaped char
FLIP = int('0x20', 16) # Used to escape chars
NEW_LINE = int('0x0a', 16)
RETURN = int('0x0d', 16)

"""
These are device commands. All commands are assumed to be performed by the device
"""
WRITE_OUTPUT_VOLTAGE = int('0xd0', 16)
WRITE_OUTPUT_CURRENT = int('0xd1', 16)
WRITE_INPUT_VOLTAGE = int('0xd2', 16)
WRITE_PREREGULATOR_VOLTAGE = int('0xd3', 16)
WRITE_ALL = int('0xa5', 16)
WRITE_IS_OUTPUT_ON = int('0xc4', 16)
WRITE_TARGET_VOLTAGE = int('0xe0', 16)
WRITE_TARGET_CURRENT = int('0xe1', 16)
READ_TARGET_VOLTAGE = int('0xc0', 16)
READ_TARGET_CURRENT = int('0xc1', 16)
TURN_ON_OUTPUT = int('0xc2', 16)
TURN_OFF_OUTPUT = int('0xc3', 16)
START_STREAM = int('0xa2', 16)
STOP_STREAM = int('0xa3', 16)

