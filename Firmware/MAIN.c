/************************************
*                                   *
*        DIGITAL PSU REV 4          *
*        Fridrik F Gautason         *
*        Gudbjorn Einarsson         *
*        Copyright 2014             *
*                                   *
*************************************/

#include "MAIN.h"

static void allValuesToString(State_struct state, char* string_array);
static void processUsbResponse(Usb_response_struct usb_response, State_struct state);

int main(void)
{
	USB_Initialize();
	Device_Initialize();

	while(1)
	{
		Usb_response_struct usb_response = USB_GetResponse();
		if (usb_response.command != 0)
		{
			State_struct state = Device_GetState();
			processUsbResponse(usb_response, state);
		}
	}
	return 0;
}

/*
 * Takes a State_struct object and converts it's values
 * into a series of ; seperated strings. These strings are
 * concatinated and store in char* string_array
 */
static void allValuesToString(State_struct state, char* string_array)
{
	char output_voltage_array[8];
	char output_current_array[8];
	char target_voltage_array[8];
	char target_current_array[8];
	char output_is_on_array[8];

	sprintf(output_voltage_array, "%i;", state.output_voltage);
	sprintf(output_current_array, "%i;", state.output_current);
	sprintf(target_voltage_array, "%i;", state.target_voltage);
	sprintf(target_current_array, "%i;", state.target_current);
	sprintf(output_is_on_array, "%i", state.output_on);

	strcpy(string_array, output_voltage_array);
	strcat(string_array, output_current_array);
	strcat(string_array, target_voltage_array);
	strcat(string_array, target_current_array);
	strcat(string_array, output_is_on_array);
}

static void processUsbResponse(Usb_response_struct usb_response, State_struct state)
{
	switch (usb_response.command)
	{
		case SERIAL_PROGRAM_ID:
			USB_WriteAcknowledge();
			break;
		case SERIAL_WRITEALL:
			USB_WriteAcknowledge();
			char all_values_array[50];
			allValuesToString(state, all_values_array);
			USB_WriteAllValues(all_values_array);
			break;
		case SERIAL_ENABLE_OUTPUT:
			USB_WriteAcknowledge();
			Device_TurnOutputOn();
			break;
		case SERIAL_DISABLE_OUTPUT:
			USB_WriteAcknowledge();
			Device_TurnOutputOff();
			break;
		case SERIAL_RECEIVE_VOLTAGE:
			USB_WriteAcknowledge();
			int voltage = atoi(usb_response.data);
			Device_SetTargetVoltage(voltage);
			break;
		case SERIAL_RECEIVE_CURRENT:
			USB_WriteAcknowledge();
			int current = atoi (usb_response.data);
			Device_SetTargetCurrent(current);
			break;
		default:
			USB_WriteNotAcknowledge();
			break;
	}
}
