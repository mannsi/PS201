#ifndef rev3_H
#define rev3_H

#include "Usb.h"
#include "Device.h"
#include "DAC.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main(void);

static void allValuesToString(State_struct state, char* string_array);
static void processUsbResponse(Usb_response_struct usb_response, State_struct state);

#endif
