#include "DISPLAY.h"

int showOutputOn = 1;

void DISPLAY_Initialize(uint8_t backlight, uint8_t contrast)
{
    LCD_Initialize(backlight,contrast);
}

void DISPLAY_StartScreen()
{
    LCD_Clear();
    LCD_Cursor(0,4);
    LCD_Write("Digital");
    LCD_Cursor(1,6);
    LCD_Write("PSU");
}

static void DISPLAY_WriteSelectorUpper(void)
{
    LCD_Cursor(0,2);
    LCD_Write("~");
    LCD_Cursor(1,2);
    LCD_Write(" ");
}

static void DISPLAY_WriteSelectorLower(void)
{
    LCD_Cursor(0,2);
    LCD_Write(" ");
    LCD_Cursor(1,2);
    LCD_Write("~");
}

void DISPLAY_HomeScreen(char* voltage,char* current, uint8_t outputOn, unsigned char encoderControls)
{
    // Write normal home screen
    LCD_Clear();
    LCD_Cursor(0,0);
    LCD_Write("V:");
    LCD_Cursor(1,0);
    LCD_Write("I:");

    DISPLAY_WriteSelectorUpper();
    DISPLAY_WriteVoltage(voltage);
    DISPLAY_WriteCurrent(current);

    if(outputOn)
    {
        DISPLAY_OutputOn();
    }
    else
    {
        DISPLAY_OutputOff();
    }
}

unsigned char menuItem[NUMBEROFMENUITEMS][12] = {
        "Backlight",
        "Contrast",
        "Status",
        "Calibration"};

unsigned char DISPLAY_MenuScreen(void)
{
    unsigned char currentItem = 0;
    unsigned char selectorUpper = 1;
    unsigned char updateScreen = 1;

    while(!SWITCH_Pressed(&switch1))
    {
        if(updateScreen)
        {
            LCD_Clear();
            if(selectorUpper)
            {
                LCD_Cursor(0,2);
            }
            else
            {
                LCD_Cursor(1,2);
            }
            LCD_Write("~");
            LCD_Cursor(0,3);
            LCD_Write(menuItem[currentItem]);
            LCD_Cursor(1,3);
            if(currentItem == NUMBEROFMENUITEMS - 1)
            {
                LCD_Write(menuItem[0]);
            }
            else
            {
                LCD_Write(menuItem[currentItem + 1]);
            }
            updateScreen = 0;
        }

        unsigned char dir = SW_CheckEncoder();
        //preveous menu item
        if(SWITCH_Pressed(&switch2) || (dir && dir != ENCODER_CCW))
        {
            if(selectorUpper)
            {
                updateScreen = 1;
                if(currentItem == 0)
                {
                    currentItem = NUMBEROFMENUITEMS-1;
                }
                else
                {
                    currentItem--;
                }
            }
            else
            {
                LCD_Cursor(0,2);
                LCD_Write("~");
                LCD_Cursor(1,2);
                LCD_Write(" ");
                selectorUpper = 1;
            }
        }
        //next menu item
        if(SWITCH_Pressed(&switch3) || dir == ENCODER_CCW)
        {
            if(selectorUpper)
            {
                LCD_Cursor(0,2);
                LCD_Write(" ");
                LCD_Cursor(1,2);
                LCD_Write("~");
                selectorUpper = 0;
            }
            else
            {
                updateScreen = 1;
                if(currentItem == NUMBEROFMENUITEMS-1)
                {
                    currentItem = 0;
                }
                else
                {
                    currentItem++;
                }
            }
        }
        //item selected
        if(SWITCH_Pressed(&switch4))
        {
            if(currentItem + 1 - selectorUpper == NUMBEROFMENUITEMS)
            {
                return 0;
            }
            else
            {
                return (currentItem + 1 - selectorUpper);
            }
        }
    }
    return -1;
}

void DISPLAY_WriteVoltage(char* voltage)
{
    LCD_Cursor(0,3);
    LCD_Write(voltage);
}

void DISPLAY_WriteCurrent(char* current)
{
    LCD_Cursor(1,3);
    LCD_Write(current);
}

void DISPLAY_SelectVoltage(void)
{
    DISPLAY_WriteSelectorUpper();
}

void DISPLAY_SelectCurrent(void)
{
    DISPLAY_WriteSelectorLower();
}

uint8_t DISPLAY_SetBacklight(uint8_t backlightIntensity)
{
    // Write small backlight screen
    LCD_Clear();
    LCD_Cursor(0,3);
    LCD_Write(menuItem[MENU_BACKLIGHT]);
    LCD_Cursor(1,0);
    LCD_Write("[              ]");
    LCD_Cursor(1,1);
    int i = backlightIntensity;
    for(i; i>0; i--)
    {
        LCD_Write("=");
    }
    LCD_Write(">");
    while(!SWITCH_Pressed(&switch1) && !SWITCH_Pressed(&switch2) && !SWITCH_Pressed(&switch3) && !SWITCH_Pressed(&switch4))
    {
        unsigned char dir = SW_CheckEncoder();
        if(dir)
        {
            if(dir == ENCODER_CCW)
            {
                backlightIntensity--;
            }
            else
            {
                backlightIntensity++;
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

uint8_t DISPLAY_SetContrast(uint8_t contrast)
{
    // Write small backlight screen
    LCD_Clear();
    LCD_Cursor(0,3);
    LCD_Write(menuItem[MENU_CONTRAST]);
    LCD_Cursor(1,0);
    LCD_Write("[              ]");
    LCD_Cursor(1,1);
    int i = contrast;
    for(i; i>0; i--)
    {
        LCD_Write("=");
    }
    LCD_Write(">");
    while(!SWITCH_Pressed(&switch1) && !SWITCH_Pressed(&switch2) && !SWITCH_Pressed(&switch3) && !SWITCH_Pressed(&switch4))
    {
        unsigned char dir = SW_CheckEncoder();
        if(dir)
        {
            if(dir == ENCODER_CCW)
            {
                contrast--;
            }
            else
            {
                contrast++;
            }
            if(contrast > 20)
            {
                contrast = 0;
            }
            else if(contrast > 13)
            {
                contrast = 13;
            }
            else
            {
                OCR1A = 5*contrast;
                LCD_Cursor(1,0);
                LCD_Write("[              ]");
                LCD_Cursor(1,1);
                for(i = contrast; i>0; i--)
                {
                    LCD_Write("=");
                }
                LCD_Write(">");
            }
        }
    }
    return contrast;
}

void DISPLAY_OutputOn()
{
    showOutputOn = 1;
    LCD_Cursor(0,13);
    LCD_Write(" ON");
}

void DISPLAY_OutputOff()
{
    showOutputOn = 0;
    LCD_Cursor(0,13);
    LCD_Write("OFF");
}