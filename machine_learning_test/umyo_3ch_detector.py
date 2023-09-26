#kinda main

import umyo_parser
import display_3ch

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
last_data_upd = 0
parse_unproc_cnt = 0
ch0 = 0
ch1 = 0
ch2 = 0
avg0 = 0
avg1 = 0
avg2 = 0
while(1):
    cnt = ser.in_waiting
    if(cnt > 0):
#        print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt/200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        umyos = umyo_parser.umyo_get_list()
        if(len(umyos) < 3): continue
        ch0 = ch0 * 0.8 + 0.2*(umyos[0].device_spectr[2] + umyos[0].device_spectr[3])
        ch1 = ch1 * 0.8 + 0.2*(umyos[1].device_spectr[2] + umyos[1].device_spectr[3])
        ch2 = ch2 * 0.8 + 0.2*(umyos[2].device_spectr[2] + umyos[2].device_spectr[3])
        scale = 1
        T = 300
        avg0 = avg0*0.999 + 0.001*ch0
        avg1 = avg1*0.999 + 0.001*ch1
        avg2 = avg2*0.999 + 0.001*ch2
        dc0 = ch0 / (ch0 + ch1 + ch2 + T) * scale
        dc1 = ch1 / (ch0 + ch1 + ch2 + T) * scale
        dc2 = ch2 / (ch0 + ch1 + ch2 + T) * scale
        display_3ch.draw_3ch(dc0, dc1, dc2)

