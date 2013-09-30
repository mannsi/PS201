/************************************
*									*
*		DIGITAL PSU REV 2			*			
*		Fridrik F Gautason			*
*		Copyright 2013				*
*									*
************************************/

#include "rev2.h"

uint8_t backlight = 10;

int main(void)
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
	OCR1B = backlight*19;						// Backlight
	TCCR1B = (1 << CS10);						// START no prescaler
	
	// A wanky opening screen
	LCD_Initialize();
	LCD_Cursor(0,4);
	LCD_Write("digital");
	LCD_Cursor(1,6);
	LCD_Write("PSU");
	_delay_ms(1000);
	LCD_Clear();

	// Voltage and current read variables
	uint16_t voltageRead = 0;
	uint16_t coltagePreRead = 0;
	uint16_t currentRead = 0;
	uint16_t currentPreRead = 0;
	uint16_t preregRead = 0;
	uint16_t vinRead = 0;
	int numReadAverages = 50;
	int readCounter = 0;

	// Voltage and current set variables
	uint16_t voltageSet = 0;
	uint16_t currentSet = 0;

	// Delay variables, because we want to show the
	// set varibles for some while before we show the 
	// readback.
	uint16_t voltageSetDelay = 0;
	uint16_t currentSetDelay = 0;
	uint16_t numDelayCycles = 3000;

	// Calibration variables
	float voltageRef = 498.8;	// The ref voltage times 100
	float voltageSetMulti = 4.7*voltageRef/1024;	// gain*ref/numBits
	float voltageReadMulti = 5.7*voltageRef/1024;
	float currentSetMulti = 1/0.33/11*voltageRef/1024;
	float currentReadMulti = 1/0.33/11*voltageRef/1024;

	// Start the ADC
	ADC_initialize();
	ADC_STARTCONVERSION;
	sei();

	// Start the USB interface
	USART_Initialize();

	MENU_Home();
	LCD_Cursor(0,3);
	LCD_WriteFloat(voltageSet);
	LCD_Cursor(1,3);
	LCD_WriteFloat(currentSet);

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
			if(OUTPUT_IS_ENABLED)
			{
				DISABLE_OUTPUT;
				LCD_Cursor(0,14);
				LCD_Write("  ");
			}
			else
			{
				ENABLE_OUTPUT;
				LCD_Cursor(0,14);
				LCD_Write("ON");
			}
		}

		// If Sw2 is pressed, let the encoder control the backlight
		if (SW_Check2())
		{
			// Go into backlight setting
			MENU_Backlight();
			MENU_Home();
			LCD_Cursor(0,3);
			LCD_WriteFloat(voltageSet);
			LCD_Cursor(1,3);
			LCD_WriteFloat(currentSet);
		}

		// IF Sw4 is pressed, toggle the encoder
		if (SW_Check4())
		{
			switch(encoderControls)
			{
			case VOLTAGE:
				encoderControls = CURRENT;
				LCD_Cursor(0,2);
				LCD_Write(" ");
				LCD_Cursor(1,2);
				LCD_Write("~");
				break;
			case CURRENT:
				encoderControls = VOLTAGE;
				LCD_Cursor(0,2);
				LCD_Write("~");
				LCD_Cursor(1,2);
				LCD_Write(" ");
				break;
			default:
				encoderControls = VOLTAGE;
				LCD_Cursor(0,2);
				LCD_Write("~");
				LCD_Cursor(1,2);
				LCD_Write(" ");
				break;
			}
		}

		
		// Rotary encoder
		unsigned char dir = SW_CheckEncoder();
		if(dir)
		{
			switch(encoderControls)
			{		
			case VOLTAGE:
				if(dir == ENCODER_CW)	voltageSet += 2;
				else 					voltageSet -= 2;

				if(voltageSet > 60000)
					voltageSet = 0;
				else if(voltageSet > 2000)
					voltageSet = 2000;

				transferToDAC(9,voltageSet/voltageSetMulti);
				LCD_Cursor(0,3);
				LCD_WriteFloat(voltageSet);
				// Set delay to keep displaying the set voltage
				// for some time
				voltageSetDelay = numDelayCycles;
				break;
			case CURRENT:
				if(dir == ENCODER_CW) 	currentSet += 1;
				else					currentSet -= 1;

				if(currentSet > 60000)
					currentSet = 0;
				else if(currentSet > 100)
					currentSet = 100;

				transferToDAC(10,currentSet/currentSetMulti);
				LCD_Cursor(1,3);
				LCD_WriteFloat(currentSet);
				currentSetDelay = numDelayCycles;
				break;
			default:
				break;
			}
		}
	
		// Reduce set delays by one
		if (voltageSetDelay > 0)
			voltageSetDelay--;
		if (currentSetDelay > 0)
			currentSetDelay--;

		// When a new ADC reading is registered we display it
		if(ADC_status & ADC_NEWREADING)
		{
			ADC_status &= ~ADC_NEWREADING;

			switch(ADC_status)
			{
			case ADC_VOLTAGE:
				voltageRead = ADC_reading*voltageReadMulti;
				ADC_status = ADC_CURRENT;
				ADMUX &= 0xF0;
				ADMUX |= CURRENT_MON;
				if (voltageSetDelay == 0)
				{
					LCD_Cursor(0,3);
					LCD_WriteFloat(voltageRead);
				}
				break;
			case ADC_CURRENT:
				currentRead = ADC_reading*currentReadMulti;
				ADC_status = ADC_PREREGULATOR;
				ADMUX &= 0xF0;
				ADMUX |= PREREG;
				if (currentSetDelay == 0)
				{
					LCD_Cursor(1,3);
					LCD_WriteFloat(currentRead);
				}
				break;
			case ADC_PREREGULATOR:
				preregRead = ADC_reading*voltageReadMulti;
				ADC_status = ADC_VIN;
				ADMUX &= 0xF0;
				ADMUX |= VIN_MON;
				break;
			case ADC_VIN:
				vinRead = ADC_reading*voltageReadMulti;
				ADC_status = ADC_VOLTAGE;
				ADMUX &= 0xF0;
				ADMUX |= VOLTAGE_MON;
			default:
				ADC_status = ADC_VOLTAGE;
				ADMUX &= 0xF0;
				ADMUX |= VOLTAGE_MON;
				break;
			}
			ADC_STARTCONVERSION;
		}


		// Listen for USB command
		unsigned char command = USART_RecieveCommand();
		uint16_t newData;

		switch(command)
		{
		case USART_SEND_HANDSHAKE:
			USART_TransmitChar(USART_HANDSHAKE);
			break;
		case USART_RECEIVE_VOLTAGE:
			newData = USART_ReceiveData();
			if(newData > 2000)
				break;
			voltageSet = newData;
			transferToDAC(9,voltageSet/voltageSetMulti);
			LCD_Cursor(0,3);
			LCD_WriteFloat(voltageSet);
			// Set delay to keep displaying the set voltage
			// for some time
			voltageSetDelay = numDelayCycles;
			break;			
		case USART_SEND_VOLTAGE:
			USART_Transmit(voltageRead);
			break;
		case USART_SEND_SET_VOLTAGE:
			USART_Transmit(voltageSet);
			break;
		case USART_RECEIVE_CURRENT:
			newData = USART_ReceiveData();
			if(newData > 100)
				break;
			currentSet = newData;
			transferToDAC(10,currentSet/currentSetMulti);
			LCD_Cursor(1,3);
			LCD_WriteFloat(currentSet);
			// Set delay to keep displaying the set voltage
			// for some time
			currentSetDelay = numDelayCycles;
			break;			
		case USART_SEND_CURRENT:
			USART_Transmit(currentRead);
			break;
		case USART_SEND_SET_CURRENT:
			USART_Transmit(currentSet);
			break;
		case USART_SEND_VIN:
			USART_Transmit(vinRead);
			break;
		case USART_SEND_VPREREG:
			USART_Transmit(preregRead);
			break;
		case USART_ENABLE_OUTPUT:
			ENABLE_OUTPUT;
			LCD_Cursor(0,14);
			LCD_Write("ON");
			break;
		case USART_DISABLE_OUTPUT:
			DISABLE_OUTPUT;
			LCD_Cursor(0,14);
			LCD_Write("  ");
			break;
		default:
			break;
		}
	}
}

