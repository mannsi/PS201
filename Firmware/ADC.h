#ifndef ADC_H
#define ADC_H

#include "def.h"
#include<avr/io.h>
#include<avr/interrupt.h>

#define VOLTAGE_MON 0x07 // ADC7
#define CURRENT_MON 0x01 // ADC1
#define PREREG 		0x02 // ADC2
#define VIN_MON 	0x06 // ADC6

// For the ADC status variable we define:
#define ADC_NEWREADING 		(1<<6)
#define ADC_ISREADING		(1<<5)
#define ADC_VOLTAGE 		1
#define ADC_CURRENT 		(1<<1)
#define ADC_PREREGULATOR 	(1<<2)
#define ADC_VIN 			(1<<3)

#define ADC_STARTCONVERSION ADCSRA |= 1 << ADSC

void ADC_Initialize(void);

extern uint16_t ADC_reading;
extern unsigned char ADC_status;

#endif
