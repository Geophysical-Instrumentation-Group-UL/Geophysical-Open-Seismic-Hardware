![GiGUL](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/GIGul.png)

# Welcome to the Geophysical Open Seismic Hardware documentation!
In this directory you will find details about the Geophysical Open Seismic Hardware project goals, design guidelines, assembly instruction and current stage of development. This repo is hosting the modifiable hardware files, assembly instruction and software required to operate the tools.

# What

 The Geophysical Open Seismic Hardware initiative is to design an open source VSP tool that is modular and can be reused or adapted by other research group for their purposes.  This contribution presents our first geophysical open-hardware contribution. We have developed a rugged and versatile 24-bit geophysical logger. The control and synchronization of the acquisition system is engineered around Arduino compatible microcontrollers that are open-source. This provides an intuitive and vibrant development community. A frequency modulated communication protocol allows us to communicate data efficiently and send power over a single conductor wireline. This modular geophysical logger can easily be reconfigured to be used with multiple sensors. The first use case of this logger is a Vertical Seismic Profiling tool chain. The novel design reduces the overall cost and size, which facilitates the deployment of more channels and in configurations that are not feasible with current commercial equipment. In particular the system in composed of :

- Analog accelerometer from Silicon Design (SI1521L)
- AD7768 multi-channel Delta-Sigma 24 bits ADC
- THVD8000 Frequency modulated RS-485
- Teensy 4.0 MC

# Overview



The system is based on a leader/worker arrangement. The leader (master) unit uphole is connected directly via USB to the PC. This leader unit is the same as the worker unit without the power supply and sensor modules. There are multiple Workers (shuttles) but only one leader uphole. DC voltage is applied on the A and B line which is used to power up the worker units. Each worker is in a pressure housing to be able to sustain borehole conditions. At the time being, the pressure housing is still in development.

![Scheme](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/schema_avec_communication_github%20(1).png)
