#include "ADC.h"

// define the raw ADC read variables
int ADC_reading = 0;
unsigned char ADC_status = 0;

// Setup for the ADC channels
void ADC_initialize(void)
{
	// initialize ADC on the voltage channel
	ADMUX |= VOLTAGE_MON;
	ADC_status = ADC_VOLTAGE;
	// Enable the ADC in interupt mode
	ADCSRA = (1 << ADEN) | (1 << ADIE);
	// Set the ADC prescaler to 128 for max
	// sampling speed
	ADCSRA |= (1 << ADPS0) | (1 << ADPS1) | (1 << ADPS2); 
}

// The ADC interupt function is automatically triggered
// when the ADC has finished converting. Here we store 
// the value. The main loop then restarts the DAC on 
// a different channel.
ISR(ADC_vect)
{
	ADC_reading = ADC;
	ADC_status |= ADC_NEWREADING;
}

