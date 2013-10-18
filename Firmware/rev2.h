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
void transferToDAC(unsigned char CTRL,int a);
void writeToLCD(int voltage, int current);
void mapVoltage(int volt, unsigned char* b);
void mapCurrent(int cur, unsigned char* b);
void writeVoltageToUsb(int voltage);
void writeCurrentToUsb(int current);

static void initRegistries(void);
static void initCalibration(void);

#endif
