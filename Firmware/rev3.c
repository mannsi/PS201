/************************************
*									*
*		DIGITAL PSU REV 3			*			
*		Fridrik F Gautason			*
*		Gudbjorn Einarsson			*
*		Copyright 2013				*
*									*
************************************/

#include "rev3.h"

// Use uint8_t (unsigned char) for variables that do not have to be 
// bigger than one byte. Use unsigned int for any other variable.
uint8_t forceUpdate = 0;
uint8_t firstRun = 1;
uint8_t readyToReceiveCommand = 1;
uint8_t outputIsOn = 0;
uint8_t backlightIntensity = 10;
uint8_t contrast = 50;
uint16_t voltageRead = 0;
uint16_t currentRead = 0;
uint16_t preregRead = 0;
uint16_t vinRead = 0;
uint16_t voltageSet = 0;
uint16_t currentSet = 0;

// Delay variables, between read cycles. We do not
// want to be constantly running the ADC.
uint16_t readDelay = 10000;
uint16_t setDelay = 50000; // This would not work with normal int!!
uint16_t delay = 10000;

// Calibration variables
float voltageRef;	// The ref voltage times 10
float voltageSetMulti;	// gain*ref/numBits
float voltageReadMulti;
float currentSetMulti;
float currentReadMulti;

