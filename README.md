PS201 - An adjustable power supply
======

What is it?
------
The PS201 is an adjustable power supply hardware project. See the 'Hardware details' section for details. The repository is split into Firmware and Software. Firmware stores code (C) running on the 
hardware while Software stores a Python 3 module called PsController that allows to control the hardware via USB cable.
The PsController software runs both and Windows and Linux (and should run on Mac but is untested) and requires Python 3.3+

Up and running
------
Until the hardware is released there is not much you can do to get started. Without the hardware the software is vapourware.  

Release date
------
Currently there is no decided release date

Software installation and execution
------
The easiest way to install is to run `sudo python3 Software/setup.py`. Note that this will try to download and install python dependencies so a network connection is probably needed (see the setup.py file for dependencies).
After install you can run the software with `sudo PsController`

Hardware details
------
The hardware unit is named DPS201. DPS201 is a 20 Volt, 1 Ampere adjustable lab power supply, the voltage can be adjusted in 100mV steps from 0 to 20V and the current limit can likewise be adjusted in 10mA steps from 0 to 1A. 
The precision has not yet been fully characterized but is close to 1% for Voltage and current over the full range. 
The power supply has independent LCD readout that normally displays the measured voltage and current and a digital encoder which the user can use to adjust the output voltage and current limit.

License
------
All code is fully open source licensed under GNU GPL v3. Feel free to copy and modify our software, any feedback is welcome.
