#ifndef SWITCH_H
#define SWITCH_H

#include "IOHandler.h"
#include<util/delay.h>

// Switches
#define SW1_PORT	portD
#define SW1_PIN		4
#define SW2_PORT	portD
#define SW2_PIN		3
#define SW3_PORT	portD
#define SW3_PIN		2
#define SW4_PORT	portC
#define SW4_PIN		5
#define ENCODERA_PORT	portC
#define ENCODERA_PIN	3
#define ENCODERB_PORT	portC
#define ENCODERB_PIN	4


typedef struct
{
    port *switchPort;
    pin switchPin;
    unsigned char state;
} button;

extern button switch1, switch2, switch3, switch4;


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



void SWITCH_Initialize(void);

// readUI reads the physical switches on the device and
// returns a command which is interpreted based on the
// state of the device.
UICommand SWITCH_readUI(void);


unsigned char SWITCH_Pressed(button *b);
unsigned char SW_CheckEncoder(void);


// Needs to be rewritten:
// To keep up with the encoder
#define ENCODER ((PINC >> PC3) & 0x03)
#define ENCODER_CCW 0x10


#endif
