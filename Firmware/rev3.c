/************************************
*                                   *
*        DIGITAL PSU REV 3          *
*        Fridrik F Gautason         *
*        Gudbjorn Einarsson         *
*        Copyright 2014             *
*                                   *
*************************************/

#include "rev3.h"

// MAGIC NUMBERS
#define MAXVOLTAGE 200
#define MAXCURRENT 100
#define NEGNUM 60000
#define DACVOLTAGE 10
#define DACCURRENT 9
#define NUMBITS 1024

// Use uint8_t (unsigned char) for variables that do not have to be 
// bigger than one byte.
uint8_t updateStartVoltage = 0;
uint8_t updateStartCurrent = 0;
uint8_t outputIsOn = 0;
uint8_t streamIsOn = 0;
uint8_t backlightIntensity = 10;
uint8_t contrast = 10;

// To keep track of the ADC 
ADC_MUX ADCmeasures = VOLTAGE;
// We store all measured voltages and current in a array of type
// PSUData, defined in the header. The four elements correspond
// exactly to the four measured voltages measured by the ADC.
// WARNING: through out the code I will use the ADC_MUX enum as
// an argument into the following arrays.
PSUData measured[4];
PSUData setting[2];
const unsigned char DAC_ctrlCode[2] = {DACVOLTAGE,DACCURRENT};

// The display and physical UI act as a state machine.
PSUState state = NORMAL;


// Delay variables, between read cycles. We do not
// want to be constantly running the ADC.
uint16_t readDelay = 10000;
uint16_t setDelay = 50000; 
uint16_t delay = 10000;

// To map the ADC_MUX variable to register locations
const unsigned char ADCregister[4] = {
  ADC_VOLTAGE_MON, ADC_CURRENT_MON, ADC_PREREG, ADC_VIN_MON
};

// Switches
button switch1 = {.switchPort = &SW1_PORT, .switchPin = SW1_PIN, .state = 0};
button switch2 = {.switchPort = &SW2_PORT, .switchPin = SW2_PIN, .state = 0};
button switch3 = {.switchPort = &SW3_PORT, .switchPin = SW3_PIN, .state = 0};
button switch4 = {.switchPort = &SW4_PORT, .switchPin = SW4_PIN, .state = 0};

