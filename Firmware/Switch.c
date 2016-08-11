#include "Switch.h"

// Generic initialization
static void SWITCH_InitializeButton(button *b);
// Returns one if switch state is updated
static unsigned char SWITCH_UpdateState(button *b);
static unsigned char SWITCH_GetState(button *b);
static unsigned char SW_encoderState;

// Switches
button switch1 = {.switchPort = &SW1_PORT, .switchPin = SW1_PIN, .state = 0};
button switch2 = {.switchPort = &SW2_PORT, .switchPin = SW2_PIN, .state = 0};
button switch3 = {.switchPort = &SW3_PORT, .switchPin = SW3_PIN, .state = 0};
button switch4 = {.switchPort = &SW4_PORT, .switchPin = SW4_PIN, .state = 0};

void SWITCH_Initialize()
{
    SWITCH_InitializeButton(&switch1);
    SWITCH_InitializeButton(&switch2);
    SWITCH_InitializeButton(&switch3);
    SWITCH_InitializeButton(&switch4);

    // Set up rotary encoder
    IOSetInput(ENCODERA_PORT,ENCODERA_PIN);
    IOEnablePullup(ENCODERA_PORT,ENCODERA_PIN);
    IOSetInput(ENCODERB_PORT,ENCODERB_PIN);
    IOEnablePullup(ENCODERB_PORT,ENCODERB_PIN);
}

UICommand SWITCH_readUI(void)
{
    if (SWITCH_Pressed(&switch1)) return CANCEL;
    if (SWITCH_Pressed(&switch4)) return ENTER;
    unsigned char encoderTurnDirection = SW_CheckEncoder();
    if(encoderTurnDirection)
    {
        if(encoderTurnDirection == ENCODER_CCW) return COUNTERCLOCKWISE;
        else return CLOCKWISE;
    }
    if (SWITCH_Pressed(&switch2)) return UP;
    if (SWITCH_Pressed(&switch3)) return DOWN;
    return NO_UI_COMMAND;
}

static void SWITCH_InitializeButton(button *b)
{
    // Setup the hardware
    IOSetInput(*(b->switchPort),(b->switchPin));
    IOEnablePullup(*(b->switchPort),(b->switchPin));
    // Record the state and initialize variables
    b->state = IOGetPin(*(b->switchPort),(b->switchPin));
}

static unsigned char SWITCH_UpdateState(button *b)
{
    unsigned char newState = IOGetPin(*(b->switchPort),(b->switchPin));
    if(newState != b->state)
    {
        // Debounce for 2 ms
        _delay_ms(2);
        newState = IOGetPin(*(b->switchPort),(b->switchPin));
        if(newState != b->state)
        {
            b->state = newState;
            return 1;
        }
    }
    return 0;
}

static unsigned char SWITCH_GetState(button *b)
{
    return b->state;
}

unsigned char SWITCH_Pressed(button *b)
{
    return (SWITCH_UpdateState(b) && !SWITCH_GetState(b));
}

// We use the following table to read the rotary encoder correctly
// in order to register a "click" the encoder must go through five
// states:
//	00 -> 01 -> 11 
//	11 -> 10 -> 00
// for clockwise and
//	00 -> 10 -> 11 
//	11 -> 01 -> 00
// for counter clockwise. We will make use of this WHOLE chain to
// determine the order of direction and to midigate any bounce.
// The first entry in the table (the row) is the previous state,
// the second entry is the current read state.
const unsigned char rotaryTable[6][4] = {
// 00 is an arbitrary state, and here considered the
// starting state of the encoder.
//  {00,   01, 10, 11}	for reference
        { 0,    1,    4,    0    },// start at 00
        { 0,    1,    0,    0x12 },// CW  from 00
        { 2,    5,    3,    2    },// start at 11
        { 0x10, 2,    3,    2    },// CW  from 11
        { 0,    0,    4,    0x22 },// CCW from 00
        { 0x20, 5,    2,    2    },// CCW from 11
};


unsigned char SW_CheckEncoder()
{
    SW_encoderState = rotaryTable[SW_encoderState & 0x0f][ENCODER];
    return SW_encoderState & 0x30;
}

