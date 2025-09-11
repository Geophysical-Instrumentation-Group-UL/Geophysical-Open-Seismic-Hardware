# Inter-board Connections

Boards are connected using rectangular connectors (see BOM list) and microfit cables.

### ADC_RS and MCU
To connect the ADC_RS and MCU (Teensy 4.0) boards, microfit cables are used. There are two ways to connect them to the MCU board.

1. Cut and expose one end of the microfit cable, and solder in the pin hole. 
2. Solder connector headers in the pin holes of the MCU, plug the microfit cables around them, and solder together.

Connections between the ADC_RS board and the MCU are as follow (ADC_RS -> MCU):
- GND -> GND
- 5V -> Vin
- 3.3MCU -> 3.3V
- RS485RX -> 15
- RS485TX -> 14
- MODE -> 9
- CS -> 10
- SCLK -> 13
- SDI -> 11
- SDO -> 12
- DRDY -> 18
- DOUT0 -> 2
- DOUT1 -> 3
- DOUT2 -> 4
- DOUT3 -> 5
- DCLK -> 6

### Power supply
The A and B lines are connected to the A and B pins of the power supply board. Connection with the ADC_RS board is the following (ADC_RS -> power supply): 12V -> +VOUT. For a simpler connection, the power supply board is grounded to the MCU, which has 3 GND pins, instead of the ADC_RS board.