int main(void)
{
  DISPLAY_Initialize(backlightIntensity,contrast);
  ADC_Initialize();
  DAC_Initialize();
  SERIAL_Initialize();
  
  initRegistries();
  //initCalibration();
  
  // Initialize switches
  SWITCH_Initialize(&switch1);
  SWITCH_Initialize(&switch2);
  SWITCH_Initialize(&switch3);
  SWITCH_Initialize(&switch4);
  
  // Set up rotary encoder
  IOSetInput(ENCODERA_PORT,ENCODERA_PIN);
  IOEnablePullup(ENCODERA_PORT,ENCODERA_PIN);
  IOSetInput(ENCODERB_PORT,ENCODERB_PIN);
  IOEnablePullup(ENCODERB_PORT,ENCODERB_PIN);
  
  DISPLAY_StartScreen();
  _delay_ms(1000);

  // Initialize PSU variables
  {
    PSUData defaultVoltage = {.analog=0, .digital=0, .multiplier=2.43, .offset=0, .maxAnalogValue=2000, .analogIncrements=10};
    PSUData defaultCurrent = {.analog=0, .digital=0, .multiplier=2.43, .offset=0, .maxAnalogValue=100, .analogIncrements=1};
    measured[VOLTAGE] = defaultVoltage;
    measured[PREREG]  = defaultVoltage;
    measured[VIN]     = defaultVoltage;
    setting[VOLTAGE]  = defaultVoltage;
    measured[CURRENT] = defaultCurrent;
    setting[CURRENT]  = defaultCurrent;
  }
  
  uint8_t encoderControls = VOLTAGE;
  
  //voltageSet = EEPROM_ReadNum(ADDR_STARTVOLTAGE);
  //currentSet = EEPROM_ReadNum(ADDR_STARTCURRENT);
  //DAC_transfer(DACVOLTAGE,((float)voltageSet)/voltageSetMulti);
  //DAC_transfer(DACCURRENT,((float)currentSet)/currentSetMulti);

  // Start in the home screen with the set valueschar data[8];
  {
    char vol[8];
    char cur[8];
    mapToString(&setting[VOLTAGE],vol);
    vol[6] = ' ';
    vol[7] = 'V';
    mapToString(&setting[CURRENT],cur);
    cur[6] = ' ';
    cur[7] = 'A';
    DISPLAY_HomeScreen(vol,cur,outputIsOn,encoderControls);
  }
  
  // Start the ADC
  ADC_StartMeasuring(ADCregister[ADCmeasures]);

  /************************
  *                       *
  *      MAIN LOOP        *
  *                       *
  *************************/

  while(1)
  {
    // loop control variables
    int newSetting = 0;
    // Read the ADC.
    int newMeasurement = readFromADC(&measured[ADCmeasures]);
    // Listen to USB commands.
    serialCommand newUSBCommand = readUSB();
    
    // The main state machine.
    switch(state){
      case NORMAL:
	if(newUSBCommand) state = setState(USBCONTROLLED);
	else
	{
	  // Read the UI switches and respond
	  UICommand newUICommand = readUI();
	  switch(newUICommand){
	    case NO_UI_COMMAND:
	      break;
	    case UP:
	      state = setState(MENU);
	      break;
	    case DOWN:
	      state = setState(MENU);
	      break;
	    case CANCEL:
	      toggleOutput();
	      newSetting = 1;
	      break;
	    case ENTER:
	      if(encoderControls==VOLTAGE) encoderControls = CURRENT;
	      else encoderControls = VOLTAGE;
	      newSetting = 1;
	      break;
	    case CLOCKWISE:
	      increaseAnalog(&setting[encoderControls]);
	      newSetting = 1;
	      break;
	    case COUNTERCLOCKWISE:
	      decreaseAnalog(&setting[encoderControls]);
	      newSetting = 1;
	      break;
	    default:
	      break;     
	  }
	}
	
	// Write to LCD
	if(newSetting)
	{
	  char data[8];
	  mapToString(&setting[VOLTAGE],data);
	  data[6] = ' ';
	  data[7] = 'V';
	  DISPLAY_WriteVoltage(data);
	  mapToString(&setting[CURRENT],data);
	  data[7] = 'A';
	  DISPLAY_WriteCurrent(data);
	}
	else if(newMeasurement)
	{
	  char data[8];
	  mapToString(&measured[VOLTAGE],data);
	  data[6] = ' ';
	  data[7] = 'V';
	  DISPLAY_WriteVoltage(data);
	  mapToString(&measured[CURRENT],data);
	  data[7] = 'A';
	  DISPLAY_WriteCurrent(data);
	}
	break;
      case USBCONTROLLED:
	break;
      case MENU:
	break;
      default:
	setState(NORMAL);
	break;
    }
    // Update the output.
    if(newSetting)
    {
      DAC_transfer(DAC_ctrlCode[encoderControls],setting[encoderControls].digital);
    }
    // Restart the ADC
    if(newMeasurement)
    {
      startADC(&ADCmeasures);
    }
  }
  return 0;
}

// TODO
PSUState setState(PSUState nextState)
{
  return NORMAL;
}

// Don't mess with order, priority is important.
UICommand readUI(void)
{
  if (SWITCH_Pressed(&switch1)) return CANCEL;
  if (SWITCH_Pressed(&switch4)) return ENTER;
  unsigned char encoderTurnDirection = SW_CheckEncoder();
  if(encoderTurnDirection)
  {
    if(encoderTurnDirection == ENCODER_CCW) return COUNTERCLOCKWISE;
    else return CLOCKWISE;
  }
  if (SWITCH_Pressed(&switch2)) return UP;
  if (SWITCH_Pressed(&switch3)) return DOWN;
  return NO_UI_COMMAND;
}

uint16_t mapToAnalog(PSUData* A)
{
  A->analog = (uint16_t) ((float) A->digital)*(A->multiplier) + (A->offset);
  return A->analog;
}

uint16_t mapToDigital(PSUData* A)
{
  A->digital = (uint16_t) ((float)((A->analog) - (A->offset)))/(A->multiplier);
  return A->digital;
}

int readFromADC(PSUData* A)
{
  // Check global variable:
  // WARNING This must be an ATOMIC operation since 
  // ADC_reading is accessed by the ISR.
  uint16_t reading;
  uint16_t oldReading;
  
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
  {
    reading = ADC_reading;
    ADC_reading = -1;
  }
  
  if(reading != -1)
  {
    oldReading = A->digital;
    if(oldReading != reading)
    {
      A->digital = reading;
      mapToAnalog(A);
      return 1;
    }
  }
  return 0;
}

// Increment the measuring varible AND start the ADC
void startADC(ADC_MUX *measuring)
{
  const static int nextMeasure[4] = {1,2,3,0};
  *measuring = nextMeasure[*measuring];
  
  ADC_StartMeasuring(ADCregister[*measuring]);
}