int main(void)
{
	initRegistries();	
	initCalibration();

	LCD_Initialize(backlightIntensity,contrast);
	ADC_initialize();
	USART_Initialize();
	// Set stdout and in
	stdout = &USART_output;
	stdin  = &USART_input;
	
	LCD_StartScreen();
	_delay_ms(1000);
	
	// Start in the home screen with the set values
	LCD_HomeScreen(voltageSet,currentSet,outputIsOn,encoderControls);

	/************************
	*						*
	*		MAIN LOOP		*
	*						*
	************************/

	while(1)
    {	
		// If Sw1 is pressed, toggle the output
		if (SW_Check1())
		{
			switchOutput();
			delay = setDelay;
			forceUpdate = 1;
		}

		// If Sw2 is pressed, let the encoder control the backlight
		if (SW_Check2())
		{
			// Go into backlight setting
			backlightIntensity = LCD_SetBacklight(backlightIntensity);
			LCD_HomeScreen(voltageSet,currentSet,outputIsOn,encoderControls);
		}

		// If Sw4 is pressed, toggle the encoder
		if (SW_Check4())
		{
			switch(encoderControls)
			{
				case VOLTAGE:
					encoderControls = CURRENT;
					break;
				case CURRENT:
					encoderControls = VOLTAGE;
					break;
				default:
					encoderControls = VOLTAGE;
					break;
			}
			LCD_WriteControlArrow(encoderControls);
		}
		
		// Rotary encoder
		unsigned char encoderTurnDirection = SW_CheckEncoder();
		if(encoderTurnDirection)
		{
			switch(encoderControls)
			{		
				case VOLTAGE:
					if(encoderTurnDirection == ENCODER_CCW)	
					{
						voltageSet--;
					}
					else 					
					{
						voltageSet++;
					}
					
					// Make sure voltage doesn't go under 0
					// or over 20 Volts.
					if(voltageSet > 60000)
					{
						voltageSet = 0;
					}
					else if(voltageSet > 200)
					{					
						voltageSet = 200;
					}
					
					transferToDAC(10, voltageSet / voltageSetMulti);
					LCD_WriteVoltage(voltageSet);
					break;
				case CURRENT:
					if(encoderTurnDirection == ENCODER_CCW) 	
					{
						currentSet--;
					}
					else					
					{
						currentSet++;
					}
					
					// Make sure Current doesn't go under 0
					// or over 1000 mA.
					if(currentSet > 60000)
					{
						currentSet = 0;
					}
					else if(currentSet > 100)
					{
						currentSet = 100;
					}
					
					transferToDAC(9, currentSet / currentSetMulti);
					LCD_WriteCurrent(currentSet);
					break;
			}
			delay = setDelay;
			forceUpdate = 1;
		}
	
		// if delay is zero we start a ADC conversion cycle
		// (if it is not reading) 
		// otherwise we reduce the delay variable
		if (delay == 0)
		{
			if(!(ADC_status & ADC_ISREADING))
			{
				ADC_status |= ADC_ISREADING;
				ADC_STARTCONVERSION;
				sei();
			}
		}
		else
		{
			delay--;
		}
			
		// When a new ADC reading is registered we display it
		if(ADC_status & ADC_NEWREADING)
		{
			cli();
			ADC_status &= ~ADC_ISREADING;
			ADC_status &= ~ADC_NEWREADING;

			uint16_t oldValue;
			switch(ADC_status)
			{
				case ADC_VOLTAGE:
					oldValue = voltageRead;
					voltageRead = ADC_reading * voltageReadMulti;
					if(voltageRead != oldValue)
					{
						forceUpdate = 1;
					}
					ADC_status = ADC_CURRENT;
					ADMUX &= 0xF0;
					ADMUX |= CURRENT_MON;
					break;
				case ADC_CURRENT:
					oldValue = currentRead;
					currentRead = ADC_reading * currentReadMulti;
					if(currentRead != oldValue)
					{
						forceUpdate = 1;
					}
					ADC_status = ADC_PREREGULATOR;
					ADMUX &= 0xF0;
					ADMUX |= PREREG;
					break;
				case ADC_PREREGULATOR:
					preregRead = ADC_reading * voltageReadMulti;
					ADC_status = ADC_VIN;
					ADMUX &= 0xF0;
					ADMUX |= VIN_MON;
					break;
				case ADC_VIN:		
					vinRead = ADC_reading * voltageReadMulti;
					ADC_status = ADC_VOLTAGE;
					ADMUX &= 0xF0;
					ADMUX |= VOLTAGE_MON;
					break;
				default:
					ADC_status = ADC_VOLTAGE;
					ADMUX &= 0xF0;
					ADMUX |= VOLTAGE_MON;
					break;
			}

			if (ADC_status == ADC_VIN)
			{	
			
				/*
				Include this if you want to update the device to real values after delay
				*/
				if(!firstRun && forceUpdate)
				{
					if(outputIsOn)
					{
						LCD_WriteCurrent(currentRead);
						LCD_WriteVoltage(voltageRead);
					}
					else
					{
						LCD_WriteCurrent(currentSet);
						LCD_WriteVoltage(voltageSet);
					}
				}
			
				delay = readDelay;
				firstRun = 0;
				forceUpdate = 0;
				readyToReceiveCommand = 1;
			}
		}

		if (USART_IsReceivingData())
		{
			// Listen for USB command
			uint8_t cmd = 0;
			char data[MAXLEN];
			char outputChar;
			char dataChar;
			uint8_t index = 0;
			uint16_t newSetting;
			
			if(getpacket(&cmd,data))
			{
				switch(cmd)
				{
					case USART_NAK:
						sendNAK();
						cmd = USART_WRITEALLCOMMANDS;
						sendcmd(cmd);
						putchar('\n');
						break;
					case USART_WRITEALL:
						sendACK();
						if (outputIsOn)
						{
							outputChar = '1';
						}
						else
						{
							outputChar = '0';
						}
						writeToUsb(voltageRead, currentRead, voltageSet, currentSet, preregRead, vinRead, outputChar);
						break;
					case USART_SEND_HANDSHAKE:
						sendACK();
						break;
					case USART_RECEIVE_VOLTAGE:
						sendACK();
						mapToVoltage(&newSetting,data);
						if(newSetting > 200) break;
						voltageSet = newSetting;
						LCD_WriteVoltage(voltageSet);
						delay = setDelay;
						forceUpdate = 1;
						transferToDAC(10, voltageSet / voltageSetMulti);
						break;			
					case USART_SEND_VOLTAGE:
						sendACK();
						mapVoltage(voltageRead,data);
						sendpacket(cmd,data);
						break;
					case USART_SEND_SET_VOLTAGE:
						sendACK();
						mapVoltage(voltageSet,data);
						sendpacket(cmd,data);
						break;
					case USART_RECEIVE_CURRENT:
						sendACK();
						mapToCurrent(&newSetting,data);
						if(newSetting > 100) break;
						currentSet = newSetting;
						LCD_WriteCurrent(currentSet);
						delay = setDelay;
						forceUpdate = 1;
						transferToDAC(9, currentSet / currentSetMulti);
						break;			
					case USART_SEND_CURRENT:
						sendACK();
						mapCurrent(currentRead,data);
						sendpacket(cmd,data);
						break;
					case USART_SEND_SET_CURRENT:
						sendACK();
						mapCurrent(currentSet,data);
						sendpacket(cmd,data);
						break;
					case USART_SEND_VIN:
						sendACK();
						mapVoltage(vinRead,data);
						sendpacket(cmd,data);
						break;
					case USART_SEND_VPREREG:
						sendACK();
						mapVoltage(preregRead,data);
						sendpacket(cmd,data);
						break;
					case USART_ENABLE_OUTPUT:
						sendACK();
						enableOutput();
						break;
					case USART_DISABLE_OUTPUT:
						sendACK();
						disableOutput();
						break;
					case USART_IS_OUTPUT_ON:
						sendACK();
						if (outputIsOn)
						{
							data[0] = '1';
						}
						else
						{
							data[0] = '0';
						}
						data[1] = '\0';
						
						sendpacket(cmd,data);
						break;
					case USART_WRITEALLCOMMANDS:
						puts("Writing all commands in ASCII:");
						puts("Send voltage:");
						sendcmd(USART_SEND_VOLTAGE);
						puts("\nchange voltage:");
						sprintf(data,"10\0");
						sendpacket(USART_RECEIVE_VOLTAGE,data);
						puts("\nSend current:");
						sendcmd(USART_SEND_CURRENT);
						puts("\nchange current:");
						sprintf(data,"234\0");
						sendpacket(USART_RECEIVE_CURRENT,data);
						puts("\nSend input voltage:");
						sendcmd(USART_SEND_VIN);
						puts("\nSend preregulator voltage:");
						sendcmd(USART_SEND_VPREREG);
						puts("\nEnable output:");
						sendcmd(USART_ENABLE_OUTPUT);
						puts("\n\n\n\n");
						break;
					default:
						break;
						
				}	
			}
		}
	}

	return 0;
}

