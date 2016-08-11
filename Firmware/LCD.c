#include "LCD.h"

#define LCD_ENABLE_PORT portD
#define LCD_ENABLE_PIN	5
#define LCD_CS_PORT	portD
#define LCD_CS_PIN	6
#define BACKLIGHT_PORT	portB
#define BACKLIGHT_PIN	2
#define CONTRAST_PORT	portB
#define CONTRAST_PIN	1

// Set up the display in 4 bit mode and ready for writing to
void LCD_Initialize(uint8_t backlight, uint8_t contrast)
{
    IOSetOutput(LCD_CS_PORT,LCD_CS_PIN);
    DESELECT_DISPLAY;
    IOSetOutput(BACKLIGHT_PORT,BACKLIGHT_PIN);
    IOSetOutput(CONTRAST_PORT,CONTRAST_PIN);
    IOSetOutput(LCD_ENABLE_PORT,LCD_ENABLE_PIN);
    DISABLE_DISPLAY;
    IOSetPin(BACKLIGHT_PORT,BACKLIGHT_PIN);
    IOSetPin(CONTRAST_PORT,CONTRAST_PIN);

    SPI_Initialize();

    // Setting up OC1 which is the PWM module for
    // the backlight and contrast. The duty cycle is
    // controlled by the user.
    BIT_SET(TCCR1A,BIT(COM1A1));			// Enable both osc
    BIT_SET(TCCR1A,BIT(COM1B1));
    BIT_SET(TCCR1A,BIT(WGM10));			// FAST 8 bit PWM
    BIT_SET(TCCR1A,BIT(WGM12));
    OCR1A = contrast*5;				// Contrast
    OCR1B = backlight*19;				// Backlight
    BIT_SET(TCCR1B,BIT(CS10));			// START no prescaler

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
    SPI_SendData(a>>4 | (1<<4));
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
    SPI_SendData(a | (1<<4));
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
void LCD_Cursor(uint8_t row, uint8_t column)
{
    switch (row)
    {
        case 0:
            LCD_Command((0x80 + column)>>4);
            LCD_Command(0x80 + column);
            break;
        case 1:
            LCD_Command((0xc0 + column)>>4);
            LCD_Command(0xc0 + column);
            break;
        default:
            break;
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
    SPI_SendData(a & ~(1<<4));
    // Restore the chip select
    DESELECT_DISPLAY;

    // enable the display to read the data
    ENABLE_DISPLAY;
    _delay_ms(1);
    DISABLE_DISPLAY;
}

