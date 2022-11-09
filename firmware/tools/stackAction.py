import numpy as np
import matplotlib.pyplot as plt
import fnmatch
import os
import math as m
import pandas as pd

class Stack:
       
    def __init__(self,serialPort,samplingRate,duration,stackName):
        
        self.serialPort = serialPort
        self.stackName = stackName
        self.samplingRate = samplingRate
        self.duration = duration

    def harvest(self,workerID,show=False):
            self.serialPort.reset_input_buffer()
            self.serialPort.reset_output_buffer()
            self.serialPort.write("harvest {}".format(workerID).encode())
            line = self.serialPort.read_until("packets : ".encode())

            numberOfSample = int(self.serialPort.read_until().decode("utf-8"))
            # print(numberOfSample)

            temps1 = np.zeros((numberOfSample-5))
            seis1 = np.zeros((numberOfSample-5))
            seis2 = np.zeros((numberOfSample-5))
            seis3 = np.zeros((numberOfSample-5))

            for i in range(numberOfSample-5):
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
            line = line.decode("utf-8")
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
        print('files saved')

    def showStack(self):
        numberOfSample = int(self.samplingRate * self.duration) #TODO test this line
        sensor1 = pd.DataFrame(np.zeros((numberOfSample,4)), columns=["time", "X", "Y", "Z"])
        sensor2 = pd.DataFrame(np.zeros((numberOfSample,4)), columns=["time", "X", "Y", "Z"])
        sensor3 = pd.DataFrame(np.zeros((numberOfSample,4)), columns=["time", "X", "Y", "Z"])
        counter = 0
        files = fnmatch.filter((f for f in os.listdir('./data')), '{}*.txt'.format(self.stackName))

        for file in files:
            if file[-5] == '1':
                temp = pd.read_csv('data/' + file,delimiter=',', header=None)
                temp.columns = ["time", "X", "Y", "Z"]
                sensor1 = sensor1 + temp
                counter += 1
            elif file[-5] == '2':
                temp = pd.read_csv('data/' +file,delimiter=',', header=None)
                temp.columns = ["time", "X", "Y", "Z"]
                sensor2 = sensor2 + temp
                counter += 1
            elif file[-5] == '3':
                temp = pd.read_csv('data/' +file, delimiter=',',header=None)
                temp.columns = ["time", "X", "Y", "Z"]
                sensor3 = sensor3 + temp
                counter += 1
        counter = counter / 3
        sensor1 = sensor1 / counter
        sensor2 = sensor2 / counter
        sensor3 = sensor3 / counter
        list_out = [sensor1, sensor2, sensor3]
        fig, ax = plt.subplots(3, 1)
        for i in range(3):
            ax[i].plot(list_out[i]['time'], list_out[i]['X'], label="X")
            ax[i].plot(list_out[i]['time'], list_out[i]['Y'], label="Y")
            ax[i].plot(list_out[i]['time'], list_out[i]['Z'], label="Z")
            ax[i].set_title("Worker {}".format(i+1))
        ax[1].legend()
        ax[2].set_xlabel('time [s]')
        ax[1].set_ylabel("Amplitude [V]")
        fig.suptitle("Stack {}".format(self.stackName))
        plt.tight_layout()
        plt.show()

