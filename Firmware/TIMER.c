#include "TIMER.h"

void TIMER_Initialize(void)
{
  // prescaler of 1024 (max)
  BIT_SET(TCCR0B,BIT(CS02));
  BIT_SET(TCCR0B,BIT(CS00));
}

void TIMER_ADC_Start(uint8_t time)
{
  // Initialize timer in CTC mode
  BIT_SET(TCCR0A,BIT(WGM01));
  // convert to 8-bit number
  OCR0A = time*F_CPU/1000/1024;
  // enable interrupt triggering
  BIT_SET(TIMSK0,BIT(OCIE0A));
}

void TIMER_ADC_Stop(void)
{
  // Stop timer
  BIT_CLEAR(TCCR0A,BIT(WGM01));
  // enable interrupt triggering
  BIT_CLEAR(TIMSK0,BIT(OCIE0A));
}