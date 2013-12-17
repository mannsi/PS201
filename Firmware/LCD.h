#ifndef LCD_H
#define LCD_H

#include<avr/io.h>
#include "SW.h"
#include "rev3.h"

#ifndef F_CPU
#define F_CPU 16000000
#endif
#include<util/delay.h>

// shortcuts for display 
#define ENABLE_DISPLAY PORTD |= 1 << PD5
#define DISABLE_DISPLAY PORTD &= ~(1 << PD5)
#define SELECT_DISPLAY PORTD &= ~(1 << PD6)
#define DESELECT_DISPLAY PORTD |= (1 << PD6)

void LCD_Initialize(uint8_t backlight, uint8_t contrast);
void LCD_Write(unsigned char* data);
void LCD_Cursor(uint8_t row, uint8_t column);
void LCD_Clear(void);
void LCD_HighLight(void);
void LCD_NoHighLight(void);
void LCD_StartScreen(void);
void LCD_HomeScreen(uint16_t v,uint16_t c, uint8_t outputOn);
void LCD_WriteControlArrow(void);
int LCD_SetBacklight(uint8_t backlightIntensity);
void LCD_OutputOn(void);
void LCD_OutputOff(void);
//void LCD_OutputOnOff(void);
void LCD_WriteVoltage(uint16_t voltage);
void LCD_WriteCurrent(uint16_t current);


static void LCD_Command(unsigned char a);
static void LCD_Data(unsigned char a);

#endif
