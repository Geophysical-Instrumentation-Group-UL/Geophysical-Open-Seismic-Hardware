/***************************************************************************//**
 *   @file ad7768.cpp
 *   @brief  Implementation of AD7768 Driver.
 *   @author armercier (arnaud.mercier.1@ulaval.ca)
********************************************************************************
This librairy is adapted from the original ad7768 librairy from Analog device 
https://github.com/analogdevicesinc/no-OS/blob/master/drivers/adc/ad7768/ad7768.c

It integrates the SPI communication protocol of the arduino instead of the standard
generic SPI protocol. Base functions to configure and read the configuration of 
ADC.
*******************************************************************************/
/******************************************************************************/
/***************************** Include Files **********************************/
/******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include "ad7768.h"
#include <SPI.h>

/**	
 * SPI read from adc homemade function.
 * @param chip - The chip parameter struct
 * @param reg_addr - register to read.
 */
 uint16_t read_spi(ad7768_chip chip,
 					uint8_t reg_addr)
{

u_int16_t buf = (reg_addr & 0x7F) | 0x80;
buf = buf << 8  ;
u_int16_t buf_received;

delay(5);
digitalWrite(chip.chipSelectPin, LOW);

SPI.transfer16(buf);

digitalWrite(chip.chipSelectPin, HIGH);
delay(5);
digitalWrite(chip.chipSelectPin, LOW);

buf_received = SPI.transfer16(0x00);
digitalWrite(chip.chipSelectPin, HIGH);

delay(5);

return buf_received;

}					 

/**
 * SPI read from adc with mask homemade function.
 * @param chip - The chip parameter struct
 * @param reg_addr - register to read.
 * @param mask - 0 everywhere except where you want to read
 */
 uint8_t read_spi_mask(ad7768_chip chip,
 					uint8_t reg_addr,
					uint8_t mask)
{

u_int16_t buf = (reg_addr & 0x7F) | 0x80;
buf = buf << 8  ;
u_int16_t buf_received;
uint8_t buf_received8;

delay(5);
digitalWrite(chip.chipSelectPin, LOW);

SPI.transfer16(buf);

digitalWrite(chip.chipSelectPin, HIGH);
delay(5);
digitalWrite(chip.chipSelectPin, LOW);

buf_received = SPI.transfer16(0x00);
digitalWrite(chip.chipSelectPin, HIGH);
buf_received8 = (lowByte(buf_received) & mask);

delay(5);

return buf_received8;

}					 


/**
 * SPI_SYNC command to adc function.
 * @param chip - The chip parameter struct
 */
 uint16_t spi_sync(ad7768_chip chip)
{
	// write low to SPI_sync command
u_int16_t sync_low = (0x06 & 0x3F) ;
sync_low = sync_low << 8  ;
sync_low = sync_low | 0x00;

digitalWrite(chip.chipSelectPin, LOW);
SPI.transfer16(sync_low);
digitalWrite(chip.chipSelectPin, HIGH);

delay(5);
// write high to SPI_sync command
u_int16_t sync_high = (0x06 & 0x3F) ;
sync_high = sync_high << 8  ;
u_int8_t add = 0x01;
add = add << 7;
sync_high = sync_high | add;


digitalWrite(chip.chipSelectPin, LOW);
SPI.transfer16(sync_high);
digitalWrite(chip.chipSelectPin, HIGH);
}
/**
 * SPI write to adc homemade function.
 * @param chip - The chip parameter struct
 * @param reg_addr - register to write.
 * @param data - data to write to register.
 */
 uint16_t write_spi(ad7768_chip chip,
 					uint8_t reg_addr,
					uint8_t data)
{
	
u_int16_t buf = (reg_addr & 0x3F) ;
buf = buf << 8  ;
buf = buf | data;

delay(5);
digitalWrite(chip.chipSelectPin, LOW);

SPI.transfer16(buf);

digitalWrite(chip.chipSelectPin, HIGH);

spi_sync(chip);
delay(5);

return buf;

}					 

