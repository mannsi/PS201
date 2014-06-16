#ifndef Device_H
#define Device_H

#include "IOHandler.h"
#include "IOMapping.h"
#include "DAC.h"
#include "ADC.h"

typedef struct State_struct {
  int output_on;
  int target_voltage;
  int target_current;
  int output_voltage;
  int output_current;
} State_struct;

void Device_Initialize(void);
State_struct Device_GetState(void);
void Device_SetTargetVoltage(int voltage);
void Device_SetTargetCurrent(int current);
void Device_TurnOutputOn(void);
void Device_TurnOutputOff(void);

static float getCurrentMultiplier(void);
static float getVoltageSetMultiplier(void);
static float getVoltageReadMultiplier(void);
static uint16_t mapFromDevice(int device_value, float multiplier);
static uint16_t mapToDevice(int set_value, float multiplier);
static void StartMeasurement(void);

#endif
