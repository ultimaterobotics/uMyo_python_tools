import sys
import time

verbose_mode = 0

cnt = len(sys.argv)
if(cnt < 2): 
    print(".bin filename expected")
    sys.exit()
    
f = open(sys.argv[1], "rb")
fw_data = f.read()
fw_len = len(fw_data)
f.close()

if(cnt > 2):
    if(sys.argv[2] == "-v"): verbose_mode = 1

print("binary file read ok, length " + str(fw_len) + " bytes")

# list
from serial.tools import list_ports
port = list(list_ports.comports())
print("current devices:")
for p in port:
    print(p.device)
    device = p.device
print("===")
print("waiting for target device plugged")
tgt_device = ""
while(len(tgt_device) < 2):
    time.sleep(0.5)
    port_new = list(list_ports.comports())
    for p2 in port_new:
        is_known = 0
        for p in port:
            if(p.device == p2.device): is_known = 1
        if(is_known == 0):
            tgt_device = p2.device
            break

#parse data
err_code_ok = 11;
err_code_toolong = 100;
err_code_wrongcheck = 101;
err_code_wronglen = 102;
err_code_packmiss = 103;
err_code_timeout = 104;
parse_buf = bytearray(0)
upload_pack_id = -1
response_pending = 0
need_resend = 0
pack_processed_ok = 1
sent_packet = bytearray(256)
last_err_code = 0

def fw_upload_parser(data):
    global pack_processed_ok, response_pending, need_resend, last_err_code
    parse_buf.extend(data)
    cnt = len(parse_buf)
    if(cnt < 4):
        return
    parsed_pos = 0
    for i in range(cnt-4):
        if(parse_buf[i] == 223 and parse_buf[i+1] == 98):
            pack_id = parse_buf[i+2]
            ret_code = parse_buf[i+3]
            if(verbose_mode): print("resp: pack " + str(pack_id) + " code " + str(ret_code))
            last_err_code = ret_code
            if(pack_id == upload_pack_id and ret_code == err_code_ok):
                response_pending = 2;
                need_resend = 0;
                pack_processed_ok = 1;
            else:
                response_pending = 2;
                need_resend = 1;
                if(ret_code == err_code_wrongcheck):
                    print("chk err")
            parsed_pos = i + 3;
    if(parsed_pos > 0): del parse_buf[0:parsed_pos]
    return cnt

#read
import serial
import time
ser = serial.Serial(port=tgt_device, baudrate=921600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=0)

print("trying to upload at: " + ser.portstr)
last_data_upd = 0
parse_unproc_cnt = 0
upload_pending = 1
upload_started = 0
resend_cnt = 0
upload_sent_bytes = 0
last_response_time = time.time()*1000
fw_pack_mult = 1


def send_data_serial(data, data_len):
    pp = 0;
    sndbuf = bytearray(data_len+7)
    sndbuf[pp] = 223; pp += 1
    sndbuf[pp] = 98; pp += 1
    sndbuf[pp] = data_len+3; pp += 1 #payload length + checksum
    for x in range(data_len):
        sndbuf[pp] = data[x]; pp += 1
		
    check_odd = 0;
    check_tri = 0;
    check_all = 0;
    for x in range(3, pp):
        if((x-3)%2 > 0): check_odd += sndbuf[x];
        if((x-3)%3 > 0): check_tri += sndbuf[x];
        check_all += sndbuf[x];

    sndbuf[pp] = check_odd&0xFF; pp += 1
    sndbuf[pp] = check_tri&0xFF; pp += 1
    sndbuf[pp] = check_all&0xFF; pp += 1
    sndbuf[pp] = 0; pp += 1
    
    ser.write(sndbuf)

prev_reported_complete = 0

while(1):
    cnt = ser.in_waiting
    if(cnt > 0):
        data = ser.read(cnt)
        fw_upload_parser(data)
        
#    print("resend_cnt " + str(resend_cnt) + " response_pending " + str(response_pending) + " need_resend " + str(need_resend))
    if(upload_pending == 0 and response_pending == 0): break
    cur_time = time.time()*1000
    if(resend_cnt > 20 and fw_len - upload_sent_bytes < 32):
        response_pending = 2
    if(resend_cnt > 200):
        upload_pending = 0
        print("upload failed")
        break
    if(response_pending > 0):
        if(response_pending == 2):
            if(upload_sent_bytes >= fw_len and need_resend == 0):
                upload_pending = 0;
                print("...done!");	
            response_pending = 0;
        if(cur_time - last_response_time > 30):
            last_response_time = cur_time;
            last_err_code = err_code_timeout;
            response_pending = 0;
            need_resend = 1;
        continue;

    if(need_resend > 0):
        resend_cnt += 1
        last_response_time = cur_time;
        if(verbose_mode): 
            if(last_err_code != err_code_timeout):
                print("...resend requested, error code " + str(last_err_code));
            else:
                print("...timeout, resending, id: " + str(sent_packet[0]));

        send_data_serial(sent_packet, 33);
        response_pending = 1;
        need_resend = 0;
        continue

    resend_cnt = 0;
    if(upload_started == 0):
        last_response_time = cur_time;
        print("starting upload...");
        upload_start_code = [0x10, 0xFC, 0xA3, 0x05, 0xC0, 0xDE, 0x11, 0x77];

        upload_pack_id = 100;
        ppos = 0;
        for n in range(256): sent_packet[n] = 0;
		
        sent_packet[ppos] = upload_pack_id; ppos += 1
        for n in range(8):
            sent_packet[ppos] = upload_start_code[n]; ppos += 1
        code_length = fw_len;
        sent_packet[ppos] = (code_length>>24)&0xFF; ppos += 1
        sent_packet[ppos] = (code_length>>16)&0xFF; ppos += 1
        sent_packet[ppos] = (code_length>>8)&0xFF; ppos += 1
        sent_packet[ppos] = code_length&0xFF; ppos += 1
#        sent_packet[ppos] = fw_pack_mult; ppos += 1

        if(verbose_mode): print("size bytes: " + str(sent_packet[ppos-4]) + " " + str(sent_packet[ppos-3]) + " " + str(sent_packet[ppos-2]) + " " + str(sent_packet[ppos-1]));

        upload_sent_bytes = 0;

        send_data_serial(sent_packet, 33);
        upload_started = 1;
        response_pending = 1;
        need_resend = 0;
        pack_processed_ok = 0;

    else:
        last_response_time = cur_time;
        if(pack_processed_ok > 0):
            upload_pack_id += 1;
            upload_pack_id = upload_pack_id&0xFF;

        ppos = 0;
        for n in range(256): sent_packet[n] = 0;
		
        if(verbose_mode): print("sending frame " + str(upload_pack_id) + " bytes remains " + str(fw_len - upload_sent_bytes));
        else:
            perc_complete = upload_sent_bytes * 100 / fw_len
            if(perc_complete - prev_reported_complete >= 5):
                prev_reported_complete += 5
                print(str(prev_reported_complete) + "% complete")

        sent_packet[ppos] = upload_pack_id; ppos += 1
        for w in range(8*fw_pack_mult):
            for n in range(4):
                idx = upload_sent_bytes + w*4 + 3-n;
                if(idx < fw_len):
                    sent_packet[ppos] = fw_data[idx]; ppos += 1
                else:
                    sent_packet[ppos] = 0xFF; ppos += 1
		
        if(pack_processed_ok > 0):
            upload_sent_bytes += 32*fw_pack_mult;
		
        send_data_serial(sent_packet, 33);
        response_pending = 1;
        need_resend = 0;
        pack_processed_ok = 0;
        

print("finished")
