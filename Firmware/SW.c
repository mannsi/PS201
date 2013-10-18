#include "SW.h"

unsigned char SW_state = 0xff;
unsigned char encoderControls = VOLTAGE;


void SW_Initialize(void)
{
	// Set up switches
	DDRD &= ~1 << PD2;	// Sw3 (interupt pin)
	PORTD |= 1 << PD2;	// Turn on pull-up
	DDRD &= ~1 << PD3;	// Sw2 (interupt pin)
	PORTD |= 1 << PD3;
	DDRD &= ~1 << PD4;	// Sw1
	PORTD |= 1 << PD4;

	// Set up rotary encoder
	DDRC &= ~1 << PC3;	// Pin A
	PORTC |= 1 << PC3;
	DDRC &= ~1 << PC4;	// Pin B
	PORTC |= 1 << PC4;
	DDRC &= ~1 << PC5;	// Encoder Sw
	PORTC |= 1 << PC5;
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
	{ 0, 	1,  4, 	0	},	// start at 00
	{ 0, 	1, 	0, 	0x12},	// CW  from 00
	{ 2, 	5, 	3, 	2	},	// start at 11
	{ 0x10, 2, 	3, 	2	},  // CW  from 11
	{ 0,	0,	4,	0x22},	// CCW from 00
	{ 0x20,	5,	2,	2	},	// CCW from 11
};


unsigned char SW_CheckEncoder()
{
	SW_encoderState = rotaryTable[SW_encoderState & 0x0f][ENCODER];
	return SW_encoderState & 0x30;	
}

// Check switch functions for all switches
unsigned char SW_Check1(void)
{
	if (SW1_IS_CLOSED && (SW_state & SW1_WAS_OPEN))
	{
		_delay_ms(2);
		if (SW1_IS_CLOSED)
		{
			SW_state &= ~SW1_WAS_OPEN;
			return 1;
		}
	}
	if (SW1_IS_OPEN && !(SW_state & SW1_WAS_OPEN))
	{
		_delay_ms(2);
		if(SW1_IS_OPEN)
			SW_state |= SW1_WAS_OPEN;
	}
	return 0;
}

unsigned char SW_Check2(void)
{
	if (SW2_IS_CLOSED && (SW_state & SW2_WAS_OPEN))
	{
		_delay_ms(2);
		if (SW2_IS_CLOSED)
		{
			SW_state &= ~SW2_WAS_OPEN;
			return 1;
		}
	}
	if (SW2_IS_OPEN && !(SW_state & SW2_WAS_OPEN))
	{
		_delay_ms(2);
		if(SW2_IS_OPEN)
			SW_state |= SW2_WAS_OPEN;
	}
	return 0;
}

unsigned char SW_Check3(void)
{
	if (SW3_IS_CLOSED && (SW_state & SW3_WAS_OPEN))
	{
		_delay_ms(2);
		if (SW3_IS_CLOSED)
		{
			SW_state &= ~SW3_WAS_OPEN;
			return 1;
		}
	}
	if (SW3_IS_OPEN && !(SW_state & SW3_WAS_OPEN))
	{
		_delay_ms(2);
		if(SW3_IS_OPEN)
			SW_state |= SW3_WAS_OPEN;
	}
	return 0;
}

unsigned char SW_Check4(void)
{
	if (SW4_IS_CLOSED && (SW_state & SW4_WAS_OPEN))
	{
		_delay_ms(2);
		if (SW4_IS_CLOSED)
		{
			SW_state &= ~SW4_WAS_OPEN;
			return 1;
		}
	}
	if (SW4_IS_OPEN && !(SW_state & SW4_WAS_OPEN))
	{
		_delay_ms(2);
		if(SW4_IS_OPEN)
		SW_state |= SW4_WAS_OPEN;
	}
	return 0;
}