void writeDebug(char *debugMessage)
{
	LCD_Clear();
	LCD_Cursor(0,0);
	LCD_Write(debugMessage);
	_delay_ms(1000);
}

// For the DAC (LTC1661) we must give one 16bit word 
// first four bits are control code, the next eight 
// are the actual data and the last two are ignored.
void transferToDAC(unsigned char CTRL,uint16_t dacData){
	readyToReceiveCommand = 0;
  	// Make sure a is a ten bit word
  	dacData &= 0x03FF;
	// Then shift up by two bits, the DAC does not
	// care about the two last bits!
	//a = a << 2; 
	// Shift the control code up by 4 bits
	CTRL = CTRL << 4;

	// Now we can transfer this to the DAC
  	// Take the DAC chip select low
  	SELECT_DAC;
  	// Transfer in two 8 bit steps
  	SPDR = CTRL | (dacData >> 6);
	while(!(SPSR & (1<<SPIF)));
	SPDR = (dacData << 2) & 0x00FF;
	while(!(SPSR & (1<<SPIF)));
  	// Restore the chip select
  	DESELECT_DAC;
}

void writeVoltageToUsb(uint16_t voltage)
{
	unsigned char voltageArray [10];
	mapVoltage(voltage, voltageArray);
	USART_Transmit(voltageArray);
}

void writeCurrentToUsb(uint16_t current)
{
	unsigned char currentArray [10];
	mapCurrent(current, currentArray);	
	USART_Transmit(currentArray);
}

void writeToUsb(uint16_t voltage, 
				uint16_t current, 
				uint16_t voltageSet, 
				uint16_t currentSet, 
				uint16_t preregVoltage,
				uint16_t inputVoltage, 
				unsigned char outputOn)
{
	unsigned char voltageArray [10];
	unsigned char currentArray [10];
	unsigned char voltageSetArray [10];
	unsigned char currentSetArray [10];
	unsigned char voltagePreregArray [10];
	unsigned char voltageInputArray [10];
	unsigned char combinedArray [66];
	
	mapVoltage(voltage, voltageArray);
	mapCurrent(current, currentArray);
	mapVoltage(voltageSet, voltageSetArray);
	mapCurrent(currentSet, currentSetArray);
	mapVoltage(preregVoltage, voltagePreregArray);
	mapVoltage(inputVoltage, voltageInputArray);
	joinArrays(voltageArray, currentArray, voltageSetArray, currentSetArray, voltagePreregArray , voltageInputArray , outputOn, combinedArray);
	sendpacket(USART_WRITEALL,combinedArray);
}

void joinArrays(
	unsigned char *voltageArray, 
	unsigned char *currentArray, 
	unsigned char *voltageSetArray, 
	unsigned char *currentSetArray,
	unsigned char *voltagePreregArray,
	unsigned char *voltageInputArray,
	unsigned char outputOn,
	unsigned char *combinedArray)
{
	clearArray(combinedArray,55);
	
	int newArraySize = appendArray(combinedArray, 0, voltageArray, 10);
	combinedArray[newArraySize] = ';';
	newArraySize = appendArray(combinedArray, newArraySize + 1, currentArray, 10);
	combinedArray[newArraySize] = ';';
	newArraySize = appendArray(combinedArray, newArraySize + 1, voltageSetArray, 10);
	combinedArray[newArraySize] = ';';
	newArraySize = appendArray(combinedArray, newArraySize + 1, currentSetArray, 10);
	combinedArray[newArraySize] = ';';
	newArraySize = appendArray(combinedArray, newArraySize + 1, voltagePreregArray, 10);
	combinedArray[newArraySize] = ';';
	newArraySize = appendArray(combinedArray, newArraySize + 1, voltageInputArray, 10);
	combinedArray[newArraySize] = ';';
	combinedArray[newArraySize+1] = outputOn;
}

