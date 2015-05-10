DPS201
======

USART Serial Definitions
------

1. All communication is through ASCII bytes

1. All packets to and from device take the following form
   SCCCLLDATA*HHHHS
  * S: Start/end byte ('~')
  * CCC: Command
  * LL: Length of data part. LL is represented in hex
  * DATA: Data that is being sent. Note that LL determines the length of DATA
  * HHHH: 16 bit CRC code in hex
  * S: Start/end byte ('~')
1. This is a master/slave protocol where slave always returns an 
   answer when length and the CRC has been verified

1. Slave also replies ID when it responds to master. For example, master
   asks for a measured value, slave responds two packages, first ```ACK``` 
   then ```DATA```. If master gives a command then slave only responds
   with ```ACK```.

1. Max package lenth (total) is 80 bytes.

1. Voltage values are represented in mV and current values are represented in mA

1. The following shows supported commands with examples

  * To device
    * Handshake : ~HAN003E07~
    * Write all : ~WRT005B7D~
    * Current   : ~CUR03500F009~ (Current = 500mA)
    * Voltage   : ~VOL041000F060~ (Voltage = 1000mV)
    * Output on : ~OUT011F3CF~
    * Output off: ~OUT010E3EE~
  * From device
    * Acknowledge     : ~ACK0090E3~
    * Not acknowledge : ~NAK001872~
    * Write all values: ~ALL0E0;0;1000;500;0174B~ 
      * ALL: Command. 
      * 0: Output voltage
      * 0: Output current
      * 1000: Target voltage (mV)
      * 500: Target current (mA)
      * 0: Output on (here it is off)

