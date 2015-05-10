#include "DAC.h"

#include "SPI.h"

#define DAC_CS_PORT	portD
#define DAC_CS_PIN	7

// Shortcuts for the DAC chip select pin
#define SELECT_DAC IOClearPin(DAC_CS_PORT,DAC_CS_PIN)
#define DESELECT_DAC IOSetPin(DAC_CS_PORT,DAC_CS_PIN)

void DAC_Initialize(void)
{
    SPI_Initialize();
    IOSetOutput(DAC_CS_PORT,DAC_CS_PIN);
    DESELECT_DAC;
}


void DAC_SetValue(unsigned char data_type,uint16_t data){
    // For the DAC (LTC1661) we must give one 16bit word
    // first four bits are control code, the next eight
    // are the actual data and the last two are ignored.

    // Make sure data is a ten bit word
    data &= 0x03FF;

    data_type = data_type << 4;

    // Now we can transfer this to the DAC
    // Take the DAC chip select low
    SELECT_DAC;

    // Transfer in two 8 bit steps
    SPI_SendData(data_type | (data >> 6));
    SPI_SendData((data << 2) & 0x00FF);

    // Restore the chip select
    DESELECT_DAC;
}
