#ifndef SERIALPARSER_H
#define SERIALPARSER_H

#include "Structs.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define SERIAL_START		'~'
#define SERIAL_END			'~'

/*
 * Parses input and puts result in output
 * Returns: Bool if parsing was succesfull
 */
int ParseSerialInput(char* input, int inputLength, Decoded_input* output);

/*
 * Creates the serial output from cmd, data and dataLength. Result returned in output.
 * Returns: The length of output
 */
uint8_t GenerateSerialOutput(char* cmd, char* data, uint8_t dataLength, char* output);

#endif
