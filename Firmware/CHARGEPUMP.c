#include "CHARGEPUMP.h"

void CHARGEPUMP_Initialize(void)
{
  // Enable pin and set to output (this is needed)
  IOSetOutput(CHARGEPUMP_PORT,CHARGEPUMP_PIN);

  // Pin driver must be set
  BIT_SET(TCCR1D,BIT(OC1AU));

  // Setting up OC1 which is the PWM module for
  // charge pump.
  BIT_SET(TCCR1A,BIT(COM1A0));	// Toggle output on match
  BIT_SET(TCCR1A,BIT(COM1A1));
  BIT_SET(TCCR1A,BIT(WGM10));	// FAST 8 bit PWM
  BIT_SET(TCCR1B,BIT(WGM12));
}

void CHARGEPUMP_Start(void)
{
  // Set the value to the compare register
  OCR1A = 127;
  // START with no prescaler
  BIT_SET(TCCR1B,BIT(CS10));
  BIT_CLEAR(TCCR1B,BIT(CS11));
  BIT_CLEAR(TCCR1B,BIT(CS12));

}

void CHARGEPUMP_Stop(void)
{
  BIT_CLEAR(TCCR1B,BIT(CS10));
  BIT_CLEAR(TCCR1B,BIT(CS11));
  BIT_CLEAR(TCCR1B,BIT(CS12));
}
