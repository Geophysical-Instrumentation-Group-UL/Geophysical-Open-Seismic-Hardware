# Refraction survey

---

Here is the details about the refraction survey from the article. All the 3D files have been developed in CREO and are available in the 3D_files directory.



## Goals

- Compare our system with the well proven *Geode* from geometrics (first arrivals and complete seismograph)
- Test the custom 3 components sensor package

## Integration of the electronics

### Sensor package

The SI 1521L are soldered on the sensor board and jumper wires are soldered to the PCB. A 3D printed box with tapered insert allow to fix the PCB in an orthogonal arrangement. Every board are connected to a wall mount DB15 connector.

![sensors](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/sensor_package.jpg)

### Main board and power supply

The main board and the power supply board were integrated onto an 3D printed frame via screws. On one end of the frame is a custom expander plug mechanism and on the other end a printed TPU (flexible) ring. These allow to slide the frame inside an 2 inch aluminium tube and lock the frame so it doesn't move. A custom cable is assemble based on a DB15 cable. Wires for the sensor package that come from the main board are soldered into the pre-assemble DB15 cable and wrapped around heat-shrink.


![assembly](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/assembly_board.jpg)

### End cap

A custom end cap is designed and 3D printed. This cap has some threaded insert so it can be fix by a screw through the tube wall. These cap have a cavity for a cable gland for the DB15 cable and for the coax wall mount connector.

![gland](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/cable_gland.png)
![coax](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/cable_gland_coax.png)

### Master box

The master unit is bolted into a simple 3D printed box with a removable cover. The box has a wall mount coax connector and a slid to allow the passage of the USB cable. Banana jack are included to connect the external power supply. Wires for the trigger are accessed from a hole in the box cover.

![box](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/master_box.png)

### Custom trigger

A custom trigger system composed of a piezo-electric ([Sparkfun](https://www.sparkfun.com/products/10293)) element is mounted onto a sledgehammer. The mount is 3D printed and is divided in 3 main parts:

- 2 pieces clamp in rigid plastic (CPE)
- 2 half-circle TPU ring that provides damping and reduce stress on the CPE plastic
- 1 TPU top cap to keep the piezo in place

![trigger](https://github.com/armercier/Open-seismic-electrical-design/blob/main/media/trigger.jpg)

## Material used

- Voltage source (HMP4040 from Rhode and Schwarz)
- Generator to power the voltage source
- Laptop with the custom software for the tool
- Sledgehammer and metal plate
- Measuring tape
- Geode from geometrics and associated cables
- Laptop with proper geometrics software
- 12 V battery
- Geophones (ION 28 Hz)



## Geometry

See images in the article.

## Data

Raw data are stored in .txt files and are available on request.
