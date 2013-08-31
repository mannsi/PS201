#ifndef REV2_H
#define REV2_H

#include<avr/io.h>
#include<avr/interrupt.h>
#include "LCD.h"
#include "SW.h"
#include "ADC.h"
#include "USART.h"



// Shortcuts for the DAC chip select pin
#define SELECT_DAC PORTD &= ~(1 << PD7)
#define DESELECT_DAC PORTD |= (1 << PD7)

// shortcut for output enable
#define ENABLE_OUTPUT PORTB |= 1 << PB0
#define DISABLE_OUTPUT PORTB &= ~(1 << PB0)
#define OUTPUT_IS_ENABLED PORTB & (1 << PB0)

int main(void);
void transferToDAC(unsigned char CTRL,uint16_t a);
void MENU_Home(void);
void MENU_Backlight(void);

extern uint8_t backlight;

#endif
