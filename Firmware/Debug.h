#ifndef DEBUG_H
#define DEBUG_H

#include <stdio.h>

void WriteSimpleDebug(char* message);
void WriteDebug(char* message, uint8_t messageLength, char* expectedValue, uint8_t expectedValueLength, char* actualValue, uint8_t actualValueLength);
void WriteIntDebug(int number);

#endif
