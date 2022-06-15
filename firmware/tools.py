
import matplotlib.pyplot as plt
import numpy as np

def harvest(workerId,serialPort):
        serialPort.reset_input_buffer()
        serialPort.reset_output_buffer()
        serialPort.write("harvest {}".format(workerId).encode())
        line = serialPort.read_until("packets : ".encode())
        # print(line)

        numberOfSample = int(serialPort.read_until().decode("utf-8"))
        print(numberOfSample)
        # data = serialPort.read_until("-----------------".encode())
        # print(data)
        # data1 = serialPort.read_until("-----------------".encode())
        # print(data1)
        # numberOfSample = 1600
        temps1 = np.zeros((numberOfSample-5))
        seis1 = np.zeros((numberOfSample-5))
        seis2 = np.zeros((numberOfSample-5))
        seis3 = np.zeros((numberOfSample-5))
        # data = serialPort.read_until("-----------------".encode())
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
        data_left = serialPort.read_until("-----------------".encode())# act as a clear buffer
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

        plt.plot(temps1[2:], seis2_mod[2:], label="X")
        plt.plot(temps1[2:], seis3_mod[2:], label="Y")  
        plt.plot(temps1[2:], seis1_mod[2:], label="Z")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [V]")
        plt.title("Worker {}".format(workerId))
        plt.legend()
        plt.show()     

def configAcquisition(workerId, serialPort, samplingRate, duration):
    serialPort.write("config acq{}\n".format(workerId).encode())
    serialPort.write("{}\n".format(samplingRate).encode())
    serialPort.write("{}\n".format(duration).encode())
    # data = serialPort.read_until("-----------------".encode())
    for i in range(3):
        line = serialPort.readline()
        line = line.decode("utf-8")
        print(line)
    serialPort.reset_input_buffer()
    serialPort.reset_output_buffer()
