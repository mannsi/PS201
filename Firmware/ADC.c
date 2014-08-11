#include "ADC.h"

// define the raw ADC read variables
volatile uint16_t ADC_reading = -1;

// Setup for the ADC channels
void ADC_Initialize(void)
{
  ADMUX = 0;
  // Enable the ADC in interupt mode
  ADCSRA = 0;
  // Enable ADC
  BIT_SET(ADCSRA,BIT(ADEN));
  // Enable ADC interupt
  BIT_SET(ADCSRA,BIT(ADIE));
  // Set the ADC prescaler to 64 for ADC
  // clock of 125kHz.
  //BIT_SET(ADCSRA,BIT(ADPS0));
  BIT_SET(ADCSRA,BIT(ADPS1));
  BIT_SET(ADCSRA,BIT(ADPS2));
}

void ADC_StartMeasuring(unsigned char a)
{
  ADMUX = 0;
  BIT_SET(ADMUX,a);
  ADC_STARTCONVERSION;
}

// The ADC interupt function is automatically triggered
// when the ADC has finished converting. Here we store
// the value. The main loop then restarts the DAC on
// a different channel.
ISR(ADC_vect)
{
  ADC_reading = ADC;
}
