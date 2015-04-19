#include "SerialParser.h"

#include<util/crc16.h>
#include "Debug.h"

#define SERIAL_ESC				    (0x7D)
#define SERIAL_FLIPBIT				(0x20)
#define SERIAL_RETURN				(0x0D)
#define SERIAL_NEWLINE				(0x0A)

#define CMD_CHAR_LENGTH             3
#define LEN_CHAR_LENGTH             2
#define CRC_CHAR_MIN_LENGTH         4
#define CRC_CHAR_MAX_LENGTH         8

/*
 * Populates hexCrc parameter with hex char crc values from other parameters
 * Returns: Length of hexCrc
 */
static uint8_t GetHexCrc(char* hexCrc, char* cmd, char* lenArray, char* data);

/*
 * Checks if value c needs to be escaped
 * Returns: Bool if c needs escaping
 */
static int ValueNeedsEscaping(uint8_t c);

uint8_t GenerateSerialOutput(char* cmd, char* data, uint8_t dataLength, char* output)
{
    int index = 0;
    output[index++] = SERIAL_START;
    int i;
    for (i = 0; i < CMD_CHAR_LENGTH; i++)
    {
        output[index++] = cmd[i];
    }

    char lenArray[LEN_CHAR_LENGTH + 1];
    sprintf(lenArray, "%02X", dataLength);

    for (i = 0; i < LEN_CHAR_LENGTH; i++)
    {
        output[index++] = lenArray[i];
    }

    for (i = 0; i < dataLength; i++)
    {
        output[index++] = data[i];
    }

    // At most 4 item crc array possible. Each crc item maps to a 2 item hex string.
    char hexCrc[CRC_CHAR_MAX_LENGTH] = "";
    uint8_t hexCrcLength = GetHexCrc(hexCrc, cmd, lenArray, data);
    i = 0;
    for(i = 0; i < hexCrcLength; i++)
    {
        output[index++] = hexCrc[i];
    }

    output[index++] = SERIAL_END;

    return index;
}

/*
Parses serial stream from input. Returns bool if succesfull
*/
int ParseSerialInput(char* input, int inputLength, Decoded_input* output)
{
    int minLength = 1 + CMD_CHAR_LENGTH + LEN_CHAR_LENGTH + CRC_CHAR_MIN_LENGTH + 1;
    if (inputLength < minLength) return 0;

    uint8_t index = 0;

    // Ignore if it does not start with serial start
    uint8_t start = input[index++];
    if(start != SERIAL_START)
    {
      return 0;
    }

    char cmd[CMD_CHAR_LENGTH + 1];
    // Get the command
    cmd[0] = input[index++];
    cmd[1] = input[index++];
    cmd[2] = input[index++];
    cmd[3] = 0;

    // Get length and convert to int
    char dataLengthArray[LEN_CHAR_LENGTH + 1] = "";
    dataLengthArray[0] = input[index++];
    dataLengthArray[1] = input[index++];
    dataLengthArray[2] = 0;

    uint8_t dataLength = (int)strtol(dataLengthArray, 0, 16);

    char data[dataLength];
    int i;
    for (i = 0; i < dataLength; i++)
    {
        data[i] = input[index++];
    }

    // Finally we retrieve the CRC code
    char readCrcArray[CRC_CHAR_MAX_LENGTH] = "";
    i = 0;
    do
    {
        readCrcArray[i++] = input[index++];
    } while(input[index] != SERIAL_END && input[index] != 0 && index <= inputLength);

    char calculatedCrcArray[CRC_CHAR_MAX_LENGTH] = "";
    uint8_t calculatedArrayLength = GetHexCrc(calculatedCrcArray, cmd, dataLengthArray, data);
    uint8_t readCrcArrayLength = i;

    for (i = 0; i < calculatedArrayLength; i++)
    {
        if (readCrcArray[i] != calculatedCrcArray[i])
        {
            return 0;
        }
    }

    // Check that the stop flag is provided
    if (input[index] != SERIAL_END) return 0;

    // Copy the values to the output variable
    output->rawData = input;
    output->cmd = cmd;
    output->data = (int)strtol(data, NULL, 10);
    return 1;
}

static int ValueNeedsEscaping(uint8_t c)
{
    if (c == SERIAL_END || c == SERIAL_ESC || c == SERIAL_RETURN || c == SERIAL_NEWLINE)
    {
        return 1;
    }
    return 0;
}

static uint8_t GetHexCrc(char* hexCrc, char* cmd, char* lenArray, char* data)
{
    // There is probably a much better way to do everything in this function.
    // I just don't know how ...
    int i = 0;
    uint16_t crc = 0x0000;

    for (i = 0; i < CMD_CHAR_LENGTH; i++)
    {
        crc = _crc_xmodem_update(crc,cmd[i]);
    }

    for (i = 0; i < strlen(lenArray); i++)
    {
        crc = _crc_xmodem_update(crc,lenArray[i]);
    }

    for (i = 0; i < strlen(data); i++)
    {
        crc = _crc_xmodem_update(crc,data[i]);
    }

    uint8_t intCrcArray[4] = "";

    uint8_t crc1 = (uint8_t) (crc >> 8);
    uint8_t crc2 = (uint8_t) crc;

    uint8_t index = 0;
    if (!ValueNeedsEscaping(crc1))
    {
        intCrcArray[index] = crc1;
        index++;
    }
    else
    {
        intCrcArray[index] = SERIAL_ESC;
        index++;
        intCrcArray[index] = (SERIAL_FLIPBIT ^ crc1);
        index++;
    }

    if (!ValueNeedsEscaping(crc2))
    {
        intCrcArray[index] = crc2;
        index++;
    }
    else
    {
        intCrcArray[index] = SERIAL_ESC;
        index++;
        intCrcArray[index] = (SERIAL_FLIPBIT ^ crc2);
        index++;
    }

    // Now we have a char array with escaped crc values.
    // Now we need to convert these values to hex strings.
    uint8_t numberOfCrcValues = index;
    index = 0;

    for(i = 0; i < numberOfCrcValues; i++)
    {
        uint8_t crcValue = intCrcArray[i];
        char tmpHexArray[3];
        sprintf(tmpHexArray, "%02X", crcValue);
        hexCrc[index++] = tmpHexArray[0];;
        hexCrc[index++] = tmpHexArray[1];
    }

    return index;
}


