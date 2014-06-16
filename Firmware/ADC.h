#ifndef ADC_H
#define ADC_H

#include<avr/io.h>
#include<avr/interrupt.h>
#include "IOHandler.h"
#include "TIMER.h"
#include "IOMapping.h"

#define ADC_STARTCONVERSION ADCSRA |= 1 << ADSC
#define ADC_DELAY 20 //in ms

void ADC_Initialize(void);
void ADC_StartMeasuringCurrent(void);
void ADC_StartMeasuringVoltage(void);
int ADC_GetMeasuredVoltage(void);
int ADC_GetMeasuredCurrent(void);

// GLOBAL VARIABLE
// that keeps track of the new reading of the ADC
// should be set to -1 for no new reading.
extern volatile uint16_t ADC_reading;

#endif
