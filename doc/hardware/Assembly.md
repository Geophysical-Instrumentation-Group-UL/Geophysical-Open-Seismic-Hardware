# Assembly

----

The assembly is done is 2 parts. The material needed is:

- Reflow oven or hot air gun for soldering to solder SMD parts
- Soldering iron to solder through hole parts
- Multimeter
- Osilloscope
- Precision tweezers
- Microscope (optionnal)



Firstly the SMD components must be soldered. The use of a stencil is highly recommended. The stencil can be ordered with the boards. Solder paste is then applied to all the board. Components are then placed according to their position (referred in the BOM file). At this point either a hot air gun or a appropriate oven can be use to reflow the solder paste. We use the AS-5010 oven from smtMAX with a specific reflow profile shown on the figure below.

Secondly, the through holes parts can be soldered with a classic soldering iron. Care must be taken to not overheat SMD component.

A video of the assembly of the worker board is available in the media directory. The assembly process is the same for the sensor and power supply board.

it is recommended to check every connection with a multimeter to ensure no shorts remains after the SMD soldering process. More secifically, here is a few verification that could be made to ensure proper working boards.

-  Make sure all planes have infinite impendance (5V, GND, TOP and BOTTOM)
-  Very large impedance between the differential channel of the input of the op-amp (see pink section of the PCB.pdf documentation file)
-  No shorts between the all the adjacent pins of the ad7768
-  No shorts between the A and B line

Once 12V is applied to the 12V pin, differents verification can be made with a multimeter and an oscillioscope.

- Make sure the power pins ouput the prescribed voltage (4.096V, 5V and 5V ref, 3.3V), see green section in the PCB.pdf documentation file
- With an oscilloscope, make sure the DCLK pins of the ADC outputs a clock signal at 4MHz
- Make sure the output of the external clock (U2) outputs a signal at 32.8 MHz

### smtMAX oven used



![](https://github.com/Geophysical-Instrumentation-Group-UL/Geophysical-Open-Seismic-Hardware/blob/main/media/oven.png)



### Reflow profile used

![](https://github.com/Geophysical-Instrumentation-Group-UL/Geophysical-Open-Seismic-Hardware/blob/main/media/reflow_profile.png)





### Stencil used to apply the solder paste

![](https://github.com/Geophysical-Instrumentation-Group-UL/Geophysical-Open-Seismic-Hardware/blob/main/media/stencil.png)

