#kinda main

import umyo_parser
import display_stuff
import os

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

fifopath = "/tmp/freecad_fifo_cmd"
os.mkfifo(fifopath)
fifo = open(fifopath, 'w')
    
print("conn: " + ser.portstr)
last_data_upd = 0
display_stuff.plot_init()
parse_unproc_cnt = 0
while(1):
    cnt = ser.in_waiting
    if(cnt > 0):
#        print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt/200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        dat_id = display_stuff.plot_prepare(umyo_parser.umyo_get_list())
        d_diff = 0
        if(not (dat_id is None)):
            d_diff = dat_id - last_data_upd
            umyo = umyo_parser.umyo_get_list()[0]
            msg = "1 "
            msg = msg + str(umyo.Qsg[1]) + " " + str(umyo.Qsg[2]) + " " + str(umyo.Qsg[3]) + " " + str(umyo.Qsg[0])
            fifo.write(msg)
#            print(msg, fifo)
        if(d_diff > 2 + cnt_corr):
            #display_stuff.plot_cycle_lines()
            display_stuff.plot_cycle_tester()
            last_data_upd = dat_id

