#include "EEPROM.h"

uint16_t EEPROM_ReadNum(unsigned char address)
{
	uint16_t num = eeprom_read_word((uint16_t*)address);
	if (num==0xFFFF)
	{
		num = 0;
	}
	return num;
}

void EEPROM_WriteNum(uint16_t num,unsigned char address)
{
	eeprom_write_word((uint16_t*)address,num);
}
	
