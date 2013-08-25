// DIGITAL POWER SUPPLY
// ARDUINO SKETCH
// COPYRIGHT 2013
// WRITTEN BY: FRIDRIK F GAUTASON


// SKETCH VERSION 1.0
// BOARD VERSION 1.1


// PIN CONFIGURATION:
// PD0: Rotary Encoder 1b
#define encoder1PinB PD0
// PD1: Rotary Encoder 1 Switch
#define encoder1Switch PD1
// PD2: Rotary Encoder 1a (interupt)
#define encoder1PinA PD2
// PD3: Rotary Encoder 2a (interupt)
#define encoder2PinA PD3
// PD4: Rotary Encoder 2b
#define encoder2PinB PD4
// PD5: LED Display Chip Select
// PD6: Constant Voltage indicator
// PD7: Constant Current indicator

// PB0: Regulator Shutdown (active low)
// PB1: Charge Pump (OC1A)
// PB2: DAC Chip Select
// PB3: SPI MOSI
// PB4: SPI MISO
// PB5: SPI CLOCK

// PC0: Output Voltage Monitor
#define voltageMon PC0
// PC1: Output Current Monitor
#define currentMon PC1
// PC2: Pre Regulator Voltage Monitor
// PC3: Temperature Monitor
// PC5: Rotary Encoder 2 Switch

// INCLUDE SPI LIBRARY
#include <SPI.h>

// VARIABLES
// Encoder 1
boolean enc1Rotating = 1;
boolean enc1StateA = 0, enc1StateB = 0;
boolean enc1PreSwitch = 0;
// Encoder 2
boolean enc2Rotating = 1;
boolean enc2StateA = 0, enc2StateB = 0;
boolean enc2PreSwitch = 0;

// Voltage and current set
int voltageSet = 0;
int currentSet = 0;

// The display shows either voltage or current
boolean displayShowsVoltage = 1;

// Display shows set values for number of cycles
// before reading the output
int numDisplayCycles = 100;
int displayCounter = 0;

// Voltage and current read variables
long voltageRead = 0;
long voltagePreRead = 0;
long currentRead = 0;
long currentPreRead = 0;
int numAverages = 10;
int readCounter = 0;

void setup() {
  // Setup Port D OUTPUTS
  DDRD  = (1 << PORTD5);  
  // Setup Port B OUTPUTS
  DDRB  = (1 << PORTB0) | (1 << PORTB1) | (1 << PORTB2);  
  // Setup Port C OUTPUTS
  //DDRC  = (1 << PORTB0) | (1 << PORTB1) | (1 << PORTB2);
  // All inputs
  
  // Do not need to set the SPI pins as outputs.
  // initialize SPI
  SPI.begin();
  SPI.setBitOrder(MSBFIRST); 
  SPI.setDataMode(3);
  
  // Take the Chip select pins high
  PORTD |= (1 << PD5);
  PORTB |= (1 << PB2);
  
  // Initialize the charge pump (page 96 of datasheet)
  TCCR1A = (1 << COM1A1) | (1 << WGM10) | (1 << WGM11);
  OCR1A = 0xFDFF;
  TCCR1B = (1 << CS10);

  // SETUP THE ADC REFERENCE
  analogReference(DEFAULT);
  
  // Attach the interrupt functions
  attachInterrupt(0, rotEncoder1, RISING);
  attachInterrupt(1, rotEncoder2, RISING);
  
  // Set the voltage
  transferVoltage(0);
  
}

void loop() {  
  // Rotating encoder 1 sets voltage
  while(enc1Rotating){
    // No acceleration detection.
    // If both pins are high, the encoder is rotating clockwise
    // otherwise if one is high and other low the encoder is
    // rotating counter clockwise
    if(enc1StateA && enc1StateB){
      // Step voltage in steps of 50mV
      if(voltageSet < 2496) voltageSet += 5;
    }
    else if (enc1StateA && !enc1StateB)
      if(voltageSet > 4) voltageSet -= 5;
    
    // Update the voltage output
    transferVoltage(voltageSet*10/14);
    enc1Rotating = false;
    displayCounter = numDisplayCycles;
  }
  
  // Rotating encoder 2 sets current
  while(enc2Rotating){
    // No acceleration detection.
    // If both pins are high, the encoder is rotating clockwise
    // otherwise if one is high and other low the encoder is
    // rotating counter clockwise
    if(enc2StateA && enc2StateB){
      // Step current in steps of 10mA
      if(currentSet < 100) currentSet++;
    }
    else if (enc2StateA && !enc2StateB)
      if(currentSet > 0) currentSet--;
    
    // Update the current output
    transferCurrent(currentSet*7/10);
    enc2Rotating = false;
    displayCounter = numDisplayCycles;
  }
  
  // The switch on encoder 1 toggles the display from showing
  // voltage to current and back.
  if(!digitalRead(encoder1Switch) && !enc1PreSwitch){
    displayShowsVoltage = !displayShowsVoltage;
    displayCounter = 0;  
    enc1PreSwitch = true;
  }
  if(digitalRead(encoder1Switch) && enc1PreSwitch)
    enc1PreSwitch = false;
    
  // Read voltage and current and average
  voltageRead += (long) analogRead(voltageMon)*2850*10/1024;
  currentRead += (long) analogRead(currentMon)*1500*10/1024;
  readCounter++;
  // After doing averages we reset the variables and counter
  if(readCounter >= numAverages){
    voltagePreRead = voltageRead/numAverages/10;
    currentPreRead = currentRead/numAverages/10;
    readCounter = 0;
    voltageRead = 0;
    currentRead = 0;
  }
    
  // Writing to the display
  if(displayShowsVoltage){
    if(displayCounter > 0){
      displayCounter--;
      sevenSegmentWrite(voltageSet,2);
    } 
    else
      sevenSegmentWrite(voltagePreRead,2);
  }
  else{
    if(displayCounter > 0){
      displayCounter--;
      sevenSegmentWrite(currentSet,2);
    } 
    else
      sevenSegmentWrite(currentPreRead,2);
  }
}

