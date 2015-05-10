#include "ADC.h"
#include<avr/interrupt.h>
#include "Timer.h"
#include "IOHandler.h"

#define ADC_STARTCONVERSION ADCSRA |= 1 << ADSC
#define ADC_DELAY 20 //in ms

#define ADC_VOLTAGE_MON 0x07 // ADC7
#define ADC_CURRENT_MON 0x01 // ADC1
#define ADC_PREREG	0x02 // ADC2
#define ADC_VIN_MON	0x06 // ADC6

int number_of_oversamplings = 16;
int number_of_measurements = 256; //number_of_oversamplings * number_of_oversamplings;
int measured_voltage = 0;
int measured_current = 0;

int ADC_GetMeasuredVoltage()
{
	return measured_voltage;
}

int ADC_GetMeasuredCurrent()
{
	return measured_current;
}

void ADC_Initialize(void)
{
  ADMUX = 0;
  // Enable the ADC in interupt mode
  ADCSRA = 0;
  // Enable ADC
  BIT_SET(ADCSRA,BIT(ADEN));
  // Enable ADC interupt
  BIT_SET(ADCSRA,BIT(ADIE));
  // Set the ADC prescaler to 64 for ADC
  // clock of 125kHz.
  //BIT_SET(ADCSRA,BIT(ADPS0));
  BIT_SET(ADCSRA,BIT(ADPS1));
  BIT_SET(ADCSRA,BIT(ADPS2));
}

void ADC_StartMeasuringCurrent()
{
  ADMUX = 0;
  BIT_SET(ADMUX,ADC_CURRENT_MON);
  ADC_STARTCONVERSION;
}

void ADC_StartMeasuringVoltage()
{
  ADMUX = 0;
  BIT_SET(ADMUX,ADC_VOLTAGE_MON);
  ADC_STARTCONVERSION;
}

// The ADC interupt function is automatically triggered
// when the ADC has finished converting. Here we store
// the value. The main loop then restarts the DAC on
// a different channel.
ISR(ADC_vect)
{
  static uint32_t accumulated_voltage = 0;
  static uint32_t accumulated_current = 0;
  static int isMeasuringCurrent = 0;
  static int counter = 0;
  if (isMeasuringCurrent)
  {
	  accumulated_current += ADC;
	  isMeasuringCurrent = 0;
	  counter++;
	  ADC_StartMeasuringVoltage();
  }
  else
  {
	  accumulated_voltage += ADC;
	  isMeasuringCurrent = 1;
	  ADC_StartMeasuringCurrent();
  }

  if (counter == number_of_measurements)
  {
	  measured_voltage = (int)(accumulated_voltage / number_of_measurements);
	  measured_current = (int)(accumulated_current / number_of_measurements);
	  counter = 0;
	  accumulated_voltage = 0;
	  accumulated_current = 0;
  }
}

// Interrupt for the ADC timer.
ISR(TIMER0_COMPA_vect)
{
  TIMER_ADC_Stop();
  //ADC_STARTCONVERSION;
}

