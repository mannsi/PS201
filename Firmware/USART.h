#ifndef USART_H
#define USART_H

#include<stdio.h>

void USART_Initialize(void);
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
