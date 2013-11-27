#include "LCD.h"

int showOutputOn = 1;

// Set up the display in 4 bit mode and ready for writing to
void LCD_Initialize(void)
{	
	//Display
	DDRD |= 1 << PD6;	// Display chip select
	DESELECT_DISPLAY;
	DDRB |= 1 << PB2;	// Backlight
	PORTB |= 1 << PB2;	// Turn Backlight on
	DDRD |= 1 << PD5;	// Display enable

	// Delay after power up
	_delay_ms(150);
	// Initialize LCD in 4 bit mode
	LCD_Command(3);
	_delay_ms(5);
	LCD_Command(3);
	LCD_Command(3);
	LCD_Command(2);
	
	// Function set
	LCD_Command(2);
	LCD_Command(8);
	_delay_ms(1);

	// Display off
	LCD_Command(0);
	LCD_Command(8);
	_delay_ms(1);

	// Entry mode
	LCD_Command(0);
	LCD_Command(6);
	_delay_ms(1);

	// Display on
	LCD_Command(0);
	LCD_Command(0x0C);
	_delay_ms(1);
	
	// Clear Screen
	LCD_Command(0);
	LCD_Command(1);
	_delay_ms(1);
}

// The display is connected through a shift 595 register, the first
// four bits are the interface to the LCD and the fifth bit is connected
// to the RS pin on the LCD. Last three are ignored. To write a character
// to the display we must send out the first four bits and then the last
// four, in both cases the RS bit must be HIGH.
static void LCD_Data(unsigned char a)
{

	// Take the 595 chip select pin low
	SELECT_DISPLAY;
	// Transfer the first four bits of a via SPI
	// manually making sure that the fifth bit is high
	SPDR = a>>4 | (1<<4);
	while(!(SPSR & (1<<SPIF)));
  	// Restore the chip select
  	DESELECT_DISPLAY;
	
	// enable the display to read the data
	// (wait two cycles to led the display read)
	ENABLE_DISPLAY; 
	_delay_ms(1);
	DISABLE_DISPLAY;

	// Take the 595 chip select pin low
	SELECT_DISPLAY;
	// Transfer the last four bits of a via SPI
	// again manually making sure fith bit is high
	SPDR = a | (1<<4);
	while(!(SPSR & (1<<SPIF)));
	// Restore the chip select
  	DESELECT_DISPLAY;
	
	// enable the display to read the data
	ENABLE_DISPLAY; 
	_delay_ms(1);
	DISABLE_DISPLAY;
}

// To write a full string to the LCD
void LCD_Write(unsigned char* data)
{
	unsigned char i;

	for(i=0;i<20;i++)
	{
		if(!data[i]) break;
		LCD_Data(data[i]);
	}
}

// To position the cursor
void LCD_Cursor(unsigned char row, unsigned char column)
{
	switch (row)
	{
		case 0:		LCD_Command((0x80 + column)>>4); 
					LCD_Command(0x80 + column);
					break;
		case 1: 	LCD_Command((0xc0 + column)>>4);
					LCD_Command(0xc0 + column);
					break;
		default:	break;
	}
}

// to highlight the current cursor position
void LCD_HighLight()
{
	LCD_Command(0);
	LCD_Command(0xE);
}

// to turn off highlight 
void LCD_NoHighLight()
{
	LCD_Command(0);
	LCD_Command(0xC);
}


// to clear the display
void LCD_Clear()
{
	LCD_Command(0);
	LCD_Command(1);
	_delay_ms(1);
}

void LCD_ShowStartScreen()
{
	LCD_Cursor(0,4);
	LCD_Write("Digital");
	LCD_Cursor(1,6);
	LCD_Write("PSU");
}

void LCD_WriteValues(unsigned char* voltage,unsigned char* current)
{
	// Write normal home screen
	LCD_Clear();
	LCD_Cursor(0,0);
	LCD_Write("V: ");
	LCD_Write(voltage);
	LCD_Write(" V");
	LCD_Cursor(1,0);
	LCD_Write("I: ");
	LCD_Write(current);
	LCD_Write(" mA");

	// Determine the last selected encoder function
	switch(encoderControls)
	{
		case VOLTAGE:
			LCD_Cursor(0,2);
			LCD_Write("~");
			break;
		case CURRENT:
			LCD_Cursor(1,2);
			LCD_Write("~");
			break;
		default:
			encoderControls = VOLTAGE;
			LCD_Cursor(0,2);
			LCD_Write("~");
			break;
	}

	showOutputOnOff();
}

int LCD_SetBacklight(int backlightIntensity)
{
	// Write small backlight screen
	LCD_Clear();
	LCD_Cursor(0,3);
	LCD_Write("Backlight");
	LCD_Cursor(1,0);
	LCD_Write("[              ]");
	LCD_Cursor(1,1);
	int i = backlightIntensity;
	for(i; i>0; i--)
	{
		LCD_Write("=");
	}
	LCD_Write(">");
	while(!SW_Check1() && !SW_Check2() && !SW_Check3() && !SW_Check4())
	{
		unsigned char dir = SW_CheckEncoder();
		if(dir)
		{
			if(dir == ENCODER_CW) 	
			{
				backlightIntensity += 1;
			} 
			else
			{
				backlightIntensity -= 1;
			}
			if(backlightIntensity > 20)
			{
				backlightIntensity = 0;
			}
			else if(backlightIntensity > 13)
			{
				backlightIntensity = 13;
			}
			else
			{
				OCR1B = 19*backlightIntensity;
				LCD_Cursor(1,0);
				LCD_Write("[              ]");
				LCD_Cursor(1,1);
				for(i = backlightIntensity; i>0; i--)
				{
					LCD_Write("=");
				}
				LCD_Write(">");
			}
		}
	}
	return backlightIntensity;
}

// This is exactly like the above function but now
// we make sure the fifth bit is allways LOW to indicate
// that the display is receiving instruction. Also we only
// send out four bits with each command the first four bits
// of a are ignored.
static void LCD_Command(unsigned char a)
{
	// Take the 595 chip select pin low
	SELECT_DISPLAY;
	// Transfer the last four bits of a via SPI
	// again manually making sure fith bit is low
	SPDR = a & ~(1<<4);
	while(!(SPSR & (1<<SPIF)));
	// Restore the chip select
  	DESELECT_DISPLAY;
	
	// enable the display to read the data
	ENABLE_DISPLAY; 
	_delay_ms(1);
	DISABLE_DISPLAY;
}

void LCD_SetOutputOn()
{
	showOutputOn = 1;
	showOutputOnOff();
}

void LCD_SetOutputOff()
{
	showOutputOn = 0;
	showOutputOnOff();
}

static void showOutputOnOff()
{
	if (showOutputOn)
	{
		LCD_Cursor(0, 13);
		LCD_Write("ON ");
	}
	else
	{
		LCD_Cursor(0, 13);
		LCD_Write("OFF");
	}
}

