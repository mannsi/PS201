#include "Tests.h"
#include "SerialParser.h"
#include "Debug.h"
#include "Structs.h"

static void TestDecodingNormalInput(void);
static void TestGeneratingNormalOutput(void);
static void TestDecodingBrokenInput(void);
static void TestDecodingWrongCrc(void);

void TestSerialParser()
{
    TestDecodingNormalInput();
    TestDecodingWrongCrc();
    TestDecodingBrokenInput();
    TestGeneratingNormalOutput();
}

static void TestGeneratingNormalOutput(void)
{
    char* testingEncoding = "Parser testing: Encoding ...";
    WriteSimpleDebug(testingEncoding, strlen(testingEncoding));

    char* expectedResult = "~CUR0510000B5C9~";
    char* cmd = "CUR";
    char* data = "10000";
    uint8_t dataLength = strlen(data);
    char output[16];
    uint8_t outputLength = GenerateSerialOutput(cmd, data, dataLength, output);

    if (!strcmp(expectedResult, output))
    {
        char *debugString = "FAIL. Unable to encode test data.";
        WriteDebug(debugString, strlen(debugString), expectedResult, strlen(expectedResult), output, outputLength);
    }
    else
    {
        char *debugString = "PASSED.";
        WriteSimpleDebug(debugString, strlen(debugString));
    }
}

static void TestDecodingNormalInput()
{
    char* testingDecoding = "Parser testing: Decoding ...";
    WriteSimpleDebug(testingDecoding, strlen(testingDecoding));

    char *input = "~CUR0510000B5C9~"; // Crc values are precalculated
    uint8_t inputLength = strlen(input);
    Decoded_input output;

    int returnValue = ParseSerialInput(input, inputLength, &output);
    if (!returnValue)
    {
        char *debugString = "FAIL. Unable to parse test data";
        WriteSimpleDebug(debugString, strlen(debugString));
    }
    else if (strcmp(output.cmd, "CUR"))
    {
        char *debugString = "FAIL. Wrong command. ";
        WriteDebug(debugString, strlen(debugString), "CUR", 3, output.cmd, 3);
    }
    else if (output.data != 10000)
    {
        char *debugString = "FAIL. Wrong data, exepected 10000 but got ";
        WriteSimpleDebug(debugString, strlen(debugString));
        WriteIntDebug(output.data);
    }
    else if (strcmp(output.rawData, input))
    {
        char *debugString = "FAIL. Raw data output does not match input. ";
        WriteDebug(debugString, strlen(debugString), input, inputLength, output.rawData, inputLength);
    }
    else
    {
        char *debugString = "PASSED.";
        WriteSimpleDebug(debugString, strlen(debugString));
    }
}

static void TestDecodingBrokenInput(void)
{
    char* testingDecoding = "Parser testing: Decoding broken data ...";
    WriteSimpleDebug(testingDecoding, strlen(testingDecoding));

    char *brokenInput = "~CUR051000~";
    uint8_t inputLength = strlen(brokenInput);
    Decoded_input output;

    int returnValue = ParseSerialInput(brokenInput, inputLength, &output);
    if (returnValue)
    {
        char *debugString = "FAIL. Returned true from parsing broken data.";
        WriteSimpleDebug(debugString, strlen(debugString));
    }
    else
    {
        char *debugString = "PASSED.";
        WriteSimpleDebug(debugString, strlen(debugString));
    }
}

static void TestDecodingWrongCrc(void)
{
    char* testingDecoding = "Parser testing: Decoding with wrong crc ...";
    WriteSimpleDebug(testingDecoding, strlen(testingDecoding));

    char *wrongCrcInput = "~CUR0510000ABCD~";
    uint8_t inputLength = strlen(wrongCrcInput);
    Decoded_input output;

    int returnValue = ParseSerialInput(wrongCrcInput, inputLength, &output);
    if (returnValue)
    {
        char *debugString = "FAIL. Returned true from parsing wrong CRC.";
        WriteSimpleDebug(debugString, strlen(debugString));
    }
    else
    {
        char *debugString = "PASSED.";
        WriteSimpleDebug(debugString, strlen(debugString));
    }
}
