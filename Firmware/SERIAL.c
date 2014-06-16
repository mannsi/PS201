#include "SERIAL.h"

void SERIAL_Initialize(void)
{
  USART_Initialize();
}

int SERIAL_IsReceivingData()
{
  return USART_IsReceivingData();
}

// Decode character by character from serial
static uint8_t DecodeChar(uint8_t *c)
{
  *c = getchar();
  // Remember to put end char in the string if we get the 
  // end char signal. THIS WILL NOT BE ESCAPED!
  if (*c == SERIAL_END)
  {
    *c = '\0';
    return 1;
  }

  // If we get the escape character we xor the NEXT char in the stream
  // with the FLIPBIT char
  if (*c == SERIAL_ESC)
  {
    *c = (SERIAL_FLIPBIT ^ getchar());
  }
  return 0;
}

uint8_t SERIAL_GetPacket(uint8_t *cmd, char *data)
{
  // Tha data structure is
  // <SFLAG><CMD><LEN><DATA[LEN]><CRC><EFLAG>
  // This function returns CMD.

  // Catch the SFLAG	
  uint8_t buffer = getchar();
  if(buffer != SERIAL_START)
  {
    *cmd = buffer;
    return 0;
  }

  // Next the CMD
  if (DecodeChar(cmd))
  {
    *cmd = SERIAL_NAK;
    return *cmd;
  }

  // The LEN
  uint8_t len = 0;
  if (DecodeChar(&len))
  {
    *cmd = SERIAL_NAK;
    return *cmd;
  }

  // Now we find the DATA, first we check if len 
  // exceeds maxlen
  if(len > MAXLEN)
  {
    *cmd = SERIAL_NAK;
    return *cmd;
  }
  else if(len != MAXLEN)
  {
  data[len] = '\0';
  }

  int i;
  for (i = 0; i < len; i++)
  {
    if (DecodeChar(&(data[i])))
    {
      *cmd = SERIAL_NAK;
      return *cmd;
      
    }
  }

  // Finally we retrieve the CRC code
  // High byte
  uint16_t crc = 0xFFFF;
  if (DecodeChar(&buffer))
  {
    *cmd = SERIAL_NAK;
    return *cmd;
  }

  crc = ((uint16_t) buffer);
  crc = crc << 8;
  // Low byte
  if (DecodeChar(&buffer))
  {
    *cmd = SERIAL_NAK;
    return *cmd;
  }
  crc |= ((uint16_t) buffer);

  // Check that the stop flag is provided
  if (getchar() != SERIAL_END)
  {
    *cmd = SERIAL_NAK;
    return *cmd;
  }

  // Do a CRC check
  // We use a crc function provided by <util/crc16.h>
  uint16_t calculatedCrc = 0;
  calculatedCrc = _crc_xmodem_update(calculatedCrc,*cmd);
  calculatedCrc = _crc_xmodem_update(calculatedCrc,len);
  for (i = 0; i < len; i++)
  {
    calculatedCrc = _crc_xmodem_update(calculatedCrc,data[i]);
  }

  // The calculated crc should now be equal to the crc received.
  if (crc != calculatedCrc)
  {
    *cmd = SERIAL_NAK;
    return *cmd;
  }

  return *cmd;
}

static void EncodeChar(uint8_t c)
{
  // We escape special characters by sending first the ESC char
  // and then xoring the character to be sent with the FLIPBIT char.
  if (c == SERIAL_END)
  {
    putchar(SERIAL_ESC);
    putchar(SERIAL_FLIPBIT ^ c);
  }
  else if (c == SERIAL_ESC)
  {
    putchar(SERIAL_ESC);
    putchar(SERIAL_FLIPBIT ^ c);
  }
  else if (c == SERIAL_RETURN)
  {
    putchar(SERIAL_ESC);
    putchar(SERIAL_FLIPBIT ^ c);
  }
  else if (c == SERIAL_NEWLINE)
  {
    putchar(SERIAL_ESC);
    putchar(SERIAL_FLIPBIT ^ c);
  }
  else 
  {
    putchar(c);
  }
}

// This is similar to getting a packet, see
// SERIAL_GetPacket for more comments.
void SERIAL_SendPacket(uint8_t cmd, char *data)
{
  // Calculate the length of the data
  uint8_t len= (strlen(data));

  // Calculate the CRC code
  uint16_t crc = 0x0000;
  crc = _crc_xmodem_update(crc,cmd);
  crc = _crc_xmodem_update(crc,len);
  int i;
  for (i = 0; i < len; i++)
  {
    crc = _crc_xmodem_update(crc,data[i]);
  }

  // Send the packet
  putchar(SERIAL_START);
  EncodeChar(cmd);
  EncodeChar(len);
  for (i = 0; i < len; i++)
  {
    EncodeChar((uint8_t) data[i]);
  }
  EncodeChar(((uint8_t) (crc >> 8)));
  EncodeChar(((uint8_t) crc));
  putchar(SERIAL_END);
}

// Sendpacket without any data
void SERIAL_SendCmd(uint8_t cmd)
{
  // We still send length of the data which is 0
  uint8_t len = 0;

  // Calculate the CRC code
  uint16_t crc = 0x0000;
  crc = _crc_xmodem_update(crc,cmd);
  crc = _crc_xmodem_update(crc,len);

  // Send the packet
  putchar(SERIAL_START);
  EncodeChar(cmd);
  EncodeChar(len);
  EncodeChar(((uint8_t) (crc >> 8)));
  EncodeChar(((uint8_t) crc));
  putchar(SERIAL_END);
}
