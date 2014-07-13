#ifndef EEPROM_H
#define EEPROM_H

#include <avr/eeprom.h>

int EEPROM_GetTargetVoltage(void);
int EEPROM_GetTargetCurrent(void);
int EEPROM_GetDeviceIsOn(void);
void EEPROM_SetTargetVoltage(int voltage);
void EEPROM_SetTargetCurrent(int current);
void EEPROM_SetDeviceOutputOn(void);
void EEPROM_SetDeviceOutputOff(void);

#endif
