#ifndef DAC_H
#define DAC_H

#include "SPI.h"
#include "IOMapping.h"

// Shortcuts for the DAC chip select pin
#define SELECT_DAC IOClearPin(DAC_CS_PORT,DAC_CS_PIN)
#define DESELECT_DAC IOSetPin(DAC_CS_PORT,DAC_CS_PIN)

// A driver for the LTC1661
void DAC_Initialize(void);
void DAC_transfer(unsigned char CTRL,uint16_t a);

#endif