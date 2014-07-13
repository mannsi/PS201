#include "EEPROM.h"

#define ADDR_VOLTAGE	10
#define ADDR_CURRENT	20
#define ADDR_DEVICE_ON	30


static int getValue(int address);
static void setValue(int value,int address);


void EEPROM_SetTargetCurrent(int current)
{
    setValue(current, ADDR_CURRENT);
}

void EEPROM_SetDeviceOutputOn(void)
{
    setValue(1, ADDR_DEVICE_ON);
}

void EEPROM_SetDeviceOutputOff(void)
{
    setValue(0, ADDR_DEVICE_ON);
}

void EEPROM_SetTargetVoltage(int voltage)
{
    setValue(voltage, ADDR_VOLTAGE);
}

int EEPROM_GetTargetVoltage(void)
{
    return getValue(ADDR_VOLTAGE);
}

int EEPROM_GetTargetCurrent(void)
{
    return getValue(ADDR_CURRENT);
}

int EEPROM_GetDeviceIsOn(void)
{
    return getValue(ADDR_DEVICE_ON);
}

static int getValue(int address)
{
    int value = eeprom_read_word((uint16_t*)address);
    if (value == -1)
    {
        return 0;
    }
    return value;
}

static void setValue(int value,int address)
{
	eeprom_write_word((uint16_t*)address,value);
}

