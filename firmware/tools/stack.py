import numpy as np
import matplotlib.pyplot as plt
import fnmatch
import os
import math as m
import pandas as pd

class Stack:
       
    def __init__(self,serialPort,samplingRate,duration,stackName,numberOfShuttle):
        
        self.serialPort = serialPort
        self.stackName = stackName
        self.numberOfShuttle = numberOfShuttle
        self.samplingRate = samplingRate
        self.duration = duration
        self.numberOfSample = int(self.samplingRate) * int(self.duration)

    def harvest(self,workerID,show=False):
            self.serialPort.reset_input_buffer()
            self.serialPort.reset_output_buffer()
            self.serialPort.write("harvest {}".format(workerID).encode())
            line = self.serialPort.read_until("packets : ".encode())

            self.numberOfSample = int(self.serialPort.read_until().decode("utf-8"))
            print(self.numberOfSample)

            temps1 = np.zeros((self.numberOfSample-5))
            seis1 = np.zeros((self.numberOfSample-5))
            seis2 = np.zeros((self.numberOfSample-5))
            seis3 = np.zeros((self.numberOfSample-5))

            for i in range(self.numberOfSample-5):
                line = self.serialPort.readline()
                line = line.decode("utf-8")
                temp = line.split(',')
                if line.count(',') == 3:
                    temps1[i] = int(temp[0])
                    seis1[i] = int(temp[1])
                    seis2[i] = int(temp[2])
                    seis3[i] = int(temp[3])
            data_left = self.serialPort.read_until("-----------------".encode())# act as a clear buffer
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
            if show:
                plt.plot(temps1[2:], seis2_mod[2:], label="X")
                plt.plot(temps1[2:], seis3_mod[2:], label="Y")  
                plt.plot(temps1[2:], seis1_mod[2:], label="Z")
                plt.xlabel("Time [s]")
                plt.ylabel("Amplitude [V]")
                plt.title("Worker {}".format(workerID))
                plt.legend()
                plt.show()
            output = np.vstack((temps1[2:], seis2_mod[2:], seis3_mod[2:], seis1_mod[2:]))
            return output   

    def configWorker(self,workerID):
        self.serialPort.write("config acq{}\n".format(workerID).encode())
        self.serialPort.write("{}\n".format(self.samplingRate).encode())
        self.serialPort.write("{}\n".format(self.duration).encode())
        message = []
        for i in range(2):
            line = self.serialPort.readline()
            line = line.decode('utf-8')
            print(line)
            message.append(line)
        self.serialPort.reset_input_buffer()
        self.serialPort.reset_output_buffer()
        return message

    def save2file(self,data,shotNumber):
        
        # ROOT = './'

        # I'm supposing that each item in ROOT folder that matches
        # 'somefile*.txt' is a file which we are looking for
        # files = fnmatch.filter((f for f in os.listdir(ROOT)), '{}*.txt'.format(stackName))

        # if not files:  # is empty
        #     num = ''
        # elif len(files) == 1:
        #     num = '(1)'
        # else:
        #     # files is supposed to contain 'somefile.txt'
        #     files.remove('{}.txt'.format(stackName))
        #     num = '(%i)' % (int(re.search(r'\(([0-9]+)\)', max(files)).group(1)) + 1)
        
        for i in range(len(data)):
            output_file = open('data\{}_{}_{}.txt'.format(self.stackName, shotNumber,i+1), 'w')
            for j, sample in enumerate(data[i].T):
                output_file.write("{},{},{},{} \n".format(sample[0], sample[1],sample[2],sample[3]))

            output_file.close()
        
    def loadStack(self):
        list_out = []
        for i in range(self.numberOfShuttle):
            list_out.append(pd.DataFrame(np.zeros((self.numberOfSample,4)), columns=["time", "X", "Y", "Z"]))

        counter = 0
        files = fnmatch.filter((f for f in os.listdir('./data')), '{}*.txt'.format(self.stackName))

        for file in files:
            shuttleID = int(file[-5])
            temp = pd.read_csv('data/' + file,delimiter=',', header=None)
            temp.columns = ["time", "X", "Y", "Z"]
            list_out[shuttleID-1] = list_out[shuttleID-1] + temp
            counter += 1
        
        counter = counter / self.numberOfShuttle
        for i in range(self.numberOfShuttle):
            list_out[i] = list_out[i]/counter
            list_out[i] = list_out[i].to_numpy().T

        return list_out


