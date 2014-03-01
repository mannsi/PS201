#ifndef REV3_H
#define REV3_H

#include<avr/io.h>
#include<avr/interrupt.h>
#include<stdio.h>
#include<string.h>
#include<stdlib.h>
#include "def.h"
#include "LCD.h"
#include "SW.h"
#include "ADC.h"
#include "USART.h"
#include "EEPROM.h"

// Shortcuts for the DAC chip select pin
#define SELECT_DAC PORTD &= ~(1 << PD7)
#define DESELECT_DAC PORTD |= (1 << PD7)

// Shortcuts for enabling and disabling the output
#define ENABLE_OUTPUT  PORTC &= ~(1 << PC0)
#define DISABLE_OUTPUT PORTC |= (1 << PC0)

// Shortcuts for the serial communication
#define MAXLEN 80
#define getpacket(_cmd,_data) USART_GetPacket(_cmd,_data,MAXLEN,stdin)
#define sendpacket(_cmd,_data) USART_SendPacket(_cmd,_data,stdout)
#define sendcmd(_cmd) USART_SendCmd(_cmd,stdout)
#define sendACK() sendcmd(USART_ACK)
#define sendNAK() sendcmd(USART_NAK)

int main(void);
void transferToDAC(unsigned char CTRL,uint16_t a);
void mapVoltage(uint16_t volt, unsigned char* b);
void mapCurrent(uint16_t cur, unsigned char* b);
void mapToVoltage(uint16_t* volt, unsigned char* b);
void mapToCurrent(uint16_t* cur, char* b);
void writeVoltageToUsb(uint16_t voltage);
void writeCurrentToUsb(uint16_t current);

void switchOutput(void);
void enableOutput(void);
void disableOutput(void);

void writeToUsb(uint16_t voltage, 
				uint16_t current, 
				uint16_t voltageSet, 
				uint16_t currentSet, 
				uint16_t inputVoltage,
				uint16_t vinVoltage,
				unsigned char outputOn);

static void initRegistries(void);
static void initCalibration(void);
void doCalibration(void);

void joinArrays(
	unsigned char *voltageArray, 
	unsigned char *currentArray, 
	unsigned char *voltageSetArray, 
	unsigned char *currentSetArray,
	unsigned char *voltagePreregArray,
	unsigned char *voltageVinArray,
	unsigned char outputOn,
	unsigned char *combinedArray);
int appendArray(unsigned char *targetArray, 
				int arraySize, 
				unsigned char *appendingArray, 
				int appendingArrayMaxSize);
void clearArray(unsigned char *array, int size);

#endif
