#ifndef REV3_H
#define REV3_H

#ifndef F_CPU
#define F_CPU 16000000
#endif

#include<avr/io.h>
#include "def.h"
#include "USART.h"

#define MAXLEN 80
#define getpacket(_cmd,_data) USART_GetPacket(_cmd,_data,MAXLEN,stdin)
#define sendpacket(_cmd,_data) USART_SendPacket(_cmd,_data,stdout)

int main(void);

#endif