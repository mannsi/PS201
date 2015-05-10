#ifndef DAC_H
#define DAC_H

#include <stdint.h>

void DAC_Initialize(void);

/*
 * Set the data value for the given data type
 * data_type: values 10 for voltage, 9 for current
 */
void DAC_SetValue(unsigned char data_type,uint16_t data);

#endif
