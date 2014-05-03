#include "SPI.h"

void SPI_Initialize(void)
{
  // Setup IO pins
  IOSetOutput(SPI_MOSI_PORT,SPI_MOSI_PIN);
  IOSetInput(SPI_MISO_PORT,SPI_MISO_PIN);
  IOSetOutput(SPI_SCK_PORT,SPI_SCK_PIN);
  
  // Enable SPI, Master, set clock rate fck/16
  SPCR = 0;
  BIT_SET(SPCR,BIT(SPE));
  BIT_SET(SPCR,BIT(MSTR));
  BIT_SET(SPCR,BIT(SPR0));
}

void SPI_SendData(char data)
{
  // Start transmission
  SPDR = data;
  // And wait until it completes
  while(!BIT_GET(SPSR,BIT(SPIF)));
}

char SPI_ReceiveData(void)
{
  // Wait for the reception to complete
  while(!BIT_GET(SPSR,BIT(SPIF)));
  // Return the data register
  return SPDR;
}