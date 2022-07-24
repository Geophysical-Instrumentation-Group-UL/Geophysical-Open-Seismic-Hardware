![GiGUL](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/GIGul.png)

# Welcome to the Open-seismic wiki!
In this wiki page you will find details about the Open-seismic project goals, design guidelines and current stage of developement. The details about the librairy used in the projects can be found in the [command](https://github.com/armercier/Open-seismic/wiki/command-librairy) and [ad7768](https://github.com/armercier/Open-seismic/wiki/ad7768-librairy) pages.

# What

 The Open Seismic hardware initiative is to design an open source VSP tool that is modular and can be reused or adapted by other research group for their purposes. This repo is hosting the software required to operate the electronics of the VSP tools. In particular the systems in composed of :

- Analog accelerometer from Silicon Design (SI1521L)
- AD7768 multi-channel Delta-Sigma 24 bits ADC
- THVD8000 Frequency modulated RS-485
- Teensy 4.0 MC

![Scheme](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/schema_avec_communication_github%20(1).png)

There are multiple Workers (capsule) but only one master uphole.

# Design guidelines
This basic software is the first prototype of the control software. Only the essentials functions are implemented. This software looks at doing 2 things in particular:

- Ease of use and high-level function to operate the system [main.py and mainMaster]
- High-speed acquisition of seismic signal from the ADC (32 kHz) [mainSlave]

![Software](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/software.png)

# Principal elements in master scripts:

## main.py
- Read the input of the terminal
  - arm
  - harvestX
  - exit
- Transform the data from 24 bits to voltage. The values are hardcoded
- plot the results of the the harvested data (only 2 slaves for now)
The X is the value of the worker you wish to harvest


## mainMaster

- Read the serial from PC and read the command
 - If the arm command is detect the trigger interrupt is activated
 - If the trigger is detected, a signal is sended to the slaves and the trigerred state is turned off
- If the harvest data command is detected the flag waitForData is activated

The script uses the functions of the _command_ librairy to communicate with the slaves. When the master waits for a slave response the function _readCommand_ of the _command_ librairy is used to detect the incoming command type from the slave.

## mainSlave
- configures the adc with the seismic configuration
- Read the serial port of the rs-485 communication line
- Sort the command type with _readCommand_ function
- If armed is detected the interrupt for the clock and for the drdy is activated. The status ready to trig is then activated so the serial port is checked for a new command
- Once the ready to trig flag is true, the scripts only waits for a 't' on the serial port. When it sees it, it activated the triggered_state to true and the acquisition time is set to 0. This previous block of code is under a nointerrupt condition.
- When a drdy interrupt is detected the clck count is set to 0.
- the read_ISR function is called every clck count the register the data in a pre defined vector (bianary_data)
- At the 33 clck count the data_packet_ready flag is activated and the data is transformed form bit to integer
- The interrupt are then disable and the triggered status and ready to trig status are set to false.