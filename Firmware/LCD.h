#ifndef LCD_H
#define LCD_H

#include<avr/io.h>
#include "SW.h"

#ifndef F_CPU
#define F_CPU 8000000
#endif
#include<util/delay.h>
#include "SW.h"

// shortcuts for display 
#define ENABLE_DISPLAY PORTD |= 1 << PD5
#define DISABLE_DISPLAY PORTD &= ~(1 << PD5)
#define SELECT_DISPLAY PORTD &= ~(1 << PD6)
#define DESELECT_DISPLAY PORTD |= (1 << PD6)

#define NUMBEROFMENUITEMS 4
#define MENU_BACKLIGHT 0
#define MENU_CONTRAST 1
#define MENU_STATUS 2
#define MENU_CALIBRATION 3

void LCD_Initialize(uint8_t backlight, uint8_t contrast);
void LCD_Write(unsigned char* data);
void LCD_Cursor(uint8_t row, uint8_t column);
void LCD_Clear(void);
void LCD_HighLight(void);
void LCD_NoHighLight(void);
void LCD_StartScreen(void);
void LCD_HomeScreen(uint16_t v,uint16_t c, uint8_t outputOn, unsigned char encoderControls);
unsigned char LCD_MenuScreen(void);
void LCD_WriteControlArrow(unsigned char);

uint8_t LCD_SetBacklight(uint8_t backlightIntensity);
uint8_t LCD_SetContrast(uint8_t contrast);

void LCD_OutputOn(void);
void LCD_OutputOff(void);
//void LCD_OutputOnOff(void);
void LCD_WriteVoltage(uint16_t voltage);
void LCD_WriteCurrent(uint16_t current);

static void showOutputOnOff(void);
static void LCD_Command(unsigned char a);
static void LCD_Data(unsigned char a);

#endif
