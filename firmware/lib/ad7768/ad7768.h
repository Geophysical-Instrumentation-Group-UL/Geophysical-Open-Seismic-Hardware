/***************************************************************************//**
 *   @file   ad7768.h
 *   @brief  Header file of AD7768 Driver.
 *   @author armercier (arnaud.mercier.1@ulaval.ca)
********************************************************************************
This librairy is adapted from the original ad7768 librairy from Analog device 
https://github.com/analogdevicesinc/no-OS/blob/master/drivers/adc/ad7768/ad7768.c

It integrates the SPI communication protocol of the arduino instead of the standard
generic SPI protocol. Base functions to configure and read the configuration of 
ADC.
*******************************************************************************/
#ifndef AD7768_H_
#define AD7768_H_

/******************************************************************************/
/***************************** Include Files **********************************/
/******************************************************************************/
#include <stdint.h>
#include <Stream.h>


/******************************************************************************/
/********************** Macros and Constants Definitions **********************/
/******************************************************************************/
#define AD7768_REG_CH_STANDBY				0x00
#define AD7768_REG_CH_MODE_A				0x01
#define AD7768_REG_CH_MODE_B				0x02
#define AD7768_REG_CH_MODE_SEL				0x03
#define AD7768_REG_PWR_MODE					0x04
#define AD7768_REG_GENERAL_CFG				0x05
#define AD7768_REG_DATA_CTRL				0x06
#define AD7768_REG_INTERFACE_CFG			0x07
#define AD7768_REG_BIST_CTRL				0x08
#define AD7768_REG_DEV_STATUS				0x09
#define AD7768_REG_REV_ID					0x0A
#define AD7768_REG_DEV_ID_MSB				0x0B
#define AD7768_REG_DEV_ID_LSB				0x0C
#define AD7768_REG_SW_REV_ID				0x0D
#define AD7768_REG_GPIO_CTRL				0x0E
#define AD7768_REG_GPIO_WR_DATA				0x0F
#define AD7768_REG_GPIO_RD_DATA				0x10
#define AD7768_REG_PRECHARGE_BUF_1			0x11
#define AD7768_REG_PRECHARGE_BUF_2			0x12
#define AD7768_REG_POS_REF_BUF				0x13
#define AD7768_REG_NEG_REF_BUF				0x14
#define AD7768_REG_CH_OFFSET_1(ch)			(0x1E + (ch) * 3)
#define AD7768_REG_CH_OFFSET_2(ch)			(0x1F + (ch) * 3)
#define AD7768_REG_CH_OFFSET_3(ch)			(0x20 + (ch) * 3)
#define AD7768_REG_CH_GAIN_1(ch)			(0x36 + (ch) * 3)
#define AD7768_REG_CH_GAIN_2(ch)			(0x37 + (ch) * 3)
#define AD7768_REG_CH_GAIN_3(ch)			(0x38 + (ch) * 3)
#define AD7768_REG_CH_SYNC_OFFSET(ch)		(0x4E + (ch) * 3)
#define AD7768_REG_DIAG_METER_RX			0x56
#define AD7768_REG_DIAG_CTRL				0x57
#define AD7768_REG_DIAG_MOD_DELAY_CTRL		0x58
#define AD7768_REG_DIAG_CHOP_CTRL			0x59

/* AD7768_REG_CH_STANDBY */
#define AD7768_CH_STANDBY(x)				(1 << (x))

/* AD7768_REG_CH_MODE_x */
#define AD7768_CH_MODE_FILTER_TYPE			(1 << 3)
#define AD7768_CH_MODE_FILTER_TYPE_DATA(x)	((x) << 3)
#define AD7768_CH_MODE_DEC_RATE(x)			(((x) & 0x7) << 0)

/* AD7768_REG_CH_MODE_SEL */
#define AD7768_CH_MODE(x)					(1 << (x))

/* AD7768_REG_PWR_MODE */
#define AD7768_PWR_MODE_SLEEP_MODE			(1 << 7)
#define AD7768_PWR_MODE_POWER_MODE(x)		(((x) & 0x3) << 4)
#define AD7768_PWR_MODE_LVDS_ENABLE			(1 << 3)
#define AD7768_PWR_MODE_MCLK_DIV(x)			(((x) & 0x3) << 0)

/* AD7768_REG_DATA_CTRL */
#define AD7768_DATA_CTRL_SPI_SYNC			(1 << 7)
#define AD7768_DATA_CTRL_SINGLE_SHOT_EN		(1 << 4)
#define AD7768_DATA_CTRL_SPI_RESET(x)		(((x) & 0x3) << 0)

/* AD7768_REG_INTERFACE_CFG */
#define AD7768_INTERFACE_CFG_CRC_SEL(x)		(((x) & 0x3) << 2)
#define AD7768_INTERFACE_CFG_DCLK_DIV(x)	(((x) & 0x3) << 0)

#define AD7768_RESOLUTION					24

/******************************************************************************/
/*************************** Types Declarations *******************************/
/******************************************************************************/
typedef int ad7768_chip_select_pin;

