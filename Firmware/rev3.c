/************************************
*                                   *
*        DIGITAL PSU REV 3          *
*        Fridrik F Gautason         *
*        Gudbjorn Einarsson         *
*        Copyright 2014             *
*                                   *
*************************************/

#include "rev3.h"

#include "Usb.h"
#include "Device.h"
#include "Structs.h"
#include "Switch.h"
#include "Debug.h"
#include "Tests.h"
#include "IOHandler.h"
#include "Display.h"
#include <util/delay.h>
#include <string.h>


#define SERIAL_RECEIVE_VOLTAGE 		"VOL"
#define SERIAL_RECEIVE_CURRENT 		"CUR"
#define SERIAL_ENABLE_OUTPUT		"OUT"
#define SERIAL_PROGRAM_ID		    "HAN"
#define SERIAL_WRITEALL			    "WRT"

/*
 * Takes the state of the hardware and puts its values in string_array.
 * The format of the string_array is:
 output_voltage[mV];output_current[mA];target_voltage[mV];target_current[mA];output_on[int_bool]
 * Returns: Length of string_array
 */
static uint8_t allValuesToString(State_struct state, char* string_array);

/*
 * Processes the input from parameter reponse. Uses the parameter state if needed.
 */
static void processUsbResponse(Decoded_input response, State_struct state);

/*
 * Process input from the physical buttons on the device
 */
static void processSwitches(UICommand command);

/*
 * Sends the current device state on screen.
 * param showTargetVoltage: If target voltage should be shown or output voltage
 * param showTargetCurrent: If target current should be shown or output current
 */
static void displayDeviceState(int showTargetVoltage, int showTargetCurrent);

static const int StandardDelay = 5000;
static const int VoltageIncrement = 100;
static const int CurrentIncrement = 10;
static const int VoltageMaxValue = 20000;
static const int CurrentMaxValue = 1000;
static const uint8_t backlightIntensity = 10;
static const uint8_t contrast = 10;

int VoltageActive = 1;
int DisplayDelayCounter = 0;
State_struct deviceState;

// DEBUG STUFF
static void runDebugCode(void);
static void runTestCode(void);

int main(void)
{
    DISPLAY_Initialize(backlightIntensity,contrast);
	USB_Initialize();
	Device_Initialize();
    SWITCH_Initialize();
    DISPLAY_StartScreen();

    _delay_ms(1000);

    displayDeviceState(0,0);
	//runTestCode();
    //return 0;

    //runDebugCode();
    //return 0;

	while(1)
    {
        Decoded_input response;

        int usbResponse = USB_GetResponse(&response);
		if (usbResponse == 1)
		{
			State_struct state = Device_GetState();
			processUsbResponse(response, state);
		}
		else if (usbResponse == -1)
		{
            USB_WriteNotAcknowledge();
		}
        else
        {
            UICommand newUICommand = SWITCH_readUI();
            processSwitches(newUICommand);
        }

        if (DisplayDelayCounter > 0)
        {
            DisplayDelayCounter--;
            if (DisplayDelayCounter == 0)
            {
                displayDeviceState(0,0);
            }
        }
    }
	return 0;
}

static void runTestCode()
{
    TestSerialParser();
}

// Prints predefined usb code every 1 second and blocks everything else
static void runDebugCode()
{
    char* data1 = "10000";

    while(1)
    {
        USB_WriteAllValues(data1, strlen(data1));
        putchar ('\n');
        USB_WriteNotAcknowledge();
        putchar ('\n');
        USB_WriteAcknowledge();
        putchar ('\n');

        _delay_ms(1000);
    }
}

static uint8_t allValuesToString(State_struct state, char* string_array)
{
    uint8_t dataLength = 0;

	char output_voltage_array[8];
	char output_current_array[8];
	char target_voltage_array[8];
	char target_current_array[8];
	char output_is_on_array[8];

	dataLength += sprintf(output_voltage_array, "%i;", state.output_voltage);
	dataLength += sprintf(output_current_array, "%i;", state.output_current);
	dataLength += sprintf(target_voltage_array, "%i;", state.target_voltage);
	dataLength += sprintf(target_current_array, "%i;", state.target_current);
	dataLength += sprintf(output_is_on_array, "%i", state.output_on);

	strcpy(string_array, output_voltage_array);
	strcat(string_array, output_current_array);
	strcat(string_array, target_voltage_array);
	strcat(string_array, target_current_array);
	strcat(string_array, output_is_on_array);

	return dataLength;
}

