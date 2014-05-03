#ifndef DISPLAY_H
#define DISPLAY_H

#include "LCD.h"
#include "SWITCH.h"
#include "rev3.h"

#define NUMBEROFMENUITEMS 4
#define MENU_BACKLIGHT 0
#define MENU_CONTRAST 1
#define MENU_STATUS 2
#define MENU_CALIBRATION 3

void DISPLAY_Initialize(uint8_t backlight, uint8_t contrast);
void DISPLAY_StartScreen(void);
void DISPLAY_HomeScreen(char *v,char *c, uint8_t outputOn, unsigned char encoderControls);
unsigned char DISPLAY_MenuScreen(void);
void DISPLAY_WriteSelectorUpper(void);
void DISPLAY_WriteSelectorLower(void);

uint8_t DISPLAY_SetBacklight(uint8_t backlightIntensity);
uint8_t DISPLAY_SetContrast(uint8_t contrast);

void DISPLAY_OutputOn(void);
void DISPLAY_OutputOff(void);
//void DISPLAY_OutputOnOff(void);
void DISPLAY_WriteVoltage(char *voltage);
void DISPLAY_WriteCurrent(char *current);

static void showOutputOnOff(void);

#endif