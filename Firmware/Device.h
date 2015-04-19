#ifndef Device_H
#define Device_H

#include "IOHandler.h"
#include "IOMapping.h"
#include "DAC.h"
#include "ADC.h"
#include "EEPROM.h"
#include "Structs.h"

void Device_Initialize(void);
State_struct Device_GetState(void);
void Device_SetTargetVoltage(int voltage);
void Device_SetTargetCurrent(int current);
void Device_TurnOutputOn(void);
void Device_TurnOutputOff(void);

#endif
