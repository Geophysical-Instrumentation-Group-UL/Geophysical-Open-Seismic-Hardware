
# Geophysical Open Seismic Hardware


The Geophysical Open Seismic Hardware initiative is brought to you by the Geophysical Instrumentation Group at Université Laval (GIGul) and is funded by the Fonds de Recherche du Québec- Nature et technologies (FRQNT). This open-hardware contribution provides Earth Scientists around the world with a reference design for multi-component borehole seismic array that can be deployed from a conventional wireline winch used in the mineral industry (1/8 single conductor armoured cable). This design is engineered around the Teensy 4.0 microcontroller board which is compatible with the Arduino ecosystem and will be familiar to engineers and tinkerers. Our design philosophy is to include easily sourced components as part of modules that can readily be modified for other geophysical acquisition projects.

This repository contains all the design files for the different printed circuit boards that are integrated in this modular design(PCB). The first module includes a 3 channel 24 bit ADC that can sample signals up to 32 kHz. The second module is a power supply module that is configured to condition the power used by downhole shuttle. We provide a KiCad version of these design files. In early 2022, we migrated the project from Altium to KiCad in order to meet the ethos of our project and allow more users to benefit from our developments. Here are images of the V2 prototype WorkerBoard as assembled in december 2022. 

 Details about specific aspects of the project can be found on in the doc repository. For more information and questions please contact arnaud.mercier05@gmail.com or christian.dupuis@ggl.ulaval.ca.

 The hardware development is under the TAPR Open Hardware License, while the firmware is under the GNU General Public License V3. License files are within respective directory.

Addition of November 2022 : 
A basic GUI is now available. This first version allows the user to configure and control the system with 3 shuttles. It also have a display window to anayse the individual shots as well as the stacked trace.

![image](https://raw.githubusercontent.com/Geophysical-Instrumentation-Group-UL/Geophysical-Open-Seismic-Hardware/main/media/workerboardV2.jpg)
![image](https://raw.githubusercontent.com/Geophysical-Instrumentation-Group-UL/Geophysical-Open-Seismic-Hardware/main/media/mainboardV4_assembly3D.png)
![GUI](https://user-images.githubusercontent.com/38730912/202782073-3bbe8852-5f38-4c2e-a02f-1e7fc5d664b5.jpg)
