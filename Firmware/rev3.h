#ifndef REV3_H
#define REV3_H

#include<avr/io.h>
#include<avr/interrupt.h>
#include "def.h"
#include "LCD.h"
#include "SW.h"
#include "ADC.h"
#include "USART.h"

// Shortcuts for the DAC chip select pin
#define SELECT_DAC PORTD &= ~(1 << PD7)
#define DESELECT_DAC PORTD |= (1 << PD7)

// Shortcuts for enabling and disabling the output
#define ENABLE_OUTPUT  PORTC &= ~(1 << PC0)
#define DISABLE_OUTPUT PORTC |= (1 << PC0)

int main(void);
void transferToDAC(unsigned char CTRL,uint16_t a);
void mapVoltage(uint16_t volt, unsigned char* b);
void mapCurrent(uint16_t cur, unsigned char* b);
void writeVoltageToUsb(uint16_t voltage);
void writeCurrentToUsb(uint16_t current);

void switchOutput(void);
void enableOutput(void);
void disableOutput(void);

void writeToUsb(uint16_t voltage, 
				uint16_t current, 
				uint16_t voltageSet, 
				uint16_t currentSet, 
				uint16_t preregVoltage, 
				unsigned char outputOn);

static void initRegistries(void);
static void initCalibration(void);

void joinArrays(
	unsigned char *voltageArray, 
	unsigned char *currentArray, 
	unsigned char *voltageSetArray, 
	unsigned char *currentSetArray,
	unsigned char *voltagePreregArray, 
	unsigned char outputOn,
	unsigned char *combinedArray);
int appendArray(unsigned char *targetArray, 
				int arraySize, 
				unsigned char *appendingArray, 
				int appendingArrayMaxSize);
void clearArray(unsigned char *array, int size);

#endif
