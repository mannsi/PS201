#ifndef Usb_h
#define Usb_h

#include "Structs.h"
#include <stdio.h>

void USB_Initialize(void);

/*
 * Fetches data packet from serial. Result stored in response
 * Returns: Bool if succesfull
 */
int USB_GetResponse(Decoded_input* response);
void USB_WriteAcknowledge(void);
void USB_WriteNotAcknowledge(void);
void USB_WriteAllValues(char* all_values, uint8_t allValuesLength);

#endif
