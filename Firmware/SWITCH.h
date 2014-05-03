#ifndef SWITCH_H
#define SWITCH_H

#include "IOHandler.h"

#ifndef F_CPU
#define F_CPU 16000000
#endif
#include<util/delay.h>

typedef struct
{
  port *switchPort;
  pin switchPin;
  unsigned char state;
} button;

// Generic initialization
void SWITCH_Initialize(button *b);
// Returns one if switch state is updated
unsigned char SWITCH_UpdateState(button *b);
unsigned char SWITCH_GetState(button *b);
unsigned char SWITCH_Pressed(button *b);

// Needs to be rewritten:
// To keep up with the encoder
#define ENCODER ((PINC >> PC3) & 0x03)
#define ENCODER_CCW 0x10

unsigned char SW_CheckEncoder(void);
unsigned char SW_encoderState;
#endif