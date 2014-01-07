/************************************
*									*
*		Serial Test to try			*			
*		IOStream functionality		*
*		Fridrik F Gautason			*
*		Copyright 2013				*
*									*
************************************/

#include "serialTest.h"

int main(void){
	USART_Initialize();
	// Set stdout and in
	stdout = &USART_output;
	stdin  = &USART_input;

	uint8_t cmd = 0;
	char data[MAXLEN];
	
	//USART_Transmit((unsigned char) "Hello world");
	puts("Hello world!");
	
	while(1){
		if(USART_IsReceivingData())
		{
			if(getpacket(&cmd,data))
			{
				printf("Command %c received ",cmd);
				printf("with data ");
				puts(data);
				sprintf(data,"Frissi");
				cmd = ((uint8_t) '1');
				sendpacket(cmd,data);
				putchar('\n');
			}
		}
	}
	
	return 0;
}
