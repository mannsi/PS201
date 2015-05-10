#ifndef ADC_H
#define ADC_H

#include <stdint.h>

void ADC_Initialize(void);
void ADC_StartMeasuringCurrent(void);
void ADC_StartMeasuringVoltage(void);
int ADC_GetMeasuredVoltage(void);
int ADC_GetMeasuredCurrent(void);

#endif
