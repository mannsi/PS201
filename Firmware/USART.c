#include "USART.h"

void USART_Initialize(void)
{
	// Set BAUD rate
	UBRRH = (unsigned char)(MYUBRR>>8);
	UBRRL = (unsigned char) MYUBRR;

	// Enable receiver and transmitter
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

void USART_Transmit(unsigned char * data)
{
	unsigned char i;

	for(i=0;i<100;i++)
	{
		if(!data[i]) break;
		USART_TransmitChar(data[i]);
	}
	USART_TransmitChar('\n');
}

unsigned char USART_ReceiveCommand()
{
	if(UCSRA & 1 << RXC)
	{
		// Decode the signal in main loop
		return UDR;
	}
	// return 0 for no command
	return 0;
}

int USART_ReceiveData()
{
	int out;
	// DANGEROUS! we wait for data
	while( !(UCSRA & (1<<RXC)));
	out = UDR<<8;
	while( !(UCSRA & (1<<RXC)));
	out |= UDR;
	
	return out;
}

