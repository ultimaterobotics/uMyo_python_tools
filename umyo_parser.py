#parser

import umyo_class

parse_buf = bytearray(0)

umyo_list = []
unseen_cnt = []

def id2idx(uid):
    cnt = len(umyo_list)
    u = 0
    while(u < cnt):
        if(unseen_cnt[u] > 1000 and umyo_list[u].unit_id != uid):
            del umyo_list[u]
            del unseen_cnt[u]
            cnt -= 1
        else: u += 1
    for u in range(cnt):
        unseen_cnt[u] += 1
        if(umyo_list[u].unit_id == uid): 
            unseen_cnt[u] = 0
            return u
        
    umyo_list.append(umyo_class.uMyo(uid))
    unseen_cnt.append(0)
    return cnt

def umyo_parse(pos):
    pp = pos
    packet_id = parse_buf[pp]; pp+=1
    packet_len = parse_buf[pp]; pp+=1
    unit_id = parse_buf[pp]; pp+=1; unit_id <<= 8
    unit_id += parse_buf[pp]; pp+=1; unit_id <<= 8
    unit_id += parse_buf[pp]; pp+=1; unit_id <<= 8
    unit_id += parse_buf[pp]; pp+=1
    idx = id2idx(unit_id)
    packet_type = parse_buf[pp]; pp+=1
    if(packet_type > 80 and packet_type < 120):
        umyo_list[idx].data_count = packet_type - 80;
        umyo_list[idx].packet_type = 80;
    else:
        return

    param_id = parse_buf[pp]; pp+=1
    pb1 = parse_buf[pp]; pp+=1
    pb2 = parse_buf[pp]; pp+=1
    pb3 = parse_buf[pp]; pp+=1
    if(param_id == 0):
        umyo_list[idx].batt = 2000 + pb1*10;
        umyo_list[idx].version = pb2
    data_id = parse_buf[pp]; pp+=1
    d_id = data_id - umyo_list[idx].prev_data_id
    umyo_list[idx].prev_data_id = data_id
    if(d_id < 0): d_id += 256
    umyo_list[idx].data_id += d_id
    for x in range(umyo_list[idx].data_count):
        hb = parse_buf[pp]; pp+=1
        lb = parse_buf[pp]; pp+=1
        val = hb*256 + lb
        if(hb > 127):
            val = -65536 + val
        umyo_list[idx].data_array[x] = val

    for x in range(4):
        hb = parse_buf[pp]; pp+=1
        lb = parse_buf[pp]; pp+=1
        val = hb*256 + lb
#        if(hb > 127):
#            val = -65536 + val
        umyo_list[idx].device_spectr[x] = val

    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    qww = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    qwx = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    qwy = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    qwz = val
    umyo_list[idx].Qsg[0] = qww
    umyo_list[idx].Qsg[1] = qwx
    umyo_list[idx].Qsg[2] = qwy
    umyo_list[idx].Qsg[3] = qwz

#    print(data_id)

def umyo_parse_preprocessor(data):
    parse_buf.extend(data)
    cnt = len(parse_buf)
    if(cnt < 26):
        return
    parsed_pos = 0
    for i in range(cnt-25):
        if(parse_buf[i] == 79 and parse_buf[i+1] == 213):
            rssi = parse_buf[i+2]
            packet_id = parse_buf[i+3]
            packet_len = parse_buf[i+4]
            if(packet_len > 20 and i + packet_len < cnt):
                umyo_parse(i+3)
                parsed_pos = i+2+packet_len
                i += 1+packet_len
#                del parse_buf[0:i+2+packet_len]
#                break
    if(parsed_pos > 0): del parse_buf[0:parsed_pos]
    return cnt

def umyo_get_list():
    return umyo_list
