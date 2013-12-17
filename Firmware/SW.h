#ifndef SW_H
#define SW_H

#include<avr/io.h>
#ifndef F_CPU
#define F_CPU 16000000
#endif
#include<util/delay.h>

// shortcuts for switches
#define SW1_IS_CLOSED !(PIND & (1 << PD4))
#define SW1_IS_OPEN   PIND & (1 << PD4)
#define SW1_WAS_OPEN (1 << 2)
#define SW2_IS_CLOSED !(PIND & (1 << PD3))
#define SW2_IS_OPEN   PIND & (1 << PD3)
#define SW2_WAS_OPEN (1 << 3)
#define SW3_IS_CLOSED !(PIND & (1 << PD2))
#define SW3_IS_OPEN   PIND & (1 << PD2)
#define SW3_WAS_OPEN (1 << 4)
#define SW4_IS_CLOSED !(PINC & (1 << PC5))
#define SW4_IS_OPEN   PINC & (1 << PC5)
#define SW4_WAS_OPEN (1 << 5)
#define ENCODERPINA_IS_CLOSED !(PINC & (1 << PC3))
#define ENCODERPINA_IS_OPEN PINC & (1 << PC3)
#define ENCODERPINA_WAS_OPEN (1 << 4)
#define ENCODERPINB_IS_CLOSED !(PINC & (1 << PC4))
#define ENCODERPINB_IS_OPEN PINC & (1 << PC4)
#define ENCODERPINB_WAS_OPEN (1 << 5)
#define ENCODER ((PINC >> PC3) & 0x03)
#define ENCODER_CCW 0x10

// To keep up with the encoder
#define VOLTAGE 	1 << 0
#define CURRENT 	1 << 1
#define BACKLIGHT 	1 << 2
#define DISABLED	1 << 8

void SW_Initialize(void);
unsigned char SW_CheckEncoder(void);
unsigned char SW_Check1(void);	// S1
unsigned char SW_Check2(void);	// S2
unsigned char SW_Check3(void);	// S3
unsigned char SW_Check4(void); 	// Encoder Switch

extern unsigned char SW_state;
extern unsigned char encoderControls;
unsigned char SW_encoderState;
#endif
