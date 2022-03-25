/***************************************************************************//**
 *   @file   
 *   @brief  Command library
 *   @author Arnaud (arnaud.mercier.1@ulaval.ca)
 ********************************************************************************

This library contains basic commands of the open-seismic system. All funciton are
homemade and using arduino standard librairy
*******************************************************************************/
/******************************************************************************/
/***************************** Include Files **********************************/
/******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include "command.h"
#include <string>


/**	
 * build and send the command on serial
 * @param serial_port - Serial port to send the data
 * @param command - the command struct to send.

 */
 uint16_t buildAndSendCommand(Stream  *serial_port,
                            command command)
{
    //TODO: Find a way to print every element in the struct
serial_port->print("i");
serial_port->print(command.workerId);
serial_port->print("w");
serial_port->print(command.type); 
serial_port->print("t");
serial_port->print(command.def);
serial_port->print("d");
serial_port->print(command.status);
serial_port->print("s");
serial_port->print(command.adcConfig);
serial_port->print("a");
serial_port->print(command.data);
serial_port->print("f");
serial_port->flush();

return 0;

}
/**	
 * Read the command from serial 
 * @param serial_port - Serial port to send the data
 * @param command - The command struct
 */
 command readCommand(Stream  *serial_port)
{    
    command commandRead;
    // int out = 0;
    // out = serial_port->read();

if (serial_port->find("i"))
{
    //TODO: find a way to read eveything then find out which element is what. No more specific order
    String re_w;
    String re_t;
    String re_d;
    String re_s;
    String re_a;
    String re_f;
    
    re_w = serial_port->readStringUntil('w');
    commandRead.workerId = re_w.toInt();

    re_t = serial_port->readStringUntil('t');
    commandRead.type = re_t.toInt();

    re_d = serial_port->readStringUntil('d');
    commandRead.def = re_d.toInt();

    re_s = serial_port->readStringUntil('s');
    commandRead.status = re_s.toInt();

    re_a = serial_port->readStringUntil('a');
    commandRead.adcConfig = re_a.toInt();

    re_f = serial_port->readStringUntil('f');
    commandRead.data = re_f;
}	
return commandRead;
}				 					 

/**	
 * arm command
 * @param serial_port - Serial port to send the data
 */
 uint16_t arm(Stream  *serial_port)
 {
     command armCommand = {
         .type = GLOBAL,
         .def = ARM,
     };


     buildAndSendCommand(serial_port, armCommand);
    return 0;
 }

 /**	
 * harvest command. Get all the data from workers
 * @param serial_port - Serial port to send the data
 */
 uint16_t HarvestData(Stream  *serial_port,
                      int workerID)
 {
     command harvestCommand = {
         .type = LOCAL,
         .def = HARVEST,
         .status = 0,
         .adcConfig = 0,
         .data = "",
         .workerId = workerID,
     };

     buildAndSendCommand(serial_port, harvestCommand);
     return 0;
 }

   /**	
 * get the status of all the workers
 * @param serial_port - Serial port to send the data
 * @param workerID - the adress of the worker
 */
 uint16_t getWorkerStatus(Stream  *serial_port,
                      int workerID)
 {
         command statusCommand = {
         .type = LOCAL,
         .def = STATUS,
         .status = 0,
         .adcConfig = 0,
         .data = "",
         .workerId = workerID,
     };
    buildAndSendCommand(serial_port,statusCommand);
    return 0;
 }
   /**	
 * send the status from a worker
 * @param serial_port - Serial port to send the data
 * @param workerStatus - the status of the worker
 * @param workerID - the ID of the worker
 */
 uint16_t sendWorkerStatus(Stream  *serial_port,
                            int workerStatus,
                            int workerID)
 {
     command statusCommand = {
         .type = LOCAL,
         .def = STATUS,
         .status = workerStatus,
         .adcConfig = 0,
         .data = "",
         .workerId = workerID,         
     };
     buildAndSendCommand(serial_port,statusCommand);
     return 0;
 }

    /**	
 * send trigger notif to slave
 * @param serial_port - Serial port to send the data
 */
 uint16_t sendTrigger(Stream  *serial_port)
 {
    serial_port->print('t');
    serial_port->flush();
    return 0;
 }

    /**	
 * send adc config to workers
 * @param serial_port - Serial port to send the data
 * @param config - the config type
 * @param workerID - the ID of the worker
 */
 uint16_t sendConfigToADC(Stream  *serial_port,
                            int config,
                            String acq_duration,
                            int workerID)
 {  
    //  String duration = String(acq_duration);
     
     command configCommand = {
         .type = LOCAL,
         .def = CONFIG,
         .status = IDLE,
         .adcConfig = config,
         .data = acq_duration,
         .workerId = workerID,
         
     };
     buildAndSendCommand(serial_port,configCommand);
     return 0;
 }