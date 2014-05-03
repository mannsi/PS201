#ifndef ADC_H
#define ADC_H

#include<avr/io.h>
#include<avr/interrupt.h>
#include "IOHandler.h"

#define ADC_STARTCONVERSION ADCSRA |= 1 << ADSC

void ADC_Initialize(void);
void ADC_StartMeasuring(unsigned char);

// GLOBAL VARIABLE
// that keeps track of the new reading of the ADC
// should be set to -1 for no new reading.
extern volatile uint16_t ADC_reading;

#endif
