#include "Device.h"

static float getCurrentMultiplier(void);
static float getVoltageSetMultiplier(void);
static float getVoltageReadMultiplier(void);
static uint16_t mapFromDevice(int device_value, float multiplier);
static uint16_t mapToDevice(int set_value, float multiplier);
static void StartMeasurement(void);
static void InitRegisters(void);

const float REFERENCE_VOLTAGE = 2.43;
const float SHUNT_RESISTOR = 0.2; // Ohms
const float CURRENT_AMPLIFIER_GAIN = 11.0;
const float VOLTAGE_AMPLIFIER_GAIN = 10.0;
const float VOLTAGE_MEASUREMENT_GAIN = 11.0;

State_struct state = {.output_on=0, .target_voltage=0, .target_current=0, .output_voltage=0, .output_current=0};

void Device_Initialize()
{
	ADC_Initialize();
	DAC_Initialize();
	InitRegisters();
	StartMeasurement();
}

void StartMeasurement(void)
{
	sei();
	ADC_StartMeasuringVoltage();
}

State_struct Device_GetState(void)
{
	int device_voltage = ADC_GetMeasuredVoltage();
	int device_current = ADC_GetMeasuredCurrent();
	float voltage_conversion_factor = getVoltageReadMultiplier();
	float current_conversion_factor = getCurrentMultiplier();
	
	state.output_voltage = mapFromDevice(device_voltage, voltage_conversion_factor);
	state.output_current = mapFromDevice(device_current, current_conversion_factor);
    return state;
}

/*
 * Sets the target voltage of the device. set_voltage is measured in mV
 */
void Device_SetTargetVoltage(int set_voltage)
{
	state.target_voltage = set_voltage;
	float voltage_mulitiplier = getVoltageSetMultiplier();
	uint16_t device_voltage_value = mapToDevice(set_voltage, voltage_mulitiplier);
    DAC_transfer(10, device_voltage_value);
}

/*
 * Sets the garget current value of the device. set_current is measured in mA
 */
void Device_SetTargetCurrent(int set_current)
{
	state.target_current = set_current;
	float current_mulitiplier = getCurrentMultiplier();
	uint16_t device_current_value = mapToDevice(set_current, current_mulitiplier);
    DAC_transfer(9, device_current_value);
}

void Device_TurnOutputOn()
{
	state.output_on = 1;
	IOClearPin(SHUTDOWN_PORT,SHUTDOWN_PIN);
	IOClearPin(PREREG_PORT,PREREG_PIN);
}

void Device_TurnOutputOff()
{
	state.output_on = 0;
	IOSetPin(PREREG_PORT,PREREG_PIN);
	IOSetPin(SHUTDOWN_PORT,SHUTDOWN_PIN);
}

/* 
 * Gets the mulitplier when converting between current set values and current device values
 */ 
static float getCurrentMultiplier()
{
  return REFERENCE_VOLTAGE/CURRENT_AMPLIFIER_GAIN/SHUNT_RESISTOR;
}

/* 
 * Gets the mulitplier when converting from voltage set value to voltage device value
 */ 
static float getVoltageSetMultiplier()
{
  return VOLTAGE_AMPLIFIER_GAIN*REFERENCE_VOLTAGE;
}

/* 
 * Gets the mulitplier when converting from voltage device value to voltage set value
 */ 
static float getVoltageReadMultiplier()
{
  return VOLTAGE_MEASUREMENT_GAIN*REFERENCE_VOLTAGE;
}

/*
 * Maps a value from device to a USB set value
 */  
static uint16_t mapFromDevice(int device_value, float multiplier)
{
	return (uint16_t) ((float) (device_value)*(multiplier));
}

/*
 *  Maps a set value from USB to a value the device understands
 */
static uint16_t mapToDevice(int set_value, float multiplier)
{
	return (uint16_t) ((float)(set_value))/(multiplier);
}

static void InitRegisters(void)
{
	// Turn off Bias
	IOSetOutput(SHUTDOWN_PORT,SHUTDOWN_PIN);
	IOSetOutput(PREREG_PORT,PREREG_PIN);
	IOSetPin(PREREG_PORT,PREREG_PIN); 
	IOSetPin(SHUTDOWN_PORT,SHUTDOWN_PIN);
}
