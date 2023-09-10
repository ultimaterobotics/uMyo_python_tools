#kinda main

import umyo_parser

import numpy as np
from matplotlib import pyplot as plt

plot_ys = [0]*1000

def plot_prepare():
    global plot_ys
    devices = umyo_parser.umyo_get_list()
    cnt = len(devices)
    if(cnt < 1): return
    for x in range(devices[0].data_count):
        val = devices[0].data_array[x]
        plot_ys.append(val)
    if(len(plot_ys) < 2): return
    plot_ys = plot_ys[-1000:]
    print(plot_ys[0])
    return devices[0].data_id

# list
from serial.tools import list_ports
port = list(list_ports.comports())
print("available ports:")
for p in port:
    print(p.device)
    device = p.device
print("===")

#read
import serial
ser = serial.Serial(port=device, baudrate=921600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=0)

print("conn: " + ser.portstr)

plt.axis([0,1000,0,10000])
plt.ion()
plt.show()
x = [0]
for i in range(999):
    x.append(1+i)
#x = np.arange(0, len(plot_ys))
line, = plt.plot(x, plot_ys)
plt.ylim(7000,9000)
plt.draw()
plt.pause(0.01)

last_data_upd = 0
while(1):
    cnt = ser.in_waiting
    if(cnt > 0):
        data = ser.read(cnt)
        umyo_parser.umyo_parse_preprocessor(data)
        dat_id = plot_prepare()
        d_diff = dat_id - last_data_upd
        if(d_diff > 100):
            plt.ylim(plot_ys[0]-1000,plot_ys[0]+1000)
            last_data_upd = dat_id
            line.set_ydata(plot_ys)
            plt.draw()
            plt.pause(0.001)