static void processUsbResponse(Decoded_input usb_response, State_struct state)
{
    if (strcmp(usb_response.cmd, SERIAL_PROGRAM_ID) == 0)
    {
        USB_WriteAcknowledge();
    }
    else if (strcmp(usb_response.cmd, SERIAL_WRITEALL) == 0)
    {
        USB_WriteAcknowledge();
        char all_values_array[50];
        uint8_t dataLength = allValuesToString(state, all_values_array);
        USB_WriteAllValues(all_values_array, dataLength);
    }
    else if (strcmp(usb_response.cmd, SERIAL_ENABLE_OUTPUT) == 0)
    {
        if (usb_response.data)
        {
            USB_WriteAcknowledge();
			Device_TurnOutputOn();
        }
        else
        {
            USB_WriteAcknowledge();
			Device_TurnOutputOff();
        }
        DisplayDelayCounter = StandardDelay;
    }
    else if (strcmp(usb_response.cmd, SERIAL_RECEIVE_VOLTAGE) == 0)
    {
        USB_WriteAcknowledge();
        Device_SetTargetVoltage(usb_response.data);
        DisplayDelayCounter = StandardDelay;
    }
    else if (strcmp(usb_response.cmd, SERIAL_RECEIVE_CURRENT) == 0)
    {
        USB_WriteAcknowledge();
        Device_SetTargetCurrent(usb_response.data);
        DisplayDelayCounter = StandardDelay;
    }
    else
    {
        USB_WriteNotAcknowledge();
    }
}

static void processSwitches(UICommand command)
{
    switch(command){
        case NO_UI_COMMAND:
            break;
        case UP:
            VoltageActive = 0;
            displayDeviceState(0,0);
            break;
        case CANCEL:
            VoltageActive = 1;
            displayDeviceState(0,0);
            break;
        case DOWN:
            deviceState = Device_GetState();
            if (deviceState.output_on)
            {
                Device_TurnOutputOff();
            }
            else
            {
                Device_TurnOutputOn();
            }
            displayDeviceState(0,0);
            DisplayDelayCounter = StandardDelay;
            break;
        case ENTER:
            break;
        case CLOCKWISE:
            deviceState = Device_GetState();
            if (VoltageActive)
            {
                int newTargetVoltage = deviceState.target_voltage + VoltageIncrement;
                if (newTargetVoltage > VoltageMaxValue) break;
                Device_SetTargetVoltage(newTargetVoltage);
                displayDeviceState(1,0);
            }
            else
            {
                int newTargetCurrent = deviceState.target_current + CurrentIncrement;
                if (newTargetCurrent > CurrentMaxValue) break;
                Device_SetTargetCurrent(newTargetCurrent);
                displayDeviceState(0,1);
            }

            DisplayDelayCounter = StandardDelay;
            break;
        case COUNTERCLOCKWISE:
            deviceState = Device_GetState();
            if (VoltageActive)
            {
                int newTargetVoltage = deviceState.target_voltage - VoltageIncrement;
                if (newTargetVoltage < 0) break;
                Device_SetTargetVoltage(newTargetVoltage);
                displayDeviceState(1,0);
            }
            else
            {
                int newTargetCurrent = deviceState.target_current - CurrentIncrement;
                if (newTargetCurrent < 0) break;
                Device_SetTargetCurrent(newTargetCurrent);
                displayDeviceState(0,1);
            }

            DisplayDelayCounter = StandardDelay;
            break;
        default:
            break;
    }
}

static void displayDeviceState(int showTargetVoltage, int showTargetCurrent)
{
    State_struct state = Device_GetState();
    char* vol = "OUT";
    char* cur = "OUT";

    int displayVoltage = state.output_voltage;
    int displayCurrent = state.output_current;
    if (showTargetVoltage == 1 || !state.output_on)
    {
        displayVoltage = state.target_voltage;
    }

    if (showTargetCurrent == 1 || !state.output_on)
    {
        displayCurrent = state.target_current;
    }

    char voltageArray[8];
    voltageArray[0] = displayVoltage < 10000 ? ' ' : (char) ( ((int) '0') + displayVoltage / 10000 );
    voltageArray[1] = displayVoltage < 1000  ? '0' : (char) ( ((int) '0') + (displayVoltage%10000) / (1000) );
    voltageArray[2] = '.';
    voltageArray[3] = (char) ( ((int) '0') + (displayVoltage%1000)/100);
    voltageArray[4] = (char) ( ((int) '0') + (displayVoltage%100)/10);
    voltageArray[5] = ' ';
    voltageArray[6] = 'V';
    voltageArray[7] = '\0';

    char currentArray[8];
    currentArray[0] = ' ';
    currentArray[1] = displayCurrent < 100  ? '0' : (char) ( ((int) '0') + (displayCurrent%1000) / (100) );
    currentArray[2] = '.';
    currentArray[3] = (char) ( ((int) '0') + (displayCurrent%100)/10);
    currentArray[4] = (char) ( ((int) '0') + (displayCurrent%10));
    currentArray[5] = ' ';
    currentArray[6] = 'A';
    currentArray[7] = '\0';

    DISPLAY_HomeScreen(voltageArray, currentArray, state.output_on, VoltageActive);
}

