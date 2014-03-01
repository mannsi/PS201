#ifndef EEPROM_H
#define EEPROM_H

#define ADDR_STARTVOLTAGE	0xA0
#define ADDR_STARTCURRENT	0xA2
#define ADDR_CALIBRATION	0xD0

#include <avr/eeprom.h>
uint16_t EEPROM_ReadNum(unsigned char);
void EEPROM_WriteNum(uint16_t num,unsigned char);

#endif