/**
 * SPI write to adc with mask homemade function.
 * @param chip - The chip parameter struct
 * @param reg_addr - register to write.
 * @param mask - mask to apply to data. 0 everywhere except where you want to write
 * @param data - data to write to register.
 */
 uint16_t write_spi_mask(ad7768_chip chip,
 					uint8_t reg_addr,
					uint8_t mask,
					uint8_t data)
{
uint8_t buf_actual;	
u_int16_t buf = (reg_addr & 0x3F) ;
buf = buf << 8  ;
buf_actual = read_spi(chip,reg_addr); // read the actual data
buf_actual &= ~mask; // apply the inverse filter to keep all the other values of
buf_actual |= data; // add the data
buf = buf | buf_actual; // make it a 16 bit long
delay(5);
digitalWrite(chip.chipSelectPin, LOW);

SPI.transfer16(buf);

digitalWrite(chip.chipSelectPin, HIGH);

spi_sync(chip);
delay(5);

return buf;

}					 


/**
 * Print ADC configuration
 */
uint8_t print_config(ad7768_chip chip, Stream  *serial_port)
{
	uint16_t temp16;
	uint8_t temp8;
	uint8_t temp8power;
	uint8_t temp8filter;
	uint8_t temp8deci;
	uint8_t temp8dclk;
	float decimation_rate;
	float ODR;
	float mclk_divider;


	temp8 = read_spi_mask(chip, AD7768_REG_PWR_MODE,AD7768_PWR_MODE_MCLK_DIV(0x03));
	temp8power = read_spi_mask(chip, AD7768_REG_PWR_MODE,AD7768_PWR_MODE_POWER_MODE(0x3));
	temp8filter = read_spi_mask(chip, AD7768_REG_CH_MODE_A, AD7768_CH_MODE_FILTER_TYPE);
	temp16 = read_spi_mask(chip, AD7768_REG_CH_MODE_A, AD7768_CH_MODE_DEC_RATE(0x07));
	temp8deci = lowByte(temp16) & AD7768_CH_MODE_DEC_RATE(0x07)	; // application of a mask
	temp8dclk = read_spi_mask(chip,AD7768_REG_INTERFACE_CFG,AD7768_INTERFACE_CFG_DCLK_DIV(0x07));

	if (temp8 == 0x00)
	{
		serial_port->print("MCLK DIVIDER : "),serial_port->println(32);
		mclk_divider = 32;
		delay(1);
	}
	else if (temp8 == 0x02)
	{
		serial_port->print("MCLK DIVIDER : "),serial_port->println(8);
		mclk_divider = 8;
		delay(1);
	}
	else if (temp8 == 0x03)
	{
		serial_port->print("MCLK DIVIDER : "),serial_port->println(4);
		mclk_divider = 4;
		delay(1);
	}
	
	
	if (temp8power == 0x00)
	{
		serial_port->print("POWER MODE : "),serial_port->println("Low");
		delay(1);
	}
	else if (temp8power == 0x20)
	{
		serial_port->print("POWER MODE : "),serial_port->println("Median");
		delay(1);
	}
	else if (temp8power == 0x30)
	{
		serial_port->print("POWER MODE : "),serial_port->println("Fast");
		delay(1);
	}


	
	if (temp8filter == 0x00)
	{
		serial_port->print("FILTER TYPE : "),serial_port->println("Wideband");
		delay(1);
	}
	if (temp8filter == 0x08)
	{
		serial_port->print("FILTER TYPE : "),serial_port->println("Sinc5");
		delay(1);
	}



	if (temp8deci == 0x00)
	{
		serial_port->print("DECIMATION RATE : "),serial_port->println(32);
		decimation_rate = 32;
		delay(1);
	}
	else if (temp8deci == 0x01)
	{
		serial_port->print("DECIMATION RATE : "),serial_port->println(64);
		decimation_rate = 64;
		delay(1);
	}
	else if (temp8deci == 0x02)
	{
		serial_port->print("DECIMATION RATE : "),serial_port->println(128);
		decimation_rate = 128;
		delay(1);
	}
	else if (temp8deci == 0x03)
	{
		serial_port->print("DECIMATION RATE : "),serial_port->println(256);
		decimation_rate = 256;
		delay(1);
	}
	else if (temp8deci == 0x04)
	{
		serial_port->print("DECIMATION RATE : "),serial_port->println(512);
		decimation_rate = 512;
		delay(1);
	}
	else if (temp8deci == 0x05 or temp8deci == 0x06 or temp8deci == 0x07)
	{
		serial_port->print("DECIMATION RATE : "),serial_port->println(1024);
		decimation_rate = 1024;
		delay(1);
	}

	
	
	
	if (temp8dclk == 0x00)
	{
		serial_port->print("DCLK DIVIDER : "),serial_port->println(8);
		delay(1);
	}
	else if (temp8dclk == 0x01)
	{
		serial_port->print("DCLK DIVIDER : "),serial_port->println(4);
		delay(1);
	}
	else if (temp8dclk == 0x02)
	{
		serial_port->print("DCLK DIVIDER : "),serial_port->println(2);
		delay(1);
	}
	else if (temp8dclk == 0x03)
	{
		serial_port->print("DCLK DIVIDER : "),serial_port->println(1);
		delay(1);
	}



ODR = (32.76 / mclk_divider) * (1/decimation_rate) *1000;
delay(1);

serial_port->print("ODR [kHz] : "),serial_port->println(ODR,4);
delay(1);
serial_port->println('d');



	
	return round(ODR);

}



