#ifndef IOMAPPING_H
#define IOMAPPING_H

#include "IOHandler.h"

// Switches
#define SW1_PORT	portD
#define SW1_PIN		4
#define SW2_PORT	portD
#define SW2_PIN		3
#define SW3_PORT	portD
#define SW3_PIN		2
#define SW4_PORT	portC
#define SW4_PIN		5
#define ENCODERA_PORT	portC
#define ENCODERA_PIN	3
#define ENCODERB_PORT	portC
#define ENCODERB_PIN	4

// SPI
#define SPI_MOSI_PORT	portB
#define SPI_MOSI_PIN	3
#define SPI_MISO_PORT	portB
#define SPI_MISO_PIN	4
#define SPI_SCK_PORT	portB
#define SPI_SCK_PIN	5

// LCD
#define LCD_ENABLE_PORT portD
#define LCD_ENABLE_PIN	5
#define LCD_CS_PORT	portD
#define LCD_CS_PIN	6
#define BACKLIGHT_PORT	portB
#define BACKLIGHT_PIN	2
#define CONTRAST_PORT	portB
#define CONTRAST_PIN	1

// ADC
#define ADC_VOLTAGE_MON 0x07 // ADC7
#define ADC_CURRENT_MON 0x01 // ADC1
#define ADC_PREREG	0x02 // ADC2
#define ADC_VIN_MON	0x06 // ADC6

// DAC
#define DAC_CS_PORT	portD
#define DAC_CS_PIN	7

// Output enable
#define SHUTDOWN_PORT	portC
#define SHUTDOWN_PIN	0
#define PREREG_PORT	portB
#define PREREG_PIN	0

#endif