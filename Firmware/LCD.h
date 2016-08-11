#ifndef LCD_H
#define LCD_H

#include "IOHandler.h"
#include "SPI.h"

#ifndef F_CPU
#define F_CPU 8000000
#endif
#include<util/delay.h>

// shortcuts for display
#define ENABLE_DISPLAY		IOSetPin(LCD_ENABLE_PORT,LCD_ENABLE_PIN)
#define DISABLE_DISPLAY		IOClearPin(LCD_ENABLE_PORT,LCD_ENABLE_PIN)
#define SELECT_DISPLAY		IOClearPin(LCD_CS_PORT,LCD_CS_PIN)
#define DESELECT_DISPLAY	IOSetPin(LCD_CS_PORT,LCD_CS_PIN)

void LCD_Initialize(uint8_t backlight, uint8_t contrast);
void LCD_Write(unsigned char* data);
void LCD_Cursor(uint8_t row, uint8_t column);
void LCD_Clear(void);
void LCD_HighLight(void);
void LCD_NoHighLight(void);
static void LCD_Command(unsigned char a);
static void LCD_Data(unsigned char a);

#endif
