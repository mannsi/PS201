#include "SPI.h"

#define SPI_MOSI_PORT	portB
#define SPI_MOSI_PIN	3
#define SPI_MISO_PORT	portB
#define SPI_MISO_PIN	4
#define SPI_SCK_PORT	portB
#define SPI_SCK_PIN	5

void SPI_Initialize(void)
{
  // SS pin must be set as output
  IOSetOutput(portB,2);

  // Setup IO pins
  IOSetOutput(SPI_MOSI_PORT,SPI_MOSI_PIN);
  IOSetInput(SPI_MISO_PORT,SPI_MISO_PIN);
  IOSetOutput(SPI_SCK_PORT,SPI_SCK_PIN);

  // Enable SPI, Master, set clock rate fck/16
  SPCR = 0;
  BIT_SET(SPCR,BIT(MSTR));
  BIT_SET(SPCR,BIT(SPR0));
  BIT_SET(SPCR,BIT(SPE));
  //SPCR = (1<<SPE)|(1<<MSTR)|(1<<SPR0);
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