int appendArray(unsigned char *targetArray, 
				int arraySize, 
				unsigned char *appendingArray, 
				int appendingArrayMaxSize)
{
	int i;
	unsigned char tempChar;
	for(i = 0; i< appendingArrayMaxSize; i++)
	{
		tempChar = appendingArray[i];
		if(!tempChar)
		{
			break;
		}
		targetArray[i + arraySize] = tempChar;
	}
	
	return i + arraySize;
}

void mapVoltage(uint16_t voltage, unsigned char *voltageArray)
{
	voltageArray[0] = voltage < 1000 ? ' ' : (char) ( ((int) '0') + voltage / 1000 );
	voltageArray[1] = voltage < 100 ? ' ' : (char) ( ((int) '0') + (voltage%1000) / (100) );
	voltageArray[2] = voltage < 10 ? '0' : (char) ( ((int) '0') + (voltage%100) / (10) );
	voltageArray[3] = '.';
	voltageArray[4] = (char) ( ((int) '0') + (voltage%10));
	voltageArray[5] = '\0';
}

void mapCurrent(uint16_t current, unsigned char *currentArray)
{
	currentArray[0] = current < 100 ? ' ' : (char) ( ((int) '0') + current / 100 );
	currentArray[1] = current < 10 ? ' ' : (char) ( ((int) '0') + (current%100) / (10) );
	currentArray[2] = (char) ( ((int) '0') + current%10 );
	currentArray[3] = '0';
	currentArray[4] = '\0';
}

void mapToVoltage(uint16_t *voltage, unsigned char *voltageArray)
{
	// Determine the length of the string
	char *a;
	char *b;
	*voltage = (uint16_t) (strtol(voltageArray,&a,0)*10);
	// Find the fractional part of the number
	if(*a == '.')
	{
		uint16_t fraction = (uint16_t) strtol((a+1),&b,0);
		// Throw away extra digits
		while(fraction > 10)
		{
			fraction = fraction/10;
		}
		*voltage = *voltage + fraction;
	}
}

void mapToCurrent(uint16_t *current, char *currentArray)
{
	*current  = atol(currentArray)/10;
}


void clearArray(unsigned char *array, int size)
{
	int i;
	for (i = 0; i < size; i++)
	{
		array[i] = 0;
	}
}

void switchOutput()
{
	if(outputIsOn)
	{
		disableOutput();
	}
	else
	{
		enableOutput();
	}
}

void enableOutput()
{
	outputIsOn = 1;
	LCD_OutputOn();
	ENABLE_OUTPUT;
}

void disableOutput()
{
	outputIsOn = 0;
	LCD_OutputOff();
	DISABLE_OUTPUT;
}

static void initRegistries()
{
	DDRB = 0;
	DDRC = 0;
	DDRD = 0;

	// Initialize the Switches and encoder
	SW_Initialize();
	
	// DAC
	DDRD |= 1 << PD7;	// DAC chip select
	DESELECT_DAC;

	//Display
	DDRD |= 1 << PD6;	// Display chip select
	DESELECT_DISPLAY;
	DDRB |= 1 << PB2;	// Backlight
	DDRB |= 1 << PB1;	// Contrast
	DDRD |= 1 << PD5;	// Display enable
	DISABLE_DISPLAY;
	PORTB |= 1 << PB2; 
	PORTB |= 1 << PB1;	

	// Turn off Bias
	DDRB  |= 1 << PB0;	// Switcher Shutdown
	PORTB &= ~(1 << PB0);
	DDRC  |= 1 << PC0; 	// Shutdown transistor
	outputIsOn = 0;
	DISABLE_OUTPUT;

	// SPI interface to DAC and DISPLAY
	DDRB |= 1 << PB3;	// SPI MOSI
	DDRB |= 1 << PB5;	// SPI SCK

	// Enable SPI, Master, set clock rate fck/16
	SPCR = (1<<SPE)|(1<<MSTR)|(1<<SPR0);
}

static void initCalibration()
{
	// Calibration variables
	voltageRef = 25.0;	// The ref voltage times 10
	voltageSetMulti  = 10.0*voltageRef/1024;	// gain*ref/numBits
	voltageReadMulti = 11.0*voltageRef/1024;
	currentSetMulti  = 10/0.2/11*voltageRef/1024;
	currentReadMulti = 10/0.2/11*voltageRef/1024;
}
