#include "DAC.h"

void DAC_Initialize(void)
{
  SPI_Initialize();
  IOSetOutput(DAC_CS_PORT,DAC_CS_PIN);
  DESELECT_DAC;
}

// For the DAC (LTC1661) we must give one 16bit word 
// first four bits are control code, the next eight 
// are the actual data and the last two are ignored.
void DAC_transfer(unsigned char CTRL,uint16_t dacData){
  // Make sure dacData is a ten bit word
  dacData &= 0x03FF;

  CTRL = CTRL << 4;

  // Now we can transfer this to the DAC
  // Take the DAC chip select low
  SELECT_DAC;
  // Transfer in two 8 bit steps
  SPI_SendData(CTRL | (dacData >> 6));
  SPI_SendData((dacData << 2) & 0x00FF);
  // Restore the chip select
  DESELECT_DAC;
}
