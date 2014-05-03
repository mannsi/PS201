DPS201
======

USART Serial Definitions
------

1. We use automation friendly protocol, that means non human-readable.

2. We use HDLC framing protocol with

   Character  | Hex
   -----------|-----------
   start char | ```0x7E```
   end char   | ```0x7E```
   esc char   | ```0x7D```
   ACK        | ```0x06```
   NAK        | ```0x15```
   Return     | ```0x0D```
   Newline    | ```0x0A```

   All characters in above table which appear in the data stream are
   escaped by first sending ```0x7D``` followed by the original character
   with the third MSB flipped.

3. This is a master/slave protocol where slave always returns an 
   answer when length and the CRC has been verified

4. ALL packets take the form

   Packet byte(s)    | Contents	
   ------------------|-----------------------
   ```u8 start```    | Start character
   ```u8 ID```       | Command identification
   ```u8 len```      | length of data
   ```u8 data[len]```| data
   ```u16 CRC```     | 16 bit CRC code
   ```u8 end```      | end character
 
   This means all packets will be of length len+4 (char)

5. Slave also replies ID when it responds to master. For example, master
   asks for a measured value, slave responds two packages, first ```ACK``` 
   then ```ID+data```. If master gives a command then slave only responds
   with ```ACK```.

6. Max package lenth (total) is 80 bytes.

7. All numerical values are sent using SI units in scientific notation.

8. Commands will be listed below