typedef enum {
	AD7768_ACTIVE,
	AD7768_SLEEP,
} ad7768_sleep_mode;

typedef enum {
	AD7768_ECO = 0,
	AD7768_MEDIAN = 2,
	AD7768_FAST = 3,
} ad7768_power_mode;

typedef enum {
	AD7768_MCLK_DIV_32 = 0,
	AD7768_MCLK_DIV_8 = 2,
	AD7768_MCLK_DIV_4 = 3,
} ad7768_mclk_div;

typedef enum {
	AD7768_DCLK_DIV_8,
	AD7768_DCLK_DIV_4,
	AD7768_DCLK_DIV_2,
	AD7768_DCLK_DIV_1,
} ad7768_dclk_div;

typedef enum {
	AD7768_PIN_CTRL,
	AD7768_SPI_CTRL,
} ad7768_pin_spi_ctrl;

typedef enum {
	AD7768_STANDARD_CONV,
	AD7768_ONE_SHOT_CONV,
} ad7768_conv_op;

typedef enum {
	AD7768_NO_CRC,
	AD7768_CRC_4,
	AD7768_CRC_16,
	AD7768_CRC_16_2ND,
} ad7768_crc_sel;

typedef enum {
	AD7768_CH0,
	AD7768_CH1,
	AD7768_CH2,
	AD7768_CH3,
	AD7768_CH4,
	AD7768_CH5,
	AD7768_CH6,
	AD7768_CH7,
	AD7768_CH_NO
} ad7768_ch;

typedef enum {
	AD7768_ENABLED,
	AD7768_STANDBY,
} ad7768_ch_state;

typedef enum {
	AD7768_MODE_A,
	AD7768_MODE_B,
} ad7768_ch_mode;

typedef enum {
	AD7768_FILTER_WIDEBAND,
	AD7768_FILTER_SINC,
} ad7768_filt_type;

typedef enum {
	AD7768_DEC_X32,
	AD7768_DEC_X64,
	AD7768_DEC_X128,
	AD7768_DEC_X256,
	AD7768_DEC_X512,
	AD7768_DEC_X1024,
	AD7768_DEC_X1024_2ND,
	AD7768_DEC_X1024_3RD,
} ad7768_dec_rate;

// typedef struct {
// 	// spi_desc			*spi_desc;
// 	struct gpio_desc	*gpio_reset;
// 	uint8_t			gpio_reset_value;
// 	struct gpio_desc	*gpio_mode0;
// 	struct gpio_desc	*gpio_mode1;
// 	struct gpio_desc	*gpio_mode2;
// 	struct gpio_desc	*gpio_mode3;
// 	uint8_t			pin_spi_input_value;
// 	ad7768_pin_spi_ctrl	pin_spi_ctrl;
// 	ad7768_sleep_mode	sleep_mode;
// 	ad7768_power_mode	power_mode;
// 	ad7768_mclk_div		mclk_div;
// 	ad7768_dclk_div		dclk_div;
// 	ad7768_conv_op		conv_op;
// 	ad7768_crc_sel		crc_sel;
// 	ad7768_ch_state		ch_state[8];
// 	ad7768_ch_mode		ch_mode[8];
// 	ad7768_filt_type	filt_type[2];
// 	ad7768_dec_rate		dec_rate[2];
// } ad7768_dev;

typedef struct {
	ad7768_chip_select_pin chipSelectPin = 10; //teensy 4.0 CS pin
	ad7768_power_mode	power_mode;
	ad7768_mclk_div		mclk_div;
	ad7768_dclk_div		dclk_div;
	ad7768_dec_rate		dec_rate;
	ad7768_filt_type	filt_type;
	// ceux-ci reste à faire
	ad7768_ch_mode		ch_mode[8];
	ad7768_conv_op		conv_op;
	ad7768_crc_sel		crc_sel;
	ad7768_ch_state		ch_state[8];	
	ad7768_sleep_mode	sleep_mode;
	// les paramètres non utilisé doivent etre apres ceux utilisé dans la
	// script main.
} ad7768_chip;


/******************************************************************************/
/************************ Functions Declarations ******************************/
/******************************************************************************/
/* SPI read from device. */
uint16_t spi_sync(ad7768_chip chip);
uint16_t read_spi(ad7768_chip chip,
 					uint8_t reg_addr);
uint8_t print_config(ad7768_chip chip, Stream  *serial_port);

uint8_t read_spi_mask(ad7768_chip chip,
 					uint8_t reg_addr,
					uint8_t mask);
/* SPI write to device. */
uint16_t write_spi(ad7768_chip chip,
 					uint8_t reg_addr,
					uint8_t data);
uint16_t write_spi_mask(ad7768_chip chip,
 					uint8_t reg_addr,
					uint8_t mask,
					uint8_t data);
int32_t ad7768_setup(ad7768_chip chip);
int32_t set_power_mode(ad7768_chip chip);
int32_t set_mclk_div(ad7768_chip chip);
int32_t set_decimation_rate(ad7768_chip chip);
int32_t set_filter_type(ad7768_chip chip);
int32_t set_dclk_div(ad7768_chip chip);

#endif // AD7768_H_