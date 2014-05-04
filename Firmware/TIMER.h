#ifndef TIMER_H
#define TIMER_H

#include "IOMapping.h"

void TIMER_Initialize(void);

// pass in time in ms
void TIMER_ADC_Start(uint8_t time);
void TIMER_ADC_Stop(void);

#endif