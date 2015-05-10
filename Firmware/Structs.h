#ifndef STRUCTS_H
#define STRUCTS_H

typedef struct State_struct {
    int output_on;
    int target_voltage;
    int target_current;
    int output_voltage;
    int output_current;
} State_struct;


typedef struct Decoded_input{
    char cmd[4];
    int data;
    char* rawData;
} Decoded_input;

// Collect all port information in one struct
typedef struct
{
  volatile unsigned char *direction;			// Direction register
  volatile unsigned char *output;			// Output register, to output data to port
  volatile unsigned char *input;			// Input register, to read data from port
  volatile unsigned char *interrupt;			// Pin change interrupt for the port
  volatile unsigned char *interruptEnableRegister;	// Register and bit to enable and
  unsigned char interruptEnableBit;			// Disable the ports pin change interrupt.
} port;

#endif
