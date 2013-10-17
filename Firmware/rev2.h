#ifndef REV2_H
#define REV2_H

#include<avr/io.h>
#include<avr/interrupt.h>
#include "LCD.h"
#include "SW.h"
#include "ADC.h"
#include "USART.h"

// Shortcuts for the DAC chip select pin
#define SELECT_DAC PORTD &= ~(1 << PD7)
#define DESELECT_DAC PORTD |= (1 << PD7)

int main(void);
void transferToDAC(unsigned char CTRL,uint16_t a);
void mapVoltage(uint16_t volt, unsigned char* b);
void mapCurrent(uint16_t cur, unsigned char* b);

static void initRegistries(void);
static void initDelays(void);
static void initCalibration(void);
static void initMappingValues(void);

#endif
