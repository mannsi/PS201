#ifndef LCD_H
#define LCD_H

#include<avr/io.h>
#include "SW.h"

#ifndef F_CPU
#define F_CPU 16000000
#endif
#include<util/delay.h>

// shortcuts for display 
#define ENABLE_DISPLAY PORTD |= 1 << PD5
#define DISABLE_DISPLAY PORTD &= ~(1 << PD5)
#define SELECT_DISPLAY PORTD &= ~(1 << PD6)
#define DESELECT_DISPLAY PORTD |= (1 << PD6)

// shortcut for output enable
#define ENABLE_OUTPUT PORTB |= 1 << PB0
#define DISABLE_OUTPUT PORTB &= ~(1 << PB0)
#define OUTPUT_IS_ENABLED PORTB & (1 << PB0)

void LCD_Initialize(void);
void LCD_Write(unsigned char* data);
void LCD_Cursor(unsigned char row, unsigned char column);
void LCD_Clear(void);
void LCD_HighLight(void);
void LCD_NoHighLight(void);
void LCD_ShowStartScreen(void);
void LCD_WriteValues(unsigned char* voltage,unsigned char* current);
uint8_t LCD_SetBacklight(uint8_t backlightIntensity);
void LCD_SwitchOutput(void);

static void LCD_Command(unsigned char a);
static void LCD_Data(unsigned char a);

#endif
