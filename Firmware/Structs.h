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
    char* cmd;
    int data;
    char* rawData;
} Decoded_input;

#endif
