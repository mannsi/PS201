#ifndef USART_H
#define USART_H

#include<avr/io.h>
#include<stdio.h>
#include <string.h>
#include <util/crc16.h>
#include "def.h"
#ifndef F_CPU
#define F_CPU 16000000
#endif

#ifndef BAUD
#define BAUD 9600
#endif
//#include <util/setbaud.h>

#define MYUBRR (F_CPU/16/BAUD - 1)

#define USART_ESC				(0x7D)
#define USART_START				(0x7E)
#define USART_END				(0x7E)
#define USART_FLIPBIT			(0x20)

#define USART_ACK				(0x06)
#define USART_NAK				(0x15)

#define USART_SEND_VOLTAGE 		(0xD0)
#define USART_RECEIVE_VOLTAGE 	(0xC0)
#define USART_SEND_CURRENT 		(0xD1)
#define USART_RECEIVE_CURRENT 	(0xC1)
#define USART_SEND_VIN	 		(0xD2)
#define USART_SEND_VPREREG 		(0xD3)
#define USART_ENABLE_OUTPUT		(0xC2)
#define USART_DISABLE_OUTPUT	(0xC3)
#define USART_IS_OUTPUT_ON  	(0xC4)
#define USART_SEND_SET_VOLTAGE	(0xE0)
#define USART_SEND_SET_CURRENT	(0xE1)
#define USART_SEND_HANDSHAKE	(0xA0)
#define USART_HANDSHAKE			(0xA1)
#define USART_WRITEALL			(0xA5)

void USART_Initialize(void);
int USART_PutChar(char c, FILE *stream);
int USART_GetChar(FILE *stream);
void USART_TransmitChar(unsigned char data);	// Should go
void USART_Transmit(unsigned char * b);			// Should go
unsigned char USART_ReceiveCommand(void);		// Should go
int USART_ReceiveData(void);					// Should go
int USART_IsReceivingData(void);
uint8_t USART_GetPacket(uint8_t *cmd, char *data, uint8_t maxlen, FILE *stream);
void USART_SendPacket(uint8_t cmd, char *data, FILE *stream);


// IO Stream
FILE USART_input;
FILE USART_output;

#endif
