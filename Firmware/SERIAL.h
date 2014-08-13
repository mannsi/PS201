#ifndef SERIAL_H
#define SERIAL_H

#include "USART.h"
#include<util/crc16.h>

#define SERIAL_ACK					(0x06)
#define SERIAL_NAK					(0x15)

#define SERIAL_ESC					(0x7D)
#define SERIAL_START				(0x7E)
#define SERIAL_END					(0x7E)
#define SERIAL_FLIPBIT				(0x20)
#define SERIAL_RETURN				(0x0D)
#define SERIAL_NEWLINE				(0x0A)

// Shortcuts for the serial communication
#define MAXLEN 80

void SERIAL_Initialize(void);

int SERIAL_IsReceivingData(void);
uint8_t SERIAL_GetPacket(uint8_t *cmd, char *data);
void SERIAL_SendPacket(uint8_t cmd, char *data);
void SERIAL_SendCmd(uint8_t cmd);

#endif