// Map the analog data of A to a character array in SI units, remember
// that by definition the analog variables are stored in 100ths of a 
// SI unit i.e. 10mV or 10mA
void mapToString(PSUData* A,char* S)
{
  uint16_t num = A->analog;
  S[0] = num < 1000 ? ' ' : (char) ( ((int) '0') + num / 1000 );
  S[1] = num < 100  ? '0' : (char) ( ((int) '0') + (num%1000) / (100) );
  S[2] = '.';
  S[3] = (char) ( ((int) '0') + (num%100));
  S[4] = (char) ( ((int) '0') + (num%10));
  S[5] = '\0';
}

// The inverse of the above function; map a string to the analog data
// of A. Remember that the  character array is in SI units, but we must
// store the analog variables in 1000ths of a SI unit i.e. 1mV or 1mA
void mapToNum(PSUData* A,char* S)
{
  char *a;
  char *b;
  uint16_t num = (uint16_t) (strtol(S,&a,0)*1000);
  // Find the fractional part of the number
  if(*a == '.')
  {
    uint16_t fraction = (uint16_t) strtol((a+1),&b,0);
    // Throw away extra digits
    while(fraction > 1000)
    {
      fraction = fraction/10;
    }
    num = num + fraction;
  }
  if(num <= A->maxAnalogValue)
  {
    A->analog = num;
  }
}

void increaseAnalog(PSUData* A)
{
  A->analog += A->analogIncrements;
  mapToDigital(A);
}

void decreaseAnalog(PSUData* A)
{
  A->analog -= A->analogIncrements;
  mapToDigital(A);
}

void logToUSB(PSUData* A,unsigned char cmd)
{
  char data[5];
  mapToString(A,data);
  sendpacket(cmd,data);
}

// To map the serialCommand to a meaningfull command
const unsigned char SERIALcode[13] = {
  SERIAL_SEND_VOLTAGE,
  SERIAL_SEND_CURRENT,
  SERIAL_SEND_VPREREG,
  SERIAL_SEND_VIN,
  SERIAL_SEND_SET_VOLTAGE,
  SERIAL_SEND_SET_CURRENT,
  SERIAL_RECEIVE_VOLTAGE,
  SERIAL_RECEIVE_CURRENT,
  SERIAL_ENABLE_OUTPUT,
  SERIAL_DISABLE_OUTPUT,
  SERIAL_IS_OUTPUT_ON,
  SERIAL_ENABLE_STREAM,
  SERIAL_DISABLE_STREAM
};

serialCommand readUSB(void)
{
  if (SERIAL_IsReceivingData())
  {
    // Listen for USB command
    uint8_t cmd = 0;
    char data[MAXLEN];
    char outputChar;
    if(getpacket(&cmd,data))
    {
      switch(cmd)
      {
	case SERIAL_NAK:
	  sendNAK();
	  break;
	case SERIAL_WRITEALL:
	  sendACK();
	  if (outputIsOn)
	  {
	    outputChar = '1';
	  }
	  else
	  {
	    outputChar = '0';
	  }
	  // NEEDS TO BE REWRITTEN
	  break;
	case SERIAL_SEND_HANDSHAKE:
	  sendACK();
	  break;
	case SERIAL_RECEIVE_VOLTAGE:
	  sendACK();
	  mapToNum(&setting[VOLTAGE],data);
	  return NEW_VOLTAGE;
	case SERIAL_SEND_VOLTAGE:
	  sendACK();
	  logToUSB(&measured[VOLTAGE],cmd);
	  break;
	case SERIAL_SEND_SET_VOLTAGE:
	  sendACK();
	  logToUSB(&setting[VOLTAGE],cmd);
	  break;
	case SERIAL_RECEIVE_CURRENT:
	  sendACK();
	  mapToNum(&setting[CURRENT],data);
	  return NEW_CURRENT;
	case SERIAL_SEND_CURRENT:
	  sendACK();
	  logToUSB(&measured[CURRENT],cmd);
	  break;
	case SERIAL_SEND_SET_CURRENT:
	  sendACK();
	  logToUSB(&setting[CURRENT],cmd);
	  break;
	case SERIAL_SEND_VIN:
	  sendACK();
	  logToUSB(&measured[VIN],cmd);
	  break;
	case SERIAL_SEND_VPREREG:
	  sendACK();
	  logToUSB(&measured[PREREG],cmd);
	  break;
	case SERIAL_ENABLE_OUTPUT:
	  sendACK();
	  enableOutput();
	  return OUTPUT_ON;
	case SERIAL_DISABLE_OUTPUT:
	  sendACK();
	  disableOutput();
	  return OUTPUT_OFF;
	case SERIAL_IS_OUTPUT_ON:
	  sendACK();
	  if (outputIsOn)
	  {
	    data[0] = '1';
	  }
	  else
	  {
	    data[0] = '0';
	  }
	  data[1] = '\0';
	  sendpacket(cmd,data);
	  break;
	case SERIAL_ENABLE_STREAM:
	  sendACK();
	  streamIsOn = 1;
	  break;
	case SERIAL_DISABLE_STREAM:
	  sendACK();
	  streamIsOn = 0;
	  break;
	default:
	  break;
      }
    }
  }
  return 0;
}

