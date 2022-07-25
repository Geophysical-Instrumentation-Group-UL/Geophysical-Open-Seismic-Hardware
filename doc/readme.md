![GiGUL](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/GIGul.png)

# Welcome to the Open-seismic documentation!
In this directory you will find details about the Open-seismic project goals, design guidelines,assembly instruction and current stage of development. The details about the software can be found in the software.md file and in the command.md andad7768.md files.

# What

 The Open Seismic hardware initiative is to design an open source VSP tool that is modular and can be reused or adapted by other research group for their purposes. This repo is hosting the modifiable hardware files, assembly instruction and software required to operate the tools. In particular the systems in composed of :

- Analog accelerometer from Silicon Design (SI1521L)
- AD7768 multi-channel Delta-Sigma 24 bits ADC
- THVD8000 Frequency modulated RS-485
- Teensy 4.0 MC

![Scheme](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/schema_avec_communication_github%20(1).png)

There are multiple Workers (shuttles) but only one master uphole. For simplicity sake, the PCB is the same for both unit.

# Design guidelines
This basic software is the first prototype of the control software. Only the essentials functions are implemented. This software looks at doing 2 things in particular:

- Ease of use and high-level function to operate the system [main.py and mainMaster]
- High-speed acquisition of seismic signal from the ADC (32 kHz) [mainSlave]

![Software](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/software.png)
