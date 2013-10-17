/************************************
*									*
*		DIGITAL PSU REV 2			*			
*		Fridrik F Gautason			*
*		Copyright 2013				*
*									*
************************************/

#include "rev2.h"

int setValuesHaveChanged = 0;

uint8_t backlightIntensity = 10;
uint16_t voltageRead = 0;
uint16_t voltageAveraging = 0;
uint16_t currentRead = 0;
uint16_t currentAveraging = 0;
uint16_t preregRead = 0;
uint16_t preregAveraging = 0;
uint16_t vinRead = 0;
uint16_t vinAveraging = 0;
uint16_t voltageSet = 0;
uint16_t currentSet = 0;

// Delay variables, between read cycles. We do not
// want to be constantly running the ADC.
uint16_t readDelay = 10000;
uint16_t setDelay = 50000;
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

	LCD_Initialize();
	ADC_initialize();
	USART_Initialize();
	
	LCD_ShowStartScreen();
	_delay_ms(1000);
	writeToLCD(voltageSet,currentSet);
	LCD_HighLight();

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
			LCD_SwitchOutput();
			writeToLCD(voltageRead,currentRead);
		}

		// If Sw2 is pressed, let the encoder control the backlight
		if (SW_Check2())
		{
			// Go into backlight setting
			backlightIntensity = LCD_SetBacklight(backlightIntensity);
			writeToLCD(voltageRead,currentRead);
		}

		// If Sw4 is pressed, toggle the encoder
		if (SW_Check4())
		{
			switch(encoderControls)
			{
				case VOLTAGE:
					encoderControls = CURRENT;
					writeToLCD(voltageRead,currentRead);
					break;
				case CURRENT:
					encoderControls = VOLTAGE;
					writeToLCD(voltageRead,currentRead);
					break;
				default:
					encoderControls = VOLTAGE;
					writeToLCD(voltageRead,currentRead);
					break;
			}
		}
		
		// Rotary encoder
		unsigned char encoderValue = SW_CheckEncoder();
		if(encoderValue)
		{
			switch(encoderControls)
			{		
				case VOLTAGE:
					if(encoderValue == ENCODER_CW)	
					{
						voltageSet += 1;
					}
					else 					
					{
						voltageSet -= 1;
					}

					if(voltageSet > 60000)
					{
						voltageSet = 0;
					}
					else if(voltageSet > 200)
					{
						voltageSet = 200;
					}

					transferToDAC(9,voltageSet/voltageSetMulti);
					writeToLCD(voltageSet,currentSet);
					// Set delay to keep displaying the set voltage
					// and current for some time
					delay = setDelay;
					setValuesHaveChanged = 1;
					break;
				case CURRENT:
					if(encoderValue == ENCODER_CW) 	
					{
						currentSet++;
					}
					else					
					{
						currentSet--;
					}

					if(currentSet > 60000)
					{
						currentSet = 0;
					}
					else if(currentSet > 100)
					{
						currentSet = 100;
					}

					transferToDAC(10,currentSet/currentSetMulti);
					writeToLCD(voltageSet,currentSet);
					delay = setDelay;
					setValuesHaveChanged = 1;
					break;
			}
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
			switch(ADC_status)
			{
				case ADC_VOLTAGE:
					voltageAveraging += ADC_reading;
					ADC_status = ADC_CURRENT;
					ADMUX &= 0xF0;
					ADMUX |= CURRENT_MON;
					break;
				case ADC_CURRENT:		
					currentAveraging += ADC_reading;
					ADC_status = ADC_PREREGULATOR;
					ADMUX &= 0xF0;
					ADMUX |= PREREG;
					break;
				case ADC_PREREGULATOR:
					preregAveraging += ADC_reading;
					ADC_status = ADC_VIN;
					ADMUX &= 0xF0;
					ADMUX |= VIN_MON;
					break;
				case ADC_VIN:		
					vinAveraging += ADC_reading;
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
				uint16_t oldVoltageRead = voltageRead;
				uint16_t oldCurrentRead = currentRead;
				voltageRead = voltageAveraging*voltageReadMulti;			
				currentRead = currentAveraging*currentReadMulti;
				preregRead = preregAveraging*voltageReadMulti;
				vinRead = vinAveraging*voltageReadMulti;
				
				if(voltageRead != oldVoltageRead || currentRead != oldCurrentRead || setValuesHaveChanged == 1)
				{
					writeToLCD(voltageRead,currentRead);
					setValuesHaveChanged = 0;
				}
				
				delay = readDelay;
				voltageAveraging = 0;
				currentAveraging = 0;
				preregAveraging = 0;
				vinAveraging = 0;
			}
		}

		// Listen for USB command
		unsigned char command = USART_ReceiveCommand();
		uint16_t newData;
		char isOutputOn;

		switch(command)
		{
			case USART_SEND_HANDSHAKE:
				USART_TransmitChar(USART_HANDSHAKE);
				USART_TransmitChar('\n');
				break;
			case USART_RECEIVE_VOLTAGE:
				newData = USART_ReceiveData();
				if(newData > 2000) break;
				voltageSet = newData;
				transferToDAC(9,voltageSet/voltageSetMulti);
				break;			
			case USART_SEND_VOLTAGE:
				writeVoltageToUsb(voltageRead);
				break;
			case USART_SEND_SET_VOLTAGE:
				writeVoltageToUsb(voltageSet);
				break;
			case USART_RECEIVE_CURRENT:
				newData = USART_ReceiveData();
				if(newData > 100) break;
				currentSet = newData;
				transferToDAC(10,currentSet/currentSetMulti);
				break;			
			case USART_SEND_CURRENT:
				writeCurrentToUsb(currentRead);
				break;
			case USART_SEND_SET_CURRENT:
				writeCurrentToUsb(currentSet);
				break;
			case USART_SEND_VIN:
				writeVoltageToUsb(vinRead);
				break;
			case USART_SEND_VPREREG:
				writeVoltageToUsb(preregRead);
				break;
			case USART_ENABLE_OUTPUT:
				ENABLE_OUTPUT;
				writeToLCD(voltageRead,currentRead);
				break;
			case USART_DISABLE_OUTPUT:
				DISABLE_OUTPUT;
				writeToLCD(voltageRead,currentRead);
				break;
			case USART_IS_OUTPUT_ON:
				if (OUTPUT_IS_ENABLED)
				{
					isOutputOn = '1';
				}
				else
				{
					isOutputOn = '0';
				}
				
			    USART_TransmitChar(isOutputOn);
				USART_TransmitChar('\n');
			    break;
		}
	}
}