void toggleOutput(void)
{
  if(outputIsOn)
  {
    disableOutput();
  }
  else
  {
    enableOutput();
  }
}

void enableOutput()
{
  outputIsOn = 1;
  ENABLE_OUTPUT;
  ENABLE_PREREG;
}

void disableOutput()
{
  outputIsOn = 0;
  DISABLE_PREREG;
  DISABLE_OUTPUT;
}

static void initRegistries()
{
  // Turn off Bias
  IOSetOutput(SHUTDOWN_PORT,SHUTDOWN_PIN);
  IOSetOutput(PREREG_PORT,PREREG_PIN);
  outputIsOn = 0;
  DISABLE_PREREG;
  DISABLE_OUTPUT;
}

// static void initCalibration()
// {
//   // Calibration variables
//   // Read from EEPROM
//   voltageSetMulti  = ((float) EEPROM_ReadNum(ADDR_CALIBRATION))/1000.0;
//   if(voltageSetMulti == 0)
//   {
//     voltageSetMulti = 0.243;
//     EEPROM_WriteNum((uint16_t)voltageSetMulti*1000,ADDR_CALIBRATION);
//   }
//   voltageReadMulti = 11.0*voltageSetMulti/10.0;
//   currentSetMulti  = voltageSetMulti/0.2/11;
//   currentReadMulti = voltageSetMulti/0.2/11;
// }
// 
// void doCalibration()
// {
// 	uint16_t measuredVoltage = 500;
// 	uint16_t voltageCode = 200;
// 	unsigned char updateScreen = 1;
// 	unsigned char buffer[10];
// 
// 	disableOutput();
// 	LCD_Clear();
// 	LCD_Cursor(0,0);
// 	LCD_Write("--CALIBRATION-- ");
// 	LCD_Cursor(1,0);
// 	LCD_Write("Disconnect load ");
// 	_delay_ms(1000);
// 	LCD_Cursor(1,0);
// 	// turn on the output at code 256,
// 	// the user then measures the output.
// 	DAC_transfer(DACVOLTAGE, voltageCode);
// 	DAC_transfer(DACCURRENT, 10.0 / currentSetMulti);
// 	ENABLE_OUTPUT;
// 	ENABLE_PREREG;
// 	LCD_Clear();
// 	LCD_Cursor(0,0);
// 	LCD_Write("--CALIBRATION-- ");
// 	LCD_Cursor(1,0);
// 	LCD_Write("Connect meter.  ");
// 	_delay_ms(1000);
// 	LCD_Cursor(1,0);
// 	LCD_Write("Turn knob until ");
// 	_delay_ms(1000);
// 	LCD_Cursor(1,0);
// 	LCD_Write("meter agrees and");
// 	_delay_ms(1000);
// 	LCD_Cursor(1,0);
// 	LCD_Write("hit OK.         ");
// 	_delay_ms(1000);
// 	LCD_Cursor(1,0);
// 	LCD_Write("Voltage:        ");
// 	while(!SWITCH_Pressed(&switch1))
// 	{
// 		if(updateScreen)
// 		{
// 			LCD_Cursor(1,9);
// 			sprintf(buffer,"%i.%2i V",measuredVoltage/100,measuredVoltage%100);
// 			LCD_Write(buffer);
// 			updateScreen = 0;
// 		}
// 		
// 		unsigned char dir = SW_CheckEncoder();
// 		if(SWITCH_Pressed(&switch2) || (dir && dir != ENCODER_CCW))
// 		{
// 			measuredVoltage++;
// 			updateScreen = 1;
// 		}
// 		if(SWITCH_Pressed(&switch3) || dir == ENCODER_CCW)
// 		{
// 			measuredVoltage--;
// 			updateScreen = 1;
// 		}		
// 
// 		if(SWITCH_Pressed(&switch4))
// 		{
// 
// 			// Now we can calculate the voltageRef
// 			voltageSetMulti = ((float) measuredVoltage)/voltageCode;
// 			EEPROM_WriteNum(voltageSetMulti*100,ADDR_CALIBRATION);
// 			initCalibration();
// 			break;
// 		}
// 	}
// 	DISABLE_PREREG;
// 	DISABLE_OUTPUT;
// 	
// 
// 	DAC_transfer(DACVOLTAGE, ((float)voltageSet) / voltageSetMulti);
// 	DAC_transfer(DACCURRENT, ((float)currentSet) / currentSetMulti);
// }
