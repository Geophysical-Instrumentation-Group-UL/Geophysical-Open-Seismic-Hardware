/***************************************************************************//**
 *   @file   command.h
 *   @brief  Header file of command Driver.
 *   @author Arnaud (arnaud.mercier.1@ulaval.ca)
********************************************************************************
*******************************************************************************/

#ifndef command_H_ 
#define command_H_

/******************************************************************************/
/***************************** Include Files **********************************/
/******************************************************************************/
#include <stdint.h>
#include <Stream.h>
// #include <ad7768.h> 
/******************************************************************************/
/********************** Macros and Constants Definitions **********************/
/******************************************************************************/
/* type */
#define GLOBAL 2
#define LOCAL 1

/* def  */
#define ARM 1
#define HARVEST 2
#define SENDTRIGGER 3
#define CALIBRATE 4
#define STATUS 5
#define CONFIG 6

/*Status */
#define IDLE 0
#define ARMED 1
#define DATAREADY 2
#define CONFIGURED 3

/*Config */
#define DEFAULT 0
#define SEISMIC 1
#define FAST 2
/******************************************************************************/
/*************************** Types Declarations *******************************/
/******************************************************************************/


typedef int commandType;
typedef int commandDef;


typedef struct {
	commandType type;
    commandDef  def;
    int        status;
    int         adcConfig;
    String        data;
    int        workerId;
    bool        empty;
} command;

/******************************************************************************/
/************************ Functions Declarations ******************************/
/******************************************************************************/

 uint16_t buildAndSendCommand(Stream  *serial_port,
                              command command);

command readCommand(Stream  *serial_port);
uint16_t arm(Stream  *serial_port);
uint16_t getWorkerStatus(Stream  *serial_port,
                      int workerID);
 uint16_t sendWorkerStatus(Stream  *serial_port,
                            int workerStatus,
                            int workerID);
uint16_t sendTrigger(Stream  *serial_port);
uint16_t sendConfigToADC(Stream  *serial_port,
                            int config,
                            String acq_duration,
                            int workerID);
uint16_t HarvestData(Stream  *serial_port,
                      int workerID);
#endif