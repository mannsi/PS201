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

void USART_Transmit(unsigned char * b)
{
	unsigned char i;

	for(i=0;i<100;i++)
	{
		if(!b[i]) break;
		USART_TransmitChar(b[i]);
	}
}

unsigned char USART_RecieveCommand()
{
	if(UCSRA & 1 << RXC)
	{
		// Decode the signal in main loop
		return UDR;
	}
	// return 0 for no command
	return 0;
}

uint16_t USART_ReceiveData()
{
	uint16_t out;
	// DANGEROUS! we wait for data
	while( !(UCSRA & (1<<RXC)));
	out = UDR<<8;
	while( !(UCSRA & (1<<RXC)));
	out |= UDR;
	
	return out;
}

