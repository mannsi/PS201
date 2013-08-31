#include "USART.h"

void USART_Initialize(void)
{
	// Set BAUD rate
	UBRRH = (unsigned char)(MYUBRR>>8);
	UBRRL = (unsigned char) MYUBRR;

	// Enable reciever and transmitter
	UCSRB = (1 << RXEN) | (1 << TXEN);
	// Set frame format: 8data, 2stop bit
	UCSRC = (1<<URSEL) | (1<<USBS) | (3<<UCSZ0);
}

void USART_TransmitChar(unsigned char data)
{
	// Wait for empty transmit buffer
	while ( !(UCSRA & (1<<UDRE)) );
	// Put the data into buffer
	UDR = data;
}

void USART_Transmit(uint16_t num)
{
	int wholeNum = num/100;
	uint16_t fraction = num - wholeNum*100;
	
	unsigned char b [10];
	sprintf(b,"%2i.%02i\n",wholeNum,fraction);

	unsigned char i;

	for(i=0;i<20;i++)
	{
		if(!b[i]) break;
		USART_TransmitChar(b[i]);
	}
}