// WRITE TO THE SEVEN SEGMENT DISPLAY
void sevenSegmentWrite(long numberToWrite, int decimal)
{
  byte byteToWrite;
  int digitNumber = 1;
  long currentDigit;
  
  decimal != 0 && decimal++;
  
  
  // Run through the digits of the numbers and shift out the digit.
  while(numberToWrite != 0 || decimal > 0)
  {
    // A simple procedure to get the least significant digit.
    currentDigit = numberToWrite;
    numberToWrite = numberToWrite/10;
    currentDigit = currentDigit - 10*numberToWrite;
  
    switch (currentDigit){
      case 0:
        byteToWrite = 3;
        break;
      case 1:
        byteToWrite = 159;
        break;
      case 2:
        byteToWrite = 37;
        break;
      case 3:
        byteToWrite = 13;
        break;
      case 4:
        byteToWrite = 153;
        break;
      case 5:
        byteToWrite = 73;
        break;
      case 6:
        byteToWrite = 65;
        break;
      case 7:
        byteToWrite = 31;
        break;
      case 8:
        byteToWrite = 1;
        break;
      case 9:
        byteToWrite = 9;
        break;
    }
    // determine if the decimal point should be written
    if(decimal == 1)
      byteToWrite -= 1;
    decimal > 0 && decimal--;
    
    // take the latchPin low so 
    // the LEDs don't change while you're sending in bits:
    PORTD &= ~(1 << PD5);
    // shift out the bits:
    
    SPI.transfer(byteToWrite);
    SPI.transfer(16/digitNumber);

    //take the latch pin high so the LEDs will light up:
    PORTD |= (1 << PD5);
    
    // count the digit number
    digitNumber = digitNumber*2;
    delay(2);
  }
}

// Interrupt function which only turns on the rotating flag
// when detected.
void rotEncoder1(){
  // Check the state of the encoder
  enc1StateA = digitalRead(encoder1PinA);
  enc1StateB = digitalRead(encoder1PinB);
  enc1Rotating = true;
}
void rotEncoder2(){
  // Check the state of the encoder
  enc2StateA = digitalRead(encoder2PinA);
  enc2StateB = digitalRead(encoder2PinB);
  enc2Rotating = true;
}

// For the DAC (LTC1661) we must give one 16bit word 
// but as the spi transfer function only transfer 8bit
// words, we must transfer two 8bit words in a row.
// For this we must manipulate the voltage slightly.
void transferVoltage(int a){
  // create two bytes
  byte spiFirst, spiSecond;
  
  // shift a (a ten bit word) up by two bits
  a = a << 2;
  // Then the spiSecond is the lowest byte of a
  spiSecond = lowByte(a);
  // The spiFirst should have four control bits
  // followed by the first four bits of a.
  spiFirst = 9 << 4; 
  // the byte 10010000 tells the DAC to set the A output
  // and turn it on
  spiFirst = spiFirst | highByte(a);
  
  // Now we can transfer this to the DAC
  // Take the DAC chip select low
  PORTB &= ~(1 << PB2);
  // Transfer
  SPI.transfer(spiFirst);
  SPI.transfer(spiSecond);
  // Restore the chip select
  PORTB |= (1 << PB2);
}

// A copy of the above function with different control 
// signal to the DAC
void transferCurrent(int a){
  // create two bytes
  byte spiFirst, spiSecond;
  
  // shift a (a ten bit word) up by two bits
  a = a << 2;
  // Then the spiSecond is the lowest byte of a
  spiSecond = lowByte(a);
  // The spiFirst should have four control bits
  // followed by the first four bits of a.
  spiFirst = 10 << 4; 
  // the byte 10100000 tells the DAC to set the A and B output
  // and turn it on
  spiFirst = spiFirst | highByte(a);
  
  // Now we can transfer this to the DAC
  // Take the DAC chip select low
  PORTB &= ~(1 << PB2);
  // Transfer
  SPI.transfer(spiFirst);
  SPI.transfer(spiSecond);
  // Restore the chip select
  PORTB |= (1 << PB2);
}

