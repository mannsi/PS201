#ifndef IOMAPPING_H
#define IOMAPPING_H

#include "IOHandler.h"

// SPI
#define SPI_MOSI_PORT	portA
#define SPI_MOSI_PIN	4
#define SPI_MISO_PORT	portA
#define SPI_MISO_PIN	2
#define SPI_SCK_PORT	portA
#define SPI_SCK_PIN	5
#define SPI_SS_PORT     portA
#define SPI_SS_PIN      6

// UART
#define UART_TRANSMIT_PORT  portA
#define UART_TRANSMIT_PIN   1
#define UART_RECEIVE_PORT   portA
#define UART_RECEIVE_PIN    0

// ADC
#define ADC_VOLTAGE_MON 0x03 // ADC3
#define ADC_CURRENT_MON 0x06 // ADC6
#define ADC_VIN_MON	0x09 // ADC9

// DAC
#define DAC_CS_PORT	portB
#define DAC_CS_PIN	1

// Output enable
#define SHUTDOWN_PORT	portB
#define SHUTDOWN_PIN	2

// Charge pump
#define CHARGEPUMP_PORT	portB
#define CHARGEPUMP_PIN	0

// Clock
#ifndef F_CPU
#define F_CPU 8000000
#endif

#endif
