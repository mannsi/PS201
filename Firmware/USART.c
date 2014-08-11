#include "USART.h"

FILE USART_input = FDEV_SETUP_STREAM(NULL,USART_GetChar,_FDEV_SETUP_READ);
FILE USART_output = FDEV_SETUP_STREAM(USART_PutChar,NULL,_FDEV_SETUP_WRITE);


void USART_Initialize(void)
{
  // Set transmit and receive registers
  IOSetOutput(UART_TRANSMIT_PORT,UART_TRANSMIT_PIN);
  IOEnablePullup(UART_RECEIVE_PORT,UART_RECEIVE_PIN);

  // Set BAUD rate
  BIT_SET(LINBTR,BIT(LDISR));
  LINBTR |= SAMPLES_PER_BIT;
  LINBRR = MYLINBRR;

  // Set LIN module to UART mode
  BIT_SET(LINCR,BIT(LCMD0));
  BIT_SET(LINCR,BIT(LCMD1));
  BIT_SET(LINCR,BIT(LCMD2));

  // Enable receiver and transmitter
  BIT_SET(LINCR,BIT(LENA));
}

int USART_PutChar(char c, FILE *stream)
{
  if(c == '\n')
  {
    USART_PutChar('\r',stream);
  }
  while ( !BIT_GET(LINSIR,BIT(LTXOK)) );
  LINDAT = c;
  return 0;
}

int USART_GetChar(FILE *stream)
{
  while ( !BIT_GET(LINSIR,BIT(LRXOK)) );
  return (int) LINDAT;
}

int USART_IsReceivingData()
{
  // The RXC0 bit of the UCSR0A register is set
  // when the buffer is loaded.
  if(BIT_GET(LINSIR,BIT(LRXOK)))
  {
    return 1;
  }
  // return 0 for no command
  return 0;
}


