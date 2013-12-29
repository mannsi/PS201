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

	char input[80];
	
	USART_Transmit((unsigned char) "Hello world");
	puts("Hello world!");
	
	while(1){
		puts("Hello world!");
		char firstChar = getchar();
		if (firstChar == '*')
		{
			// Command
			fgets(input,80,stdin);
			printf("You wrote *%s\n",input);
		}
		else if (firstChar == ':')
		{
			// Command
			fgets(input,80,stdin);
			printf("You wrote :%s\n",input);
		}
		else
		{
			printf("no command: %c\n",firstChar);
		}
	}
	
	return 0;
}
