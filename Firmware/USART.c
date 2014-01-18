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

int USART_IsReceivingData()
{
	// The RXC0 bit of the UCSR0A register is set
	// when the buffer is loaded.
	if( BIT_GET(UCSR0A,BIT(RXC0)) )
	{
		return 1;
	}
	// return 0 for no command
	return 0;

}

static uint8_t DecodeChar(uint8_t *c, FILE *stream)
{
	*c = fgetc(stream);
	if (*c == USART_END)
	{
		*c = '\0';
		return 1;
	}
	if (*c == USART_ESC)
	{
		*c = (USART_FLIPBIT ^ fgetc(stream));
	}
	return 0;
}

uint8_t USART_GetPacket(uint8_t *cmd, char *data, uint8_t maxlen, FILE *stream)
{
	// Tha data structure is
	//	<SFLAG><CMD><LEN><DATA[LEN]><CRC><EFLAG>
	// This function returns CMD.
	
	// Catch the SFLAG	
	uint8_t buffer = fgetc(stream);
	if(buffer != USART_START)
	{
		*cmd = buffer;
		return 0;
	}

	// Next the CMD
	if (DecodeChar(cmd,stream))
	{
		*cmd = USART_NAK;
		return *cmd;
	}

	// The LEN
	uint8_t len = 0;
	if (DecodeChar(&len,stream))
	{
		*cmd = USART_NAK;
		return *cmd;
	}

	// Now we find the DATA, first we check if len 
	// exceeds maxlen
	if(len > maxlen)
	{
		*cmd = USART_NAK;
		return *cmd;
	}
	else if(len != maxlen)
	{
		data[len] = '\0';
	}

	int i;
	for (i = 0; i < len; i++)
	{
		if (DecodeChar(&(data[i]),stream))
		{
			*cmd = USART_NAK;
			return *cmd;
		}
	}

	// Finally we retrieve the CRC code
	// High byte
	uint16_t crc = 0xFFFF;
	if (DecodeChar(&buffer,stream))
	{
		*cmd = USART_NAK;
		return *cmd;
	}
	crc = ((uint16_t) buffer);
	crc = crc << 8;
	// Low byte
	if (DecodeChar(&buffer,stream))
	{
		*cmd = USART_NAK;
		return *cmd;
	}
	crc |= ((uint16_t) buffer);

	// Check that the stop flag is provided
	if (fgetc(stream) != USART_END)
	{
		*cmd = USART_NAK;
		return *cmd;
	}

	// Do a CRC check
	// We use a crc function provided by <util/crc16.h>
	uint16_t calculatedCrc = 0;
	calculatedCrc = _crc_xmodem_update(calculatedCrc,*cmd);
	calculatedCrc = _crc_xmodem_update(calculatedCrc,len);
	for (i = 0; i < len; i++)
	{
		calculatedCrc = _crc_xmodem_update(calculatedCrc,data[i]);
	}

	// The calculated crc should now be equal to the crc received.
	if (crc != calculatedCrc)
	{
		*cmd = USART_NAK;
		return *cmd;
	}

	return *cmd;
}

static void EncodeChar(uint8_t c, FILE *stream)
{
	if (c == USART_END)
	{
		putc(USART_ESC,stream);
		putc(USART_FLIPBIT ^ c,stream);
	}
	else if (c == USART_ESC)
	{
		putc(USART_ESC,stream);
		putc(USART_FLIPBIT ^ c,stream);
	}
	else 
	{
		putc(c,stream);
	}
}

// This is similar to getting a packet, see
// USART_GetPacket for more comments.
void USART_SendPacket(uint8_t cmd, char *data, FILE *stream)
{
	// Calculate the length of the data
	uint8_t len= (strlen(data));
	
	// Calculate the CRC code
	uint16_t crc = 0x0000;
	crc = _crc_xmodem_update(crc,cmd);
	crc = _crc_xmodem_update(crc,len);
	int i;
	for (i = 0; i < len; i++)
	{
		crc = _crc_xmodem_update(crc,data[i]);
	}

	// Send the packet
	putc(USART_START,stream);
	EncodeChar(cmd,stream);
	EncodeChar(len,stream);
	for (i = 0; i < len; i++)
	{
		EncodeChar((uint8_t) data[i],stream);
	}
	EncodeChar(((uint8_t) (crc >> 8)),stream);
	EncodeChar(((uint8_t) crc),stream);
	putc(USART_END,stream);

}

// Sendpacket without any data
void USART_SendCmd(uint8_t cmd, FILE *stream)
{
	// We still send length of the data which is 0
	uint8_t len = 0;
	
	// Calculate the CRC code
	uint16_t crc = 0x0000;
	crc = _crc_xmodem_update(crc,cmd);
	crc = _crc_xmodem_update(crc,len);

	// Send the packet
	putc(USART_START,stream);
	EncodeChar(cmd,stream);
	EncodeChar(len,stream);
	EncodeChar(((uint8_t) (crc >> 8)),stream);
	EncodeChar(((uint8_t) crc),stream);
	putc(USART_END,stream);

}


