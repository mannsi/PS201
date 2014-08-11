/************************************
*                                   *
*        DIGITAL PSU REV 4          *
*        Fridrik F Gautason         *
*        Gudbjorn Einarsson         *
*        Copyright 2014             *
*                                   *
*************************************/

#include "MAIN.h"

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
const unsigned char ADCregister[3] = {
  ADC_VOLTAGE_MON, ADC_CURRENT_MON, ADC_VIN_MON
};

int main(void)
{
  CHARGEPUMP_Initialize();
  // Start the charge pump
  CHARGEPUMP_Start();
  ADC_Initialize();
  DAC_Initialize();
  SERIAL_Initialize();

  initRegistries();
  //initCalibration();

  // Initialize PSU variables
  {
    PSUData defaultVoltage = {.analog=0, .digital=0, .multiplier=getVoltageReadMultiplier(), .offset=0, .maxAnalogValue=2000, .analogIncrements=10};
    PSUData defaultCurrent = {.analog=0, .digital=0, .multiplier=getCurrentMultiplier(), .offset=0, .maxAnalogValue=100, .analogIncrements=1};
    measured[VOLTAGE] = defaultVoltage;
    measured[VIN]     = defaultVoltage;
    setting[VOLTAGE]  = defaultVoltage;
    measured[CURRENT] = defaultCurrent;
    setting[CURRENT]  = defaultCurrent;

    setting[VOLTAGE].multiplier = getVoltageSetMultiplier();
  }

  // initialize settings and transfer to the DAC
  setting[VOLTAGE].analog = EEPROM_ReadNum(ADDR_STARTVOLTAGE);
  setting[VOLTAGE].analog = 100;// FOR TESTING ONLY
  mapToDigital(&setting[VOLTAGE]);
  DAC_transfer(DAC_ctrlCode[VOLTAGE],setting[VOLTAGE].digital);
  setting[CURRENT].analog = EEPROM_ReadNum(ADDR_STARTCURRENT);
  setting[CURRENT].analog = 100;// FOR TESTING ONLY
  mapToDigital(&setting[CURRENT]);
  DAC_transfer(DAC_ctrlCode[CURRENT],setting[CURRENT].digital);

  // FOR TESTING ONLY !!!!!!!!!!!!!!!!
  enableOutput();

  // Start the ADC
  sei();
  ADC_StartMeasuring(ADCregister[ADCmeasures]);

  /************************
  *                       *
  *      TESTING LOOP     *
  *                       *
  ************************/
  while(1)
  {
  }
  /************************
  *                       *
  *      MAIN LOOP        *
  *                       *
  *************************/

  while(0)
  {
    // loop control variables
    int newVoltageSetting = 0;
    int newCurrentSetting = 0;
    int turnOutputOn = 0;
    int turnOutputOff = 0;
    int selectVoltage = 0;
    int selectCurrent = 0;
    // Read the ADC.
    int measurementCompleted[3] = {0,0,0};
    measurementCompleted[ADCmeasures] = readFromADC(&measured[ADCmeasures]);
    // Listen to USB commands.
    serialCommand newUSBCommand = readUSB();

    // The main state machine.
    switch(state){
      case NORMAL:
	if(newUSBCommand) state = setState(USBCONTROLLED);
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
    if(newVoltageSetting) DAC_transfer(DAC_ctrlCode[VOLTAGE],setting[VOLTAGE].digital);
    if(newCurrentSetting) DAC_transfer(DAC_ctrlCode[CURRENT],setting[VOLTAGE].digital);
    if(turnOutputOn)      enableOutput();
    if(turnOutputOff)     disableOutput();

    // Restart the ADC
    if(measurementCompleted[ADCmeasures])
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
  int16_t reading;
  int16_t oldReading;

  ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
  {
    reading = ADC_reading;
    ADC_reading = -1;
  }

  if(reading != -1)
  {
    // We accumulate data to increase the effective number of bits
    A->average += (uint32_t) reading;
    A->numberOfSamples += 1;
    // When we have reached the nuber of averages we bitshift right
    // four times, which is the same as dividing by square root of
    // the number of averages.
    if(A->numberOfSamples == 256) // THIS NUMBER IS 4^4 and should stay there!
    {
      oldReading = A->digital;
      reading = (uint16_t) (A->average>>4);
      // the reading should now be a 14 bit number in stead of just
      // 10 bit number, the last couple of bits we do not really use.
      A->average = 0;
      A->numberOfSamples = 0;
      if(oldReading != reading)
      {
	A->digital = reading;
	mapToAnalog(A);
	return 1;
      }
    }
    return -1;
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
  S[3] = (char) ( ((int) '0') + (num%100)/10);
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
  if(A->analog > A->maxAnalogValue) A->analog = A->maxAnalogValue;
  mapToDigital(A);
}

void decreaseAnalog(PSUData* A)
{
  A->analog -= A->analogIncrements;
  // remember that A.analog is a unsigned int
  if(A->analog > A->maxAnalogValue) A->analog = 0;
  mapToDigital(A);
}

void averageAnalogCurrent(PSUData* A)
{
}

void logToUSB(PSUData* A,unsigned char cmd)
{
  char data[5];
  mapToString(A,data);
  sendpacket(cmd,data);
}

float getReferenceVoltage(void)
{
  // Read from EEPROM
  float referenceVoltage  = ((float) EEPROM_ReadNum(ADDR_CALIBRATION))/1000.0;
  if(referenceVoltage == 0)
  {
    referenceVoltage = 2.43;
    EEPROM_WriteNum((uint16_t)referenceVoltage*1000,ADDR_CALIBRATION);
  }
  return referenceVoltage;
}

float getCurrentMultiplier(void)
{
  return getReferenceVoltage()/0.2/11.0/16.0;
}

float getVoltageSetMultiplier(void)
{
  return 12.0*getReferenceVoltage()/10.0;
}

float getVoltageReadMultiplier(void)
{
  return 11.0*getReferenceVoltage()/10.0/16.0;
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
}

void disableOutput()
{
  outputIsOn = 0;
  DISABLE_OUTPUT;
}

static void initRegistries()
{
  // Turn off Bias
  IOSetOutput(SHUTDOWN_PORT,SHUTDOWN_PIN);
  outputIsOn = 0;
  DISABLE_OUTPUT;
}
