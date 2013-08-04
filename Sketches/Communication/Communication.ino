/*
 * Awesome arduino program
 */

#include <EEPROM.h>

// Variables
const int ledPin_13 = 13;
const int programId = 17;
const int handshakeId = 7;
const int writeRealVoltage = 8;
const int writeRealCurrent = 9;
const int readTargetVoltage = 10;
const int readTargetCurrent = 11;
const int writeTargetVoltage = 12;
const int writeTargetCurrent = 13;
const int ledStateChange = 14;
int targetVoltage = 3;
int targetCurrent = 3;

//Inputs
byte inputProgramId;
byte inputCommand;

void setup() {
  pinMode(ledPin_13, OUTPUT);
  Serial.begin(9600);
  Serial.print(handshakeId);
}

void loop() {
  if (Serial.available()  == 3) 
  {
    inputProgramId = Serial.read();
    if(inputProgramId == programId)
    {
      delay(100);  
      inputCommand = Serial.read();
      switch (inputCommand) 
       {
          case writeRealVoltage:
            Serial.print(8);
            break;
          case writeRealCurrent:
            Serial.print(9);
            break;
          case readTargetVoltage:
            targetVoltage = Serial.read();
            for (int i = 0; i < targetVoltage; i++) { 
              digitalWrite(ledPin_13, HIGH);   
              delay(500);                  
              digitalWrite(ledPin_13, LOW);  
              delay(500); 
            }
            break;
          case readTargetCurrent:
            //targetCurrent = Serial.read();
            break;
          case writeTargetVoltage:
            Serial.print(targetVoltage);
            break;
          case writeTargetCurrent:
            Serial.print(targetCurrent);
            break;
          case ledStateChange:
            int ledState = Serial.read();
            if (ledState == 0)
            {
              digitalWrite(ledPin_13, LOW);
            }
            else 
            {
              digitalWrite(ledPin_13, HIGH);
            }
            break;
        } 
        // Clear input
        inputProgramId = 0;
        inputCommand = 0;
    }  
  }
}
