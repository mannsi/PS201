#include "IOHandler.h"

void IOSetOutput(port po, pin pi)
{
  BIT_SET(*(po.direction),BIT(pi));
}

void IOSetInput(port po, pin pi)
{
  BIT_CLEAR(*(po.direction),BIT(pi));
}

void IOEnablePullup(port po, pin pi)
{
  IOSetPin(po,pi);
}

void IOSetPin(port po, pin pi)
{
  BIT_SET(*(po.output),BIT(pi));
}

void IOClearPin(port po, pin pi)
{
  BIT_CLEAR(*(po.output),BIT(pi));
}

void IOTogglePin(port po, pin pi)
{
  BIT_FLIP(*(po.output),BIT(pi));
}

unsigned char IOGetPin(port po, pin pi)
{
  return BIT_GET(*(po.input),BIT(pi));
}

void IOEnableInterrupt(port po, pin pi)
{
  BIT_SET(*(po.interrupt),BIT(pi));
}

void IODisableInterrupt(port po, pin pi)
{
  BIT_CLEAR(*(po.interrupt),BIT(pi));
}

void IODisableAllInterrupts(port po)
{
  BIT_CLEAR(*(po.interrupt),0xFF);
}

void IOTurnOnPinChangeInterrupt(port po)
{
  BIT_SET(*(po.interruptEnableRegister),BIT(po.interruptEnableBit));
}

void IOTurnOffPinChangeInterrupt(port po)
{
  BIT_CLEAR(*(po.interruptEnableRegister),BIT(po.interruptEnableBit));
}

void IOSetAllPins(port po, unsigned char val)
{
  *(po.output) = val;
}

unsigned char IOGetAllPins(port po)
{
  return *(po.input);
}

// Definitions of ports
port portB = {.direction = &DDRB, 
	      .output = &PORTB, 
	      .input = &PINB, 
	      .interrupt = &PCMSK0, 
	      .interruptEnableRegister = &PCICR,
	      .interruptEnableBit = PCIE0
};
port portC = {.direction = &DDRC, 
	      .output = &PORTC, 
	      .input = &PINC, 
	      .interrupt = &PCMSK1,
	      .interruptEnableRegister = &PCICR,
	      .interruptEnableBit = PCIE1
};
port portD = {.direction = &DDRD, 
	      .output = &PORTD, 
	      .input = &PIND, 
	      .interrupt = &PCMSK2,
	      .interruptEnableRegister = &PCICR,
	      .interruptEnableBit = PCIE2
};