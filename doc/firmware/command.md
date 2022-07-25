**This homemade librairy implements hihg level functions to operate the open-seismic harware**

All functions needs a stream object, wich is the serial port you want to use to send command.

All function use a command object to transfer data:

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

This allows to have different _command_ object depending on the communication needs. 

The buildAndSendCommand function send all the parameters in the command struct object with a letters before each parameter. This makes it easy to decode the information in the readCommand function.

When the master wants to harvest the data from a slave the it send a command asking for data. The slaves writes the data directly into the serial port while the master is ready to listen.