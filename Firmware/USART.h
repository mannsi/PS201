#ifndef USART_H
#define USART_H

#include<avr/io.h>
#include<stdio.h>
#ifndef F_CPU
#define F_CPU 16000000
#endif

#define BAUD 9600
#define MYUBRR (F_CPU/16/BAUD - 1)

void USART_Initialize(void);
void USART_TransmitChar(unsigned char data);
void USART_Transmit(uint16_t num);

#endif
