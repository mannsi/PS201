#ifndef SPI_H
#define SPI_H

#include "IOHandler.h"

void SPI_Initialize(void);
void SPI_SendData(char);
char SPI_ReceiveData(void);

#endif
