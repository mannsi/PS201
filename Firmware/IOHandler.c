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

unsigned char IOGetPin(port po, pin pi)
{
	return BIT_GET(*(po.input),BIT(pi));
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
