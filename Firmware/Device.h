#ifndef Device_H
#define Device_H

#include "Structs.h"

void Device_Initialize(void);
State_struct Device_GetState(void);
void Device_SetTargetVoltage(int targetVoltage_mV);
void Device_SetTargetCurrent(int targetCurrent_mA);
void Device_TurnOutputOn(void);
void Device_TurnOutputOff(void);

#endif
