#include "USART.h"

FILE USART_input = FDEV_SETUP_STREAM(NULL,USART_GetChar,_FDEV_SETUP_READ);
FILE USART_output = FDEV_SETUP_STREAM(USART_PutChar,NULL,_FDEV_SETUP_WRITE);


void USART_Initialize(void)
{
	// Set BAUD rate
	UBRR0H = (unsigned char)(MYUBRR>>8);
	UBRR0L = (unsigned char) MYUBRR;

	// Enable receiver and transmitter
	BIT_SET(UCSR0B,BIT(RXEN0));
	BIT_SET(UCSR0B,BIT(TXEN0));
	// Set frame format: 8data, 2stop bit
	BIT_SET(UCSR0C,BIT(USBS0));
	BIT_SET(UCSR0C,BIT(UCSZ00));

	// Set stdout and in
	//stdout = &USART_output;
	//stdin  = &USART_input;
}

int USART_PutChar(char c, FILE *stream)
{
	if(c == '\n')
	{
		USART_PutChar('\r',stream);
	}
	while ( !BIT_GET(UCSR0A,BIT(UDRE0)) );
	UDR0 = c;
	return 0;
}

int USART_GetChar(FILE *stream)
{
	while ( !BIT_GET(UCSR0A,BIT(RXC0)) );
	return (int) UDR0;
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