/**
 * Set the power mode
 * @param chip - The chip parameter struct
 * @param mode - The mode : low/median/fast
*/
int32_t set_power_mode(ad7768_chip chip)
{
	write_spi_mask(chip,
					AD7768_REG_PWR_MODE,
					AD7768_PWR_MODE_POWER_MODE(0x3),
					AD7768_PWR_MODE_POWER_MODE(chip.power_mode));
	return 0;
}

/**
 * Set the mclk divider mode
 * @param chip - The chip parameter struct
 * @param div - divider
*/
int32_t set_mclk_div(ad7768_chip chip)
{
	write_spi_mask(chip,
					AD7768_REG_PWR_MODE,
					AD7768_PWR_MODE_MCLK_DIV(0x03),
					AD7768_PWR_MODE_MCLK_DIV(chip.mclk_div));
	return 0;
}

/**
 * Set the dclk divider mode
 * @param chip - The chip parameter struct
 * @param div - divider
*/
int32_t set_dclk_div(ad7768_chip chip)
{
	write_spi_mask(chip,
					AD7768_REG_INTERFACE_CFG,
					AD7768_INTERFACE_CFG_DCLK_DIV(0x03),
					AD7768_INTERFACE_CFG_DCLK_DIV(chip.dclk_div));
	return 0;
}

/**
 * Set the decimation rate
 * @param chip - The chip parameter struct
 * @param deci - decimation rate
*/
int32_t set_decimation_rate(ad7768_chip chip)
{
	write_spi_mask(chip,
					AD7768_REG_CH_MODE_A,
					AD7768_CH_MODE_DEC_RATE(0x07),
					AD7768_CH_MODE_DEC_RATE(chip.dec_rate));
	return 0;
}

/**
 * Set the channel mode only for channel type A
 * @param chip - The chip parameter struct
 * @param channel - channel
 * @param mode - mode A or B
*/
int32_t set_filter_type(ad7768_chip chip)
{
	write_spi_mask(chip,
					AD7768_REG_CH_MODE_A,
					AD7768_CH_MODE_FILTER_TYPE,
					AD7768_CH_MODE_FILTER_TYPE_DATA(chip.filt_type));
	return 0;
}


/**
 * Configure the ad7768 based on the parameters in the ad7768_chip struct
 * @param chip - The struct defining the chip
 * @return print the parameters of the ADC
 */
int32_t ad7768_setup(ad7768_chip chip)
{
	set_power_mode(chip);
	set_mclk_div(chip);
	set_decimation_rate(chip);
	set_filter_type(chip);
	set_dclk_div(chip);
return 0;
}

