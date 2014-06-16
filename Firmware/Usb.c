#include "Usb.h"

void USB_Initialize(void)
{
    SERIAL_Initialize();
}

Usb_response_struct USB_GetResponse(void)
{
	Usb_response_struct usb_response = {.command=0};
	
	if (SERIAL_IsReceivingData())
	{
		uint8_t cmd = 0;
		char data[MAXLEN];
		
		if(SERIAL_GetPacket(&cmd,data))
		{
			usb_response.command = cmd;
			usb_response.data = data;
		}
	}
	return usb_response;
}

void USB_WriteAcknowledge(void)
{
    SERIAL_SendCmd(SERIAL_ACK);
}

void USB_WriteNotAcknowledge(void)
{
    SERIAL_SendCmd(SERIAL_NAK);
}

void USB_WriteAllValues(char* all_values)
{
	SERIAL_SendPacket(SERIAL_WRITEALL, all_values);
}
