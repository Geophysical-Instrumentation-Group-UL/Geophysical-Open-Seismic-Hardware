import serial
import matplotlib.pyplot as plt
from tools import *




serial_port = 'COM7'
baud_rate = 115200  # In arduino, Serial.begin(baud_rate)

ser = serial.Serial(serial_port, baud_rate)

ON = True
print("please configure your acquisition")
print("samplingRate [kHz] ? ")
samplingRate = input()
print("duration [ms] ? ")
duration = input()
configAcquisition('1',ser, samplingRate, duration)
configAcquisition('2',ser, samplingRate, duration)
configAcquisition('3',ser, samplingRate, duration)
out_len = 0


while ON:
    command = input()
    if command == 'exit':
        ON = False
        break
    elif command == 'new stack':
        print("Name of the stack ? ")
        stackName = input()
        shot_count = 0

    elif command == 'config':
        print("samplingRate ? ")
        samplingRate = input()
        print("duration ? ")
        duration = input()
        configAcquisition('1',ser, samplingRate, duration)
        configAcquisition('2',ser, samplingRate, duration)
        configAcquisition('3',ser, samplingRate, duration)



    elif command == 'arm':
        ser.write("{}".format(command).encode())
        line = ser.read_until("...".encode())
        print(line.decode("utf-8"))

        line = ser.read_until("ed".encode())
        line = line.decode("utf-8")
        print(line)
        shot_count += 1
        print("shot count : {}".format(shot_count))
  

    elif command.startswith('harvest'):
        workerId = command[-1]
        harvest(workerId, ser, show=True)

    elif command == 'collect':
        out1 = harvest('1', ser)
        out2 = harvest('2', ser)
        out3 = harvest('3', ser)
        list_out = [out1, out2, out3]
        fig, ax = plt.subplots(3, 1)
        for i in range(3):
            ax[i].plot(list_out[i][0], list_out[i][1], label="X")
            ax[i].plot(list_out[i][0], list_out[i][2], label="Y")
            ax[i].plot(list_out[i][0], list_out[i][3], label="Z")

        ax[1].legend()
        ax[2].set_xlabel('time [s]')
        ax[1].set_ylabel("Amplitude [V]")
        fig.suptitle("Shot {}".format(shot_count))
   
        
        save2file(list_out, stackName, shot_count)
        out_len = out1.shape[-1]

    elif command == 'show stack':
        showStack(stackName,numberOfSample=out_len)

    elif command == 'show saved stack':
        print("Name of the stack ? ")
        stackName = input()
        showStack(stackName,numberOfSample=1993)

