DPS201
======

USART Serial Definitions
------

* We use automation friendly protocol, that means non human-readable.

* We use HDLC framing protocol with
  - start char: 	0x7E
  - end char:		0x7E
  - esc char:		0x7D

* This is a master/slave protocol where slave always returns an 
  answer when length and the CRC has been verified
  - ACK:			0x06
  - NAK:			0x15

* ALL packets take the form

  Packet byte(s) | Contents	
  ---------------|-----------------------
  <u8 start>     | Start character
  <u8 ID>        | Command identification
  <u8 len>       | length of data
  <u8 data[len]> | data
  <u16 CRC>      | 16 bit CRC code
  <u8 end>       | end character

  This means all packets will be of length len+4 (char)

* slave also replies ID when it responds to master. For example, master
  asks for a measured value, slave responds two packages, first <ACK> 
  then <ID><data>. If master gives a command then slave only responds
  with <ACK>.

* Max package lenth (total) is 80.

* All numercal values are sent using SI units in scientific notation.

* Command identifications are defined in the file: idCodes

