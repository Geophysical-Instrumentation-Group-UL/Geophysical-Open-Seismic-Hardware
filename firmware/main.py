import matplotlib.pyplot as plt
import numpy as np
import serial
import fnmatch
import os
import re
import matplotlib.pyplot as pl



serial_port = 'COM7'
baud_rate = 115200  # In arduino, Serial.begin(baud_rate)

ser = serial.Serial(serial_port, baud_rate)

ON = True

while ON:
    command = input()
    if command == 'exit':
        ON = False
        break
    elif command == 'arm':
        ser.write("{}".format(command).encode())
        line = ser.readline()
        line = line.decode("utf-8")
        print(line)
        line = ser.read_until()
        print(line.decode("utf-8"))
    elif command == 'harvest1':

        ser.write("{} 1".format(command).encode())
        line = ser.read_until('packets : '.encode())
        numberOfSample = int(ser.read_until().decode("utf-8"))
        numberOfSample=1600
        temps1 = np.zeros((numberOfSample-5))
        seis1 = np.zeros((numberOfSample-5))
        seis2 = np.zeros((numberOfSample-5))
        seis3 = np.zeros((numberOfSample-5))
        for i in range(numberOfSample-5):
            line = ser.readline()
            line = line.decode("utf-8")
            temp = line.split(',')
            if line.count(',') == 3:
                # print(temp)
                temps1[i] = int(temp[0])
                seis1[i] = int(temp[1])
                seis2[i] = int(temp[2])
                seis3[i] = int(temp[3])

        temps1 = (temps1 - temps1[0]) / 1E6
        range_accel = (4.1 - 0.0021) * 2
        seis1 = (seis1 * range_accel) / (2 ** 24)
        seis1_mod = np.zeros((len(seis1)))

        seis2 = (seis2 * range_accel) / (2 ** 24)
        seis2_mod = np.zeros((len(seis2)))

        seis3 = (seis3 * range_accel) / (2 ** 24)
        seis3_mod = np.zeros((len(seis3)))

        for i, val in enumerate(seis1):
            if val > 4.096:
                seis1_mod[i] = val - range_accel
            else:
                seis1_mod[i] = val

        for i, val in enumerate(seis2):
            if val > 4.096:
                seis2_mod[i] = val - range_accel
            else:
                seis2_mod[i] = val

        for i, val in enumerate(seis3):
            if val > 4.096:
                seis3_mod[i] = val - range_accel
            else:
                seis3_mod[i] = val 

        plt.plot(temps1[2:], seis1_mod[2:], label="W1 Accel 1")
        plt.plot(temps1[2:], seis2_mod[2:], label="W1 Accel 2")
        plt.plot(temps1[2:], seis3_mod[2:], label="W1 Accel 3")  
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [V]")
        plt.legend()
        plt.show()     


    elif command == 'harvest2':
        ser.write("{} 2".format(command).encode())
        line = ser.read_until('packets : '.encode())
        numberOfSample = int(ser.read_until().decode("utf-8"))
        numberOfSample=1600
        temps2 = np.zeros((numberOfSample-5))
        seis12 = np.zeros((numberOfSample-5))
        seis22 = np.zeros((numberOfSample-5))
        seis32 = np.zeros((numberOfSample-5))
        for i in range(numberOfSample-5):
            line = ser.readline()
            line = line.decode("utf-8")
            temp = line.split(',')
            if line.count(',') == 3:
                # print(temp)
                temps2[i] = int(temp[0])
                seis12[i] = int(temp[1])
                seis22[i] = int(temp[2])
                seis32[i] = int(temp[3])

        temps2 = (temps2 - temps2[0]) / 1E6
        range_accel = (4.1 - 0.0021) * 2
        seis12 = (seis12 * range_accel) / (2 ** 24)
        seis12_mod = np.zeros((len(seis12)))

        seis22 = (seis22 * range_accel) / (2 ** 24)
        seis22_mod = np.zeros((len(seis22)))

        seis32 = (seis32 * range_accel) / (2 ** 24)
        seis32_mod = np.zeros((len(seis32)))

        for i, val in enumerate(seis12):
            if val > 4.096:
                seis12_mod[i] = val - range_accel
            else:
                seis12_mod[i] = val

        for i, val in enumerate(seis22):
            if val > 4.096:
                seis22_mod[i] = val - range_accel
            else:
                seis22_mod[i] = val

        for i, val in enumerate(seis32):
            if val > 4.096:
                seis32_mod[i] = val - range_accel
            else:
                seis32_mod[i] = val   

        plt.plot(temps2, seis12_mod, label="W2 Accel 1")
        plt.plot(temps2, seis22_mod, label="W2 Accel 2")
        plt.plot(temps2, seis32_mod, label="W2 Accel 3")

        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [V]")
        plt.legend()
        plt.show()


    elif command == 'harvest3':
        ser.write("{} 2".format(command).encode())
        line = ser.read_until('packets : '.encode())
        numberOfSample = int(ser.read_until().decode("utf-8"))
        numberOfSample=1600
        temps2 = np.zeros((numberOfSample-5))
        seis12 = np.zeros((numberOfSample-5))
        seis22 = np.zeros((numberOfSample-5))
        seis32 = np.zeros((numberOfSample-5))
        for i in range(numberOfSample-5):
            line = ser.readline()
            line = line.decode("utf-8")
            temp = line.split(',')
            if line.count(',') == 3:
                # print(temp)
                temps2[i] = int(temp[0])
                seis12[i] = int(temp[1])
                seis22[i] = int(temp[2])
                seis32[i] = int(temp[3])

        temps2 = (temps2 - temps2[0]) / 1E6
        range_accel = (4.1 - 0.0021) * 2
        seis12 = (seis12 * range_accel) / (2 ** 24)
        seis12_mod = np.zeros((len(seis12)))

        seis22 = (seis22 * range_accel) / (2 ** 24)
        seis22_mod = np.zeros((len(seis22)))

        seis32 = (seis32 * range_accel) / (2 ** 24)
        seis32_mod = np.zeros((len(seis32)))

        for i, val in enumerate(seis12):
            if val > 4.096:
                seis12_mod[i] = val - range_accel
            else:
                seis12_mod[i] = val

        for i, val in enumerate(seis22):
            if val > 4.096:
                seis22_mod[i] = val - range_accel
            else:
                seis22_mod[i] = val

        for i, val in enumerate(seis32):
            if val > 4.096:
                seis32_mod[i] = val - range_accel
            else:
                seis32_mod[i] = val   

        plt.plot(temps2, seis12_mod, label="W2 Accel 1")
        plt.plot(temps2, seis22_mod, label="W2 Accel 2")
        plt.plot(temps2, seis32_mod, label="W2 Accel 3")

        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [V]")
        plt.legend()
        plt.show()
    

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
