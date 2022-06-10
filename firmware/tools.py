
import matplotlib.pyplot as plt
import numpy as np

def harvest(workerId,serialPort):
        serialPort.write("harvest {}".format(workerId).encode())
        line = serialPort.read_until('packets : '.encode())
        numberOfSample = int(serialPort.read_until().decode("utf-8"))
        numberOfSample=1600
        temps1 = np.zeros((numberOfSample-5))
        seis1 = np.zeros((numberOfSample-5))
        seis2 = np.zeros((numberOfSample-5))
        seis3 = np.zeros((numberOfSample-5))
        for i in range(numberOfSample-5):
            line = serialPort.readline()
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
        plt.title("Worker {}".format(workerId))
        plt.legend()
        plt.show()     
