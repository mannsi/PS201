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


int CurrentActive = 0;
State_struct deviceState;

static const int VoltageIncrement = 100;
static const int CurrentIncrement = 10;
static const int VoltageMaxValue = 20000;
static const int CurrentMaxValue = 1000;

// DEBUG STUFF
static void runDebugCode(void);
static void runTestCode(void);

int main(void)
{
	USB_Initialize();
	Device_Initialize();
    SWITCH_Initialize();
    // TODO Initialize screen

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
    }
    else if (strcmp(usb_response.cmd, SERIAL_RECEIVE_VOLTAGE) == 0)
    {
        USB_WriteAcknowledge();
        Device_SetTargetVoltage(usb_response.data);
    }
    else if (strcmp(usb_response.cmd, SERIAL_RECEIVE_CURRENT) == 0)
    {
        USB_WriteAcknowledge();
        Device_SetTargetCurrent(usb_response.data);
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
            CurrentActive = !CurrentActive;
            break;
        case DOWN:
            CurrentActive = !CurrentActive;
            break;
        case CANCEL:
            deviceState = Device_GetState();
            if (deviceState.output_on)
            {
                Device_TurnOutputOff();
            }
            else
            {
                Device_TurnOutputOn();
            }
            break;
        case ENTER:
            break;
        case CLOCKWISE:
            deviceState = Device_GetState();
            if (CurrentActive)
            {
                int newTargetCurrent = deviceState.target_current + CurrentIncrement;
                if (newTargetCurrent > CurrentMaxValue) break;
                Device_SetTargetCurrent(newTargetCurrent);
            }
            else
            {
                int newTargetVoltage = deviceState.target_voltage + VoltageIncrement;
                if (newTargetVoltage > VoltageMaxValue) break;
                Device_SetTargetVoltage(newTargetVoltage);
            }
            break;
        case COUNTERCLOCKWISE:
            deviceState = Device_GetState();
            if (CurrentActive)
            {
                int newTargetCurrent = deviceState.target_current - CurrentIncrement;
                if (newTargetCurrent < 0) break;
                Device_SetTargetCurrent(newTargetCurrent);
            }
            else
            {
                int newTargetVoltage = deviceState.target_voltage - VoltageIncrement;
                if (newTargetVoltage < 0) break;
                Device_SetTargetVoltage(newTargetVoltage);
            }
            break;
        default:
            break;
    }
}

