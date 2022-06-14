from socket import timeout
import numpy as np
import serial
import fnmatch
import os
import re
from tools import *


serial_port = 'COM7'
baud_rate = 115200  # In arduino, Serial.begin(baud_rate)

ser = serial.Serial(serial_port, baud_rate,timeout=2)

ON = True

while ON:
    command = input()
    if command == 'exit':
        ON = False
        break

    elif command == 'config':
        print("workerID ? ")
        workerId = input()
        print("samplingRate ? ")
        samplingRate = input()
        print("duration ? ")
        duration = input()
        configAcquisition(workerId,ser, samplingRate, duration)



    elif command == 'arm':
        ser.write("{}".format(command).encode())
        line = ser.read_until("ed".encode())
        line = line.decode("utf-8")
        print(line)
  

    elif command.startswith('harvest'):
        workerId = command[-1]
        harvest(workerId, ser)

    elif command == 'collect':
        harvest('1', ser)
        harvest('2', ser)
        harvest('3', ser)

    elif command == 'save':
        name = 'hop'
        ROOT = './'

        # I'm supposing that each item in ROOT folder that matches
        # 'somefile*.txt' is a file which we are looking for
        files = fnmatch.filter((f for f in os.listdir(ROOT)), '{}*.txt'.format(name))

        if not files:  # is empty
            num = ''
        elif len(files) == 1:
            num = '(1)'
        else:
            # files is supposed to contain 'somefile.txt'
            files.remove('{}.txt'.format(name))
            num = '(%i)' % (int(re.search(r'\(([0-9]+)\)', max(files)).group(1)) + 1)
        output_file = open('{}{}.txt'.format(name, num), 'w')
        for i, sample in enumerate(temps1):
            output_file.write("{},{},{},{} \n".format(sample, seis1_mod[i],temps2[i],seis2_mod[i]))

        output_file.close()
        print('file close')





    # print(command)

    # rep = ser.read()
    # print(rep)
