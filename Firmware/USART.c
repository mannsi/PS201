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

int USART_IsReceivingData()
{
  // The RXC0 bit of the UCSR0A register is set
  // when the buffer is loaded.
  if(BIT_GET(UCSR0A,BIT(RXC0)))
  {
    return 1;
  }
  // return 0 for no command
  return 0;
}


