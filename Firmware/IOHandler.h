#ifndef IOHANDLER_H
#define IOHANDLER_H

#include <avr/io.h>

// For readability
#define BIT(x)			(0x01 << (x))
#define BIT_SET(x,y)		((x) |= (y))
#define BIT_CLEAR(x,y)		((x) &= (~(y)))
#define BIT_FLIP(x,y)		((x) ^= (y))
#define BIT_GET(x,y)		((x) & (y))
#define BIT_VAL(x,y)		(((x)>>(y)) & 1)

// Collect all port information in one struct
typedef struct
{
  volatile unsigned char *direction;			// Direction register
  volatile unsigned char *output;			// Output register, to output data to port
  volatile unsigned char *input;			// Input register, to read data from port
  volatile unsigned char *interrupt;			// Pin change interrupt for the port
  volatile unsigned char *interruptEnableRegister;	// Register and bit to enable and 
  unsigned char interruptEnableBit;			// Disable the ports pin change interrupt.
} port;

// Use enum to define a 8-bit pin object
typedef uint8_t pin;

// To set a pin to input/output
void IOSetOutput(port po, pin pi);
void IOSetInput(port po, pin pi);
// As the name suggests, enable pull-up. Note that the function does not
// check that the respective pin is really a input.
void IOEnablePullup(port po, pin pi);
// Set a output pin high.
void IOSetPin(port po, pin pi);
// Set a output pin low.
void IOClearPin(port po, pin pi);
// Invert the pins state, that is if the pin is high then it is set to
// low, and if it is low it is set to high.
void IOTogglePin(port po, pin pi);
// Get the value of a input pin.
unsigned char IOGetPin(port po, pin pi);
// Enable pin change interrupt on a pin
void IOEnableInterrupt(port po, pin pi);
// Disable pin change interrupt on a pin
void IODisableInterrupt(port po, pin pi);
// Disable all pin change interrupts on a port
void IODisableAllInterrupts(port po);
void IOTurnOnPinChangeInterrupt(port po);
void IOTurnOffPinChangeInterrupt(port po);
// Set the entire port to a 8-bit value
void IOSetAllPins(port po, unsigned char val);
// Get the 8-bit value of a port
unsigned char IOGetAllPins(port po);

// Definitions of ports as external variables. This definition is processor 
// specific to the ATMEGA series microcontrollers, and depends on the <avr/io.h>
// library.
extern port portA, portB;

#endif
