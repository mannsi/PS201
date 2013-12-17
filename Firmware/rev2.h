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
 void writeDebug(char *debugMessage);
 void transferToDAC(unsigned char CTRL, int a);
 void writeToLCD(int voltage, int current);
 void writeVoltageToUsb(int voltage);
 void writeCurrentToUsb(int current);
 void writeToUsb(int voltage, int current, int voltageSet, int currentSet, int preregVoltage, unsigned char outputOn);
 void joinArrays(
	unsigned char *voltageArray,
	unsigned char *currentArray,
	unsigned char *voltageSetArray,
	unsigned char *currentSetArray,
	unsigned char *voltagePreregArray,
	unsigned char outputOn,
	unsigned char *combinedArray);
 int appendArray(unsigned char *targetArray, int arraySize, unsigned char *appendingArray, int appendingArrayMaxSize);
 void mapVoltage(int volt, unsigned char* b);
 void mapCurrent(int cur, unsigned char* b);
 void clearArray(unsigned char *array, int size);
 void switchOutput(void);
 void enableOutput(void);
 void disableOutput(void);
 void initRegistries(void);
 void initCalibration(void);

#endif
