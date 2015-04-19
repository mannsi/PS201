#include "Debug.h"
#include "USART.h"

void WriteSimpleDebug(char* message, uint8_t messageLength)
{
    int i;
    for(i=0; i < messageLength; i++)
    {
        putchar(message[i]);
    }
    putchar('\n');
}

void WriteDebug(char* message, uint8_t messageLength, char* expectedValue, uint8_t expectedValueLength, char* actualValue, uint8_t actualValueLength)
{
    char* expected = "Expected: ";
    char* actual = ". Actual:";

    int i;
    for(i=0; i < messageLength; i++)
    {
        putchar(message[i]);
    }
    for(i=0; i < strlen(expected); i++)
    {
        putchar(expected[i]);
    }
    for(i=0; i < expectedValueLength; i++)
    {
        putchar(expectedValue[i]);
    }
    for(i=0; i < strlen(actual); i++)
    {
        putchar(actual[i]);
    }
    for(i=0; i < actualValueLength; i++)
    {
        putchar(actualValue[i]);
    }
    putchar('\n');
}

void WriteIntDebug(int number)
{
    char numberArray[7];
    sprintf(numberArray, "%i", number);
    int i;
    for (i=0; i< strlen(numberArray); i++)
    {
        putchar(numberArray[i]);
    }
    putchar('\n');
}
