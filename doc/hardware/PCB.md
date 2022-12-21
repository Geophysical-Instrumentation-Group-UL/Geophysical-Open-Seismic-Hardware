# Printed circuit board details

----

## Main board (ADC_RS)

The components have been divided on 3 different printed circuit boards (PCB). The main board contains the ADC, the MCU and the communication module. This board has 4 layers in order to reduce its size as much as possible and to ensure a decoupling between the digital signals, the analog signals and the power 7 supply. Its dimensions of 40 by 160 mm respects the objective of a diameter less than 46 mm. 

![](https://raw.githubusercontent.com/Geophysical-Instrumentation-Group-UL/Geophysical-Open-Seismic-Hardware/remove-micro-vias/media/pcbV2.png)



### ADC drivers (pink)

Those are 2 channels amplifiers with unity gain to drive the ADC analog inputs. They are ADA4841-2 from Analog Device. The output of a sensor has 2 signals. Both signal are conditioned by an amplifier before going to the ADC. The design of this amplification stage is based on the application note https://www.analog.com/media/en/technical-documentation/application-notes/AN-1384.pdf.

### Voltage regulator (green)

4 different voltage regulator are used on this board. The 4.096 V is used as a reference for the ADC. The 3.3 power up the clock and reference the ADC. The 5Vref is the reference for the sensors and it is a high precision voltage regulator while the 5V is used to power up the ADC and other component, he can produce higher current than the 5Vref. 

### RS-485 (Yellow)

The THVD8000 is responsible of transforming the UART data to a frequency modulated RS-485 signal that is send on the A and B line. The carrier frequency is set by the R22 resistors. Values of resistor can be found in the THVD8000 [datasheet](https://www.ti.com/product/THVD8000?utm_source=google&utm_medium=cpc&utm_campaign=asc-int-null-prodfolderdynamic-cpc-pf-google-wwe&utm_content=prodfolddynamic&ds_k=DYNAMIC+SEARCH+ADS&DCM=yes&gclid=Cj0KCQjwof6WBhD4ARIsAOi65ajVA_-4Qv5Z8-NflDabHUv2FtYJd0RHMERMfylwqK505uBJHmn_EZ0aAl1MEALw_wcB&gclsrc=aw.ds). The choice of the decoupling capacitor is based on the application note here [THVD8000 design guide](https://www.ti.com/lit/an/slla496a/slla496a.pdf?ts=1658843537116&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FTHVD8000%253Futm_source%253Dgoogle%2526utm_medium%253Dcpc%2526utm_campaign%253Dasc-int-null-prodfolderdynamic-cpc-pf-google-wwe%2526utm_content%253Dprodfolddynamic%2526ds_k%253DDYNAMIC%2BSEARCH%2BADS%2526DCM%253Dyes%2526gclid%253DCj0KCQjwof6WBhD4ARIsAOi65ajVA_-4Qv5Z8-NflDabHUv2FtYJd0RHMERMfylwqK505uBJHmn_EZ0aAl1MEALw_wcB%2526gclsrc%253Daw.ds).

### Connectors 

J1 is dedicated to the communication chip. Theses wire have to be connected to the chosen MCU. J2 is a 10 pin connector dedicated to the configuration and communication with the ADC. J3 is a 7 pin high power connector used by the A,B and 12V lines. Finally, the J4 15 pin connector is used to drive and collect the signals from 4 analog differential sensors.

## Power supply

The power supply and its component are built into a separate 40 by 85 mm PCB. This way, switching noise cannot affect the precision components of the main board. The design is based on the [DC2895A](https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/dc2895a.html#eb-overview) demo board. On one side the A and B line enters and goes thru the inductor to filter out the high frequency.  Since the cable is expected to have a high capacitance (140 microF), turning on the power supply can create a  current surge. The added 100 Ohms resistor (R5) allows to reduce the current spike when turning on the power supply. The mode header is used to set the operating mode for the output of the power supply. Burst mode is the default since it draws less current.

![](https://github.com/armercier/Open-seismic-electrical-design/blob/documentation/media/power_supply.png)





## Sensors

The sensors are assembled on miniature PCBs in order to facilitate the assembly on a mount with the desired geometry.  Wires are soldered directly into the sensor boards. These wires are linked to the main board by a locking clip connector to ensure proper contact The PCB follows the connection proposed in the sensor datasheet ([si1521L](https://www.silicondesigns.com/_files/ugd/3fcdcf_d6eb801b372f408bbba8180fd1f07cc7.pdf)). 



![](https://github.com/armercier/Open-seismic-electrical-design/blob/documentation/media/sensor.png)
