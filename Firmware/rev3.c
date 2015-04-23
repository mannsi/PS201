/************************************
*                                   *
*        DIGITAL PSU REV 3          *
*        Fridrik F Gautason         *
*        Gudbjorn Einarsson         *
*        Copyright 2014             *
*                                   *
*************************************/

#include "rev3.h"

#include "Debug.h"

#define SERIAL_RECEIVE_VOLTAGE 		"VOL"
#define SERIAL_RECEIVE_CURRENT 		"CUR"
#define SERIAL_ENABLE_OUTPUT		"OUT"
#define SERIAL_PROGRAM_ID		    "HAN"

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

// DEBUG STUFF
static void runDebugCode(void);
static void runTestCode(void);

int main(void)
{
	USB_Initialize();
	Device_Initialize();

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

