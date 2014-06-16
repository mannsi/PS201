#ifndef Usb_h
#define Usb_h

#include "Device.h"
#include "SERIAL.h"

#define SERIAL_SEND_VOLTAGE 		(0xD0)
#define SERIAL_RECEIVE_VOLTAGE 		(0xC0)
#define SERIAL_SEND_CURRENT 		(0xD1)
#define SERIAL_RECEIVE_CURRENT 		(0xC1)
#define SERIAL_SEND_VIN	 			(0xD2)
#define SERIAL_SEND_VPREREG 		(0xD3)
#define SERIAL_ENABLE_OUTPUT		(0xC2)
#define SERIAL_DISABLE_OUTPUT		(0xC3)
#define SERIAL_IS_OUTPUT_ON  		(0xC4)
#define SERIAL_SEND_SET_VOLTAGE		(0xE0)
#define SERIAL_SEND_SET_CURRENT		(0xE1)
#define SERIAL_PROGRAM_ID			(0xA0)
#define SERIAL_WRITEALL				(0xA5)
#define SERIAL_WRITEALLCOMMANDS		(0xBB)
#define SERIAL_ENABLE_STREAM		(0xA2)
#define SERIAL_DISABLE_STREAM		(0xA3)

typedef struct Usb_response_struct {
  int command;
  char* data;
} Usb_response_struct;

void USB_Initialize(void);
Usb_response_struct USB_GetResponse(void);
void USB_WriteAcknowledge(void);
void USB_WriteNotAcknowledge(void);
void USB_WriteAllValues(char* all_values);

#endif