// For the DAC (LTC1661) we must give one 16bit word 
// first four bits are control code, the next eight 
// are the actual data and the last two are ignored.
void transferToDAC(unsigned char CTRL,uint16_t a){
  	// Make sure a is a ten bit word
  	a &= 0x03FF;
	// Then shift up by two bits, the DAC does not
	// care about the two last bits!
	//a = a << 2; 
	// Shift the control code up by 4 bits
	CTRL = CTRL << 4;

	// Now we can transfer this to the DAC
  	// Take the DAC chip select low
  	SELECT_DAC;
  	// Transfer in two 8 bit steps
  	SPDR = CTRL | (a >> 6);
	while(!(SPSR & (1<<SPIF)));
	SPDR = (a << 2) & 0x00FF;
	while(!(SPSR & (1<<SPIF)));
  	// Restore the chip select
  	DESELECT_DAC;
}

void MENU_Home(void)
{
	// Write normal home screen
	LCD_Clear();
	LCD_Cursor(0,0);
	LCD_Write("V: ");
	LCD_Cursor(1,0);
	LCD_Write("I: ");

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

	if(OUTPUT_IS_ENABLED)
	{
		LCD_Cursor(0,14);
		LCD_Write("ON");
	}
	else
	{
		LCD_Cursor(0,14);
		LCD_Write("  ");
	}

}

void MENU_Backlight(void)
{
	// Write small backlight screen
	LCD_Clear();
	LCD_Cursor(0,3);
	LCD_Write("Backlight");
	LCD_Cursor(1,0);
	LCD_Write("[              ]");
	LCD_Cursor(1,1);
	uint8_t i = backlight;
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
			if(dir == ENCODER_CW) 	backlight += 1; 
			else					backlight -= 1;
			if(backlight > 20)
				backlight = 0;
			else if(backlight > 13)
				backlight = 13;
			else
			{
				OCR1B = 19*backlight;
				LCD_Cursor(1,0);
				LCD_Write("[              ]");
				LCD_Cursor(1,1);
				for(i = backlight; i>0; i--)
				{
					LCD_Write("=");
				}
				LCD_Write(">");
			}
		}
	}
}

// unfortunatly we need to reverse the bit order for the
// SPI interface to the 595 for the display. This is only
// four bits so we will just use a simple lookup table
//unsigned char reverseLastFourBits(unsigned char x)
//{
//	static const unsigned char lookup[16] = {
//   							0x0, 0x8, 0x4, 0xC,
//   							0x2, 0xA, 0x6, 0xE,
//   							0x1, 0x9, 0x5, 0xD,
//   							0x3, 0xB, 0x7, 0xF };
	
//	return x; //lookup[x&0x0F];	
//}


