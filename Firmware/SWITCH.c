#include "SWITCH.h"

void SWITCH_Initialize(button *b)
{
  // Setup the hardware
  IOSetInput(*(b->switchPort),(b->switchPin));
  IOEnablePullup(*(b->switchPort),(b->switchPin));
  // Record the state and initialize variables
  b->state = IOGetPin(*(b->switchPort),(b->switchPin));
}

unsigned char SWITCH_UpdateState(button *b)
{
  unsigned char newState = IOGetPin(*(b->switchPort),(b->switchPin));
  if(newState != b->state)
  {
    // Debounce for 2 ms
    _delay_ms(2);
    newState = IOGetPin(*(b->switchPort),(b->switchPin));
    if(newState != b->state)
    {
      b->state = newState;
      return 1;
    }
  }
  return 0;
}

unsigned char SWITCH_GetState(button *b)
{
  return b->state;
}

unsigned char SWITCH_Pressed(button *b)
{
  return (SWITCH_UpdateState(b) && !SWITCH_GetState(b));
}

// We use the following table to read the rotary encoder correctly
// in order to register a "click" the encoder must go through five
// states:
//	00 -> 01 -> 11 
//	11 -> 10 -> 00
// for clockwise and
//	00 -> 10 -> 11 
//	11 -> 01 -> 00
// for counter clockwise. We will make use of this WHOLE chain to
// determine the order of direction and to midigate any bounce.
// The first entry in the table (the row) is the previous state,
// the second entry is the current read state.
const unsigned char rotaryTable[6][4] = {
// 00 is an arbitrary state, and here considered the
// starting state of the encoder.
//  {00,   01, 10, 11}	for reference
  { 0,    1,    4,    0    },// start at 00
  { 0,    1,    0,    0x12 },// CW  from 00
  { 2,    5,    3,    2    },// start at 11
  { 0x10, 2,    3,    2    },// CW  from 11
  { 0,    0,    4,    0x22 },// CCW from 00
  { 0x20, 5,    2,    2    },// CCW from 11
};


unsigned char SW_CheckEncoder()
{
  SW_encoderState = rotaryTable[SW_encoderState & 0x0f][ENCODER];
  return SW_encoderState & 0x30;	
}