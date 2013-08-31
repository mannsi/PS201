#ifndef LCD_H
#define LCD_H

#include<avr/io.h>
#include<stdio.h>

#ifndef F_CPU
#define F_CPU 16000000
#endif
#include<util/delay.h>

// shortcuts for display 
#define ENABLE_DISPLAY PORTD |= 1 << PD5
#define DISABLE_DISPLAY PORTD &= ~(1 << PD5)
#define SELECT_DISPLAY PORTD &= ~(1 << PD6)
#define DESELECT_DISPLAY PORTD |= (1 << PD6)

void LCD_Initialize(void);
void LCD_Write(unsigned char* data);
void LCD_WriteFloat(uint16_t num);
void LCD_Cursor(unsigned char row, unsigned char column);
void LCD_Clear(void);


static void LCD_Command(unsigned char a);
static void LCD_Data(unsigned char a);

#endif
