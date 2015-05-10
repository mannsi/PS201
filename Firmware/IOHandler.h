#ifndef IOHANDLER_H
#define IOHANDLER_H

#include <avr/io.h>
#include "Structs.h"

#ifndef F_CPU
#define F_CPU 8000000
#endif

// For readability
#define BIT(x)			    (0x01 << (x))
#define BIT_SET(x,y)		((x) |= (y))
#define BIT_CLEAR(x,y)		((x) &= (~(y)))
#define BIT_FLIP(x,y)		((x) ^= (y))
#define BIT_GET(x,y)		((x) & (y))
#define BIT_VAL(x,y)		(((x)>>(y)) & 1)

// Definitions of ports as external variables. This definition is processor specific
// to the ATMEGA series microcontrollers, and depends on the <avr/io.h> library.
extern port portB, portC, portD;

// Use enum to define a 8-bit pin object
typedef uint8_t pin;

// To set a pin to input/output
void IOSetOutput(port po, pin pi);
void IOSetInput(port po, pin pi);
// Set a output pin high.
void IOSetPin(port po, pin pi);
// Set a output pin low.
void IOClearPin(port po, pin pi);

#endif
