#ifndef SERIAL_H
#define SERIAL_H

#include "USART.h"
#include<util/crc16.h>

#define SERIAL_ACK			(0x06)
#define SERIAL_NAK			(0x15)

#define SERIAL_SEND_VOLTAGE 		(0xD0)
#define SERIAL_RECEIVE_VOLTAGE 		(0xC0)
#define SERIAL_SEND_CURRENT 		(0xD1)
#define SERIAL_RECEIVE_CURRENT 		(0xC1)
#define SERIAL_SEND_VIN	 		(0xD2)
#define SERIAL_SEND_VPREREG 		(0xD3)
#define SERIAL_ENABLE_OUTPUT		(0xC2)
#define SERIAL_DISABLE_OUTPUT		(0xC3)
#define SERIAL_IS_OUTPUT_ON  		(0xC4)
#define SERIAL_SEND_SET_VOLTAGE		(0xE0)
#define SERIAL_SEND_SET_CURRENT		(0xE1)
#define SERIAL_SEND_HANDSHAKE		(0xA0)
#define SERIAL_HANDSHAKE		(0xA1)
#define SERIAL_WRITEALL			(0xA5)
#define SERIAL_WRITEALLCOMMANDS		(0xBB)
#define SERIAL_ENABLE_STREAM		(0xA2)
#define SERIAL_DISABLE_STREAM		(0xA3)

#define SERIAL_ESC			(0x7D)
#define SERIAL_START			(0x7E)
#define SERIAL_END			(0x7E)
#define SERIAL_FLIPBIT			(0x20)
#define SERIAL_RETURN			(0x0D)
#define SERIAL_NEWLINE			(0x0A)

// Shortcuts for the serial communication
#define MAXLEN 80
#define getpacket(_cmd,_data) SERIAL_GetPacket(_cmd,_data,MAXLEN)
#define sendpacket(_cmd,_data) SERIAL_SendPacket(_cmd,_data)
#define sendcmd(_cmd) SERIAL_SendCmd(_cmd)
#define sendACK() sendcmd(SERIAL_ACK)
#define sendNAK() sendcmd(SERIAL_NAK)

void SERIAL_Initialize(void);

int SERIAL_IsReceivingData(void);
uint8_t SERIAL_GetPacket(uint8_t *cmd, char *data, uint8_t maxlen);
void SERIAL_SendPacket(uint8_t cmd, char *data);
void SERIAL_SendCmd(uint8_t cmd);

#endif