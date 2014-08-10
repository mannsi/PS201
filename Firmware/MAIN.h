#ifndef REV3_H
#define REV3_H

#include<avr/io.h>
#include<avr/interrupt.h>
#include <util/atomic.h>
#include<string.h>
#include<stdlib.h>
#include "IOMapping.h"
#include "DISPLAY.h"
#include "SWITCH.h"
#include "ADC.h"
#include "DAC.h"
#include "SERIAL.h"
#include "EEPROM.h"

// Shortcuts for enabling and disabling the output
#define ENABLE_OUTPUT  IOClearPin(SHUTDOWN_PORT,SHUTDOWN_PIN)
#define DISABLE_OUTPUT IOSetPin(SHUTDOWN_PORT,SHUTDOWN_PIN)
#define ENABLE_PREREG  IOClearPin(PREREG_PORT,PREREG_PIN)
#define DISABLE_PREREG IOSetPin(PREREG_PORT,PREREG_PIN)

extern button switch1, switch2, switch3, switch4;

int main(void);
void mapVoltage(uint16_t volt, unsigned char* b);
void mapCurrent(uint16_t cur, unsigned char* b);
void mapToVoltage(uint16_t* volt, unsigned char* b);
void mapToCurrent(uint16_t* cur, char* b);

// Voltage or current values in both digital domain
// and analog domain, with corresponding calibration
// values:
// analog = digital*multiplier + offset
typedef struct {
  uint16_t analog;
  uint16_t digital;
  uint32_t average;
  uint16_t numberOfSamples;
  float multiplier;
  uint16_t offset;
  uint16_t maxAnalogValue; // 2000 corresponds to 20V
  uint16_t analogIncrements;
} PSUData;
// Mapping functions that act on PSUData, returns the 
// mapped to value.
uint16_t mapToAnalog(PSUData*);
uint16_t mapToDigital(PSUData*);
void mapToString(PSUData*,char*);
void mapToNum(PSUData*,char*);

// Calibration initialization
float getVoltageSetMultiplier(void);
float getVoltageReadMultiplier(void);
float getCurrentMultiplier(void);

// Some more manipulations on the PSUData
void increaseAnalog(PSUData*);
void decreaseAnalog(PSUData*);

// Serial Commands
typedef enum {
  NO_SERIAL_COMMAND,
  NEW_VOLTAGE,
  NEW_CURRENT,
  OUTPUT_ON,
  OUTPUT_OFF,
} serialCommand;
// returns 0 if a no new output setting is received.
serialCommand readUSB(void);
void logToUSB(PSUData*,serialCommand);

// ADC is multiplexed, we need a variable to
// track which peripheral is being measured
typedef enum {
  VOLTAGE,
  CURRENT,
  PREREG,
  VIN,
} ADC_MUX;
// returns 1 if a new reading was recorded, otherwise 0.
int readFromADC(PSUData*);
void startADC(ADC_MUX*);

// UI commands
typedef enum {
  NO_UI_COMMAND,
  UP,
  DOWN,
  ENTER,
  CANCEL,
  CLOCKWISE,
  COUNTERCLOCKWISE,
} UICommand;
// readUI reads the physical switches on the device and
// returns a command which is interpreted based on the
// state of the device.
UICommand readUI(void);

// The UI is essentially run as a state machine
typedef enum {
  NORMAL,
  USBCONTROLLED,
  MENU,
  CALIBRATION,
} PSUState;
PSUState setState(PSUState);





void toggleOutput(void);
void enableOutput(void);
void disableOutput(void);

void writeToUsb(uint16_t voltage, 
		uint16_t current, 
		uint16_t voltageSet, 
		uint16_t currentSet, 
		uint16_t inputVoltage,
		uint16_t vinVoltage,
		unsigned char outputOn);

static void initRegistries(void);






// void doCalibration(void);

void joinArrays(unsigned char *voltageArray, 
		unsigned char *currentArray, 
		unsigned char *voltageSetArray, 
		unsigned char *currentSetArray,
		unsigned char *voltagePreregArray,
		unsigned char *voltageVinArray,
		unsigned char outputOn,
		unsigned char *combinedArray);

int appendArray(unsigned char *targetArray, 
		int arraySize, 
		unsigned char *appendingArray, 
		int appendingArrayMaxSize);

void clearArray(unsigned char *array, int size);

#endif
