#include "Tests.h"
#include "SerialParser.h"
#include "Debug.h"
#include "Structs.h"

static void TestDecodingCurInput(void);
static void TestGeneratingNormalOutput(void);
static void TestDecodingBrokenInput(void);
static void TestDecodingWrongCrcInput(void);
static void TestDecodingWrtAllInput(void);
static void TestDecodingVolInput(void);

void TestSerialParser()
{
    TestDecodingCurInput();
    TestDecodingWrongCrcInput();
    TestDecodingBrokenInput();
    TestDecodingWrtAllInput();
    TestGeneratingNormalOutput();
    TestDecodingVolInput();
}

static void TestGeneratingNormalOutput(void)
{
    WriteSimpleDebug("Parser testing: Encoding ...");

    char* expectedResult = "~CUR0510000B5C9~";
    char* cmd = "CUR";
    char* data = "10000";
    uint8_t dataLength = strlen(data);
    char output[16];
    uint8_t outputLength = GenerateSerialOutput(cmd, data, dataLength, output);

    if (!strcmp(expectedResult, output) != 0)
    {
        char *debugString = "FAIL. Unable to encode test data.";
        WriteDebug(debugString, strlen(debugString), expectedResult, strlen(expectedResult), output, outputLength);
    }
    else
    {
        WriteSimpleDebug("PASSED.");
    }
}

static void TestDecodingCurInput()
{
    WriteSimpleDebug("Parser testing: Decoding Cur data ...");

    char *input = "~CUR0510000B5C9~"; // Crc values are precalculated
    uint8_t inputLength = strlen(input);
    Decoded_input output;

    int returnValue = ParseSerialInput(input, inputLength, &output);
    if (!returnValue)
    {
        WriteSimpleDebug("FAIL. Unable to parse test data");
    }
    else if (strcmp(output.cmd, "CUR") != 0)
    {
        char *debugString = "FAIL. Wrong command. ";
        WriteDebug(debugString, strlen(debugString), "CUR", 3, output.cmd, 3);
    }
    else if (output.data != 10000)
    {
        WriteSimpleDebug("FAIL. Wrong data, exepected 10000 but got ");
        WriteIntDebug(output.data);
    }
    else if (strcmp(output.rawData, input) != 0)
    {
        char *debugString = "FAIL. Raw data output does not match input. ";
        WriteDebug(debugString, strlen(debugString), input, inputLength, output.rawData, inputLength);
    }
    else
    {
        WriteSimpleDebug("PASSED.");
    }
}

static void TestDecodingBrokenInput(void)
{
    WriteSimpleDebug("Parser testing: Decoding broken data ...");

    char *brokenInput = "~CUR051000~";
    uint8_t inputLength = strlen(brokenInput);
    Decoded_input output;

    int returnValue = ParseSerialInput(brokenInput, inputLength, &output);
    if (returnValue)
    {
        WriteSimpleDebug("FAIL. Returned true from parsing broken data.");
    }
    else
    {
        WriteSimpleDebug("PASSED.");
    }
}

static void TestDecodingWrongCrcInput(void)
{
    WriteSimpleDebug("Parser testing: Decoding with wrong crc data ...");

    char *wrongCrcInput = "~CUR0510000ABCD~";
    uint8_t inputLength = strlen(wrongCrcInput);
    Decoded_input output;

    int returnValue = ParseSerialInput(wrongCrcInput, inputLength, &output);
    if (returnValue)
    {
        WriteSimpleDebug("FAIL. Returned true from parsing wrong CRC.");
    }
    else
    {
        WriteSimpleDebug("PASSED.");
    }
}

static void TestDecodingWrtAllInput(void)
{
    WriteSimpleDebug("Parser testing: Decoding with Write all ...");

    char *writeAllInput = "~WRT005B7D~";
    uint8_t inputLength = strlen(writeAllInput);
    Decoded_input output;

    int returnValue = ParseSerialInput(writeAllInput, inputLength, &output);
    if (!returnValue)
    {
        WriteSimpleDebug("FAIL. Unable to parse Write all data");
    }
    else if (strcmp(output.cmd, "WRT") != 0)
    {
        char *debugString = "FAIL. Wrong command. ";
        WriteDebug(debugString, strlen(debugString), "WRT", 3, output.cmd, 3);
    }
    else if (strcmp(output.rawData, writeAllInput) != 0)
    {
        char *debugString = "FAIL. Raw data output does not match input. ";
        WriteDebug(debugString, strlen(debugString), writeAllInput, inputLength, output.rawData, inputLength);
    }
    else
    {
        WriteSimpleDebug("PASSED.");
    }
}

static void TestDecodingVolInput(void)
{
    WriteSimpleDebug("Parser testing: Decoding with Vol data ...");

    char *volInput = "~VOL0510000FCEC~";
    uint8_t inputLength = strlen(volInput);
    Decoded_input output;

    int returnValue = ParseSerialInput(volInput, inputLength, &output);
    if (!returnValue)
    {
        WriteSimpleDebug("FAIL. Unable to parse Write all data");
    }
    else if (strcmp(output.cmd, "VOL") != 0)
    {
        char *debugString = "FAIL. Wrong command. ";
        WriteDebug(debugString, strlen(debugString), "VOL", 3, output.cmd, 3);
    }
    else if (strcmp(output.rawData, volInput) != 0)
    {
        char *debugString = "FAIL. Raw data output does not match input. ";
        WriteDebug(debugString, strlen(debugString), volInput, inputLength, output.rawData, inputLength);
    }
    else
    {
        WriteSimpleDebug("PASSED.");
    }
}
