#include "Usb.h"

#include "USART.h"
#include "SerialParser.h"

#define MAX_SERIAL_LENGTH           80
#define SERIAL_ACK		            "ACK"
#define SERIAL_NAK			        "NAK"
#define SERIAL_WRITE_ALL_RESPONSE   "ALL"

/*
 * Fetches data packet from serial. Result stored in response
 * Returns: Bool if succesfull
 */
static int GetPacket(Decoded_input* response);

/*
 * Sends a packet to serial.
 */
static void SendPacket(char* cmd, char* data, uint8_t dataLength);

void USB_Initialize(void)
{
    USART_Initialize();
}

int USB_GetResponse(Decoded_input* response)
{
	if (USART_IsReceivingData())
	{
		return GetPacket(response);
	}
    return 0;
}

void USB_WriteAcknowledge(void)
{
    SendPacket(SERIAL_ACK, "", 0);
}

void USB_WriteNotAcknowledge(void)
{
    SendPacket(SERIAL_NAK, "", 0);
}

void USB_WriteAllValues(char* all_values, uint8_t allValuesLength)
{
	SendPacket(SERIAL_WRITE_ALL_RESPONSE, all_values, allValuesLength);
}

static int GetPacket(Decoded_input* response)
{
    char firstChar = getchar();
    if(firstChar != SERIAL_START)
    {
        return 0;
    }

    int i = 0;
    int nextChar;
    char input[MAX_SERIAL_LENGTH] = "";
    input[i++] = firstChar;

    do
    {
        nextChar = getchar();
        if (nextChar <= 32 || i > MAX_SERIAL_LENGTH)
        {
            // Chars below 32 are not characters but control signals
            return -1;
        }
        input[i++] = nextChar;
    } while(nextChar != SERIAL_END);

    int success = ParseSerialInput(input, i, response);
    if (success)
    {
        return 1;
    }
    else
    {
        return -1;
    }
    return success;

}

static void SendPacket(char* cmd, char* data, uint8_t dataLength)
{
    char output[MAX_SERIAL_LENGTH] = "";
    uint8_t outputLength = GenerateSerialOutput(cmd, data, dataLength, output);
    int i;
    for(i = 0; i < outputLength; i++)
    {
        putchar(output[i]);
    }

}




