#include "USART.h"

void USART_Initialize(void)
{
	// Set BAUD rate
	UBRR0H = (unsigned char)(MYUBRR>>8);
	UBRR0L = (unsigned char) MYUBRR;

	// Enable receiver and transmitter
	UCSR0B = (1 << RXEN0) | (1 << TXEN0);
	// Set frame format: 8data, 2stop bit
	UCSR0C = (1<<USBS0)|(3<<UCSZ00);
}

void USART_TransmitChar(unsigned char data)
{
	// Wait for empty transmit buffer
	while ( !(UCSR0A & (1<<UDRE0)) );
	// Put the data into buffer
	UDR0 = data;
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
	if(UCSR0A & 1 << RXC0)
	{
		// Decode the signal in main loop
		return UDR0;
	}
	// return 0 for no command
	return 0;
}

int USART_ReceiveData()
{
	int out;
	// DANGEROUS! we wait for data
	while( !(UCSR0A & (1<<RXC0)));
	out = UDR0<<8;
	while( !(UCSR0A & (1<<RXC0)));
	out |= UDR0;
	
	return out;
}
