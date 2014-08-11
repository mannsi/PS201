#ifndef USART_H
#define USART_H

#include<stdio.h>
#include<string.h>
#include "IOMapping.h"

#ifndef F_CPU
#define F_CPU 8000000
#endif

#ifndef BAUD
#define BAUD 9600
#endif

#define SAMPLES_PER_BIT 16

#define MYLINBRR (F_CPU/SAMPLES_PER_BIT/BAUD - 1)

void USART_Initialize(void);
int USART_PutChar(char c, FILE *stream);
int USART_GetChar(FILE *stream);
int USART_IsReceivingData(void);

// IO Stream
FILE USART_input;
FILE USART_output;

// redefining macros
#undef	putchar
#define putchar(__c)	fputc(__c, &USART_output)
#undef	getchar
#define getchar()	fgetc(&USART_input)

#endif
