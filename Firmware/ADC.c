#include "ADC.h"

// define the raw ADC read variables
uint16_t ADC_reading = 0;
unsigned char ADC_status = 0;

// Setup for the ADC channels
void ADC_initialize(void)
{
	// initialize ADC on the voltage channel
	ADMUX = 0;
	BIT_SET(ADMUX,VOLTAGE_MON);
	ADC_status = ADC_VOLTAGE;
	// Enable the ADC in interupt mode
	
	ADCSRA = 0;
	// Enable ADC
	BIT_SET(ADCSRA,BIT(ADEN));
	// Enable ADC interupt
	BIT_SET(ADCSRA,BIT(ADIE));
	// Set the ADC prescaler to 128 for min
	// sampling speed
	BIT_SET(ADCSRA,BIT(ADPS0));
	BIT_SET(ADCSRA,BIT(ADPS1));
	BIT_SET(ADCSRA,BIT(ADPS2));
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