void writeDebug(char *debugMessage)
{
	int i;
	LCD_Clear();
	LCD_Cursor(0,0);
	LCD_Write(debugMessage);
	_delay_ms(1000);
}


// For the DAC (LTC1661) we must give one 16bit word 
// first four bits are control code, the next eight 
// are the actual data and the last two are ignored.
void transferToDAC(unsigned char CTRL,uint16_t dacData){
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

void writeToLCD(uint16_t voltage, uint16_t current)
{
	unsigned char voltageArray [10];
	unsigned char currentArray [10];
	mapVoltage(voltage, voltageArray);
	mapCurrent(current, currentArray);
	LCD_WriteValues(voltageArray,currentArray);
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

// store the numbers in chars
void mapVoltage(uint16_t voltage, unsigned char *voltageArray)
{
	int i;
	// Clear the buffer of the array
	for (i = 0; i < 10; i++)
	{
		voltageArray[i] = 0;
	}
	
	voltageArray[0] = voltage < 1000 ? ' ' : (char) ( ((int) '0') + voltage / 1000 );
	voltageArray[1] = voltage < 100 ? ' ' : (char) ( ((int) '0') + (voltage%1000) / (100) );
	voltageArray[2] = voltage < 10 ? '0' : (char) ( ((int) '0') + (voltage%100) / (10) );
	voltageArray[3] = '.';
	voltageArray[4] = (char) ( ((int) '0') + (voltage%10));
}

void mapCurrent(uint16_t current, unsigned char *currentArray)
{
	int i;
	// Clear the buffer of the array
	for (i = 0; i < 10; i++)
	{
		currentArray[i] = 0;
	}
	currentArray[0] = current < 100 ? ' ' : (char) ( ((int) '0') + current / 100 );
	currentArray[1] = current < 10 ? ' ' : (char) ( ((int) '0') + (current%100) / (10) );
	currentArray[2] = (char) ( ((int) '0') + current%10 );
	currentArray[3] = '0';
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

	// Output relay
	DDRB |= 1 << PB0;	// Output enable
	DISABLE_OUTPUT;

	// SPI interface to DAC and DISPLAY
	DDRB |= 1 << PB3;	// SPI MOSI
	DDRB |= 1 << PB5;	// SPI SCK
	// Enable SPI, Master, set clock rate fck/16
	SPCR = (1<<SPE)|(1<<MSTR)|(1<<SPR0);

	// Setting up OC1 which is the PWM module for
	// charge pump and backlight. The charge pump is 
	// always set on half duty cycle while backlight is 
	// controlled by the user.
	DDRB |= 1 << PB1;							// Charge pump
	DDRB |= 1 << PB2;							// Backlight
	TCCR1A  = (1 << COM1A1) | (1 << COM1B1);	// Enable both osc
	TCCR1A |= (1 << WGM10) | (1 << WGM12);		// FAST 8 bit PWM
	OCR1A = 0x80;								// charge pump 128
	OCR1B = backlightIntensity*19;						// Backlight
	TCCR1B = (1 << CS10);						// START no prescaler
}

static void initCalibration()
{
	// Calibration variables
	voltageRef = 49.88;	// The ref voltage times 10
	voltageSetMulti = 4.7*voltageRef/1024;	// gain*ref/numBits
	voltageReadMulti = 5.7*voltageRef/1024;
	currentSetMulti = 10/0.33/11*voltageRef/1024;
	currentReadMulti = 10/0.33/11*voltageRef/1024;
}
