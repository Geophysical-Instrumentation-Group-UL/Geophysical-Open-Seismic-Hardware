
import numpy as np
import matplotlib.pyplot as plt
import fnmatch
import os
import re
from pycrewes.seismic import fftrl, ifftrl
import math as m



def harvest(workerId,serialPort,show=False):
        serialPort.reset_input_buffer()
        serialPort.reset_output_buffer()
        serialPort.write("harvest {}".format(workerId).encode())
        line = serialPort.read_until("packets : ".encode())

        numberOfSample = int(serialPort.read_until().decode("utf-8"))
        # print(numberOfSample)

        temps1 = np.zeros((numberOfSample-5))
        seis1 = np.zeros((numberOfSample-5))
        seis2 = np.zeros((numberOfSample-5))
        seis3 = np.zeros((numberOfSample-5))

        for i in range(numberOfSample-5):
            line = serialPort.readline()
            line = line.decode("utf-8")
            temp = line.split(',')
            if line.count(',') == 3:
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
        if show:
            plt.plot(temps1[2:], seis2_mod[2:], label="X")
            plt.plot(temps1[2:], seis3_mod[2:], label="Y")  
            plt.plot(temps1[2:], seis1_mod[2:], label="Z")
            plt.xlabel("Time [s]")
            plt.ylabel("Amplitude [V]")
            plt.title("Worker {}".format(workerId))
            plt.legend()
            plt.show()
        output = np.vstack((temps1[2:], seis2_mod[2:], seis3_mod[2:], seis1_mod[2:]))
        return output   

def configAcquisition(workerId, serialPort, samplingRate, duration):
    serialPort.write("config acq{}\n".format(workerId).encode())
    serialPort.write("{}\n".format(samplingRate).encode())
    serialPort.write("{}\n".format(duration).encode())
    for i in range(3):
        line = serialPort.readline()
        line = line.decode("utf-8")
        print(line)
    serialPort.reset_input_buffer()
    serialPort.reset_output_buffer()

def save2file(data,stackName,shotNumber):
    
    ROOT = './'

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
        output_file = open('{}_{}_{}.txt'.format(stackName, shotNumber,i+1), 'w')
        for j, sample in enumerate(data[i].T):
            output_file.write("{},{},{},{} \n".format(sample[0], sample[1],sample[2],sample[3]))

        output_file.close()
    print('files closed')



def acorf(x, n=None):
    ''' calcule l'autocorrelation du vecteur x pour n éléments
    Nous utilisons la fonction convolve pour effectuer le calcul
    '''
    if n == None:
        n = x.size

    # if x.size <= n:
    #     print(u'ERREUR : Le nombre d\'éléments %i dans le vecteur est inférieur au nombre de lag à calculer %i' % (
    #     x.size, n))
    acf = np.convolve(np.flipud(x[0:n]), x[0:n], mode='full')

    return acf[np.int((acf.size - 1) / 2):np.int(acf.size)] / acf[int((acf.size - 1) / 2)]


def geophone2accel(geotrace, t, resonance, damping):
    adc_resolution = 2**10
    dt = (t[-1] - t[-2]) * 10**-3
    fnyq = 0.5 / dt
    fmin = fnyq / (adc_resolution/2)
    df = fnyq / (adc_resolution/2)
    nsamples = np.arange(fmin,fnyq,df) # all possible frequency of the recorded signal
    transfer = np.zeros(nsamples.size, dtype=complex)

    for k in range(len(nsamples)):
        if k == 0:
            transfer[k] = 1
        else:

            f = k * df
            w = 2 * m.pi * f
            w0 = 2 * m.pi * resonance
            com = complex(0, 1)
            a = -(com * w)
            b = (w0**2 + (2 * com * w0 * w * damping) - w**2)
            transfer[k] = a * b

    tranSW, nsw = fftrl(geotrace, t, 0, adc_resolution)

    transDP = np.divide(tranSW[:-2], transfer)
    outputTrace, tout = ifftrl(transDP, nsw)

    return outputTrace, tout * 10**3

