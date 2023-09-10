#parser

import umyo_class
import quat_math
#from quat_math import sV
from quat_math import *
import math

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
    rssi = parse_buf[pp-1]; #pp is guaranteed to be >0 by design
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

    umyo_list[idx].rssi = rssi
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
    if(val > 32767): val = -(65536-val)
    qww = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    qwx = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    qwy = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    qwz = val

    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    ax = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    ay = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    az = val
    
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    yaw = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    pitch = val
    hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
    if(val > 32767): val = -(65536-val)
    roll = val

    mx = 0;
    my = 0;
    mz = 0;
    if(pos + packet_len > pp + 5): #also has magn data
        hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        mx = val
        hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        my = val
        hb = parse_buf[pp]; pp+=1; lb = parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        mz = val
    nyr = sV(0, 1, 0)
    Qsg = sQ(qww, qwx, qwy, qwz)    
    nyr = quat_math.rotate_v(Qsg, nyr);
    yaw_q = math.atan2(nyr.y, nyr.x);
    
    M = sV(mx, my, mz)
    M = v_renorm(M)
    A = sV(ax, ay, -az)
    A = v_renorm(A)

    m_vert = v_dot(A, M)
    M_hor = sV(M.x - m_vert*A.x, M.y - m_vert*A.y, M.z - m_vert*A.z)
    M_hor = v_renorm(M_hor)
    H = sV(0, 1, 0);
    h_vert = v_dot(A, H)
    H_hor = sV(H.x - h_vert*A.x, H.y - h_vert*A.y, H.z - h_vert*A.z)
    H_hor = v_renorm(H_hor)
    HM = v_mult(H_hor, M_hor)
    asign = -1
    if(v_dot(HM, A) < 0): asign = 1
    mag_angle = asign*math.acos(v_dot(H_hor, M_hor))
#    print("calc mag A", asign*math.acos(v_dot(H_hor, M_hor)))
#    print("mag", mx, my, mz)
#    print("A", ax, ay, az)
    pitch = round(math.atan2(ay, az)*1000)
#    print("angles", yaw, pitch, roll)
#    print("yaw_calc", yaw_q) 

    umyo_list[idx].Qsg[0] = qww
    umyo_list[idx].Qsg[1] = qwx
    umyo_list[idx].Qsg[2] = qwy
    umyo_list[idx].Qsg[3] = qwz
    umyo_list[idx].yaw = yaw
    umyo_list[idx].pitch = umyo_list[idx].pitch * 0.95 + 0.05 * pitch
    if(pitch > 2000 and umyo_list[idx].pitch < -2000): umyo_list[idx].pitch = pitch 
    if(pitch < -2000 and umyo_list[idx].pitch > 2000): umyo_list[idx].pitch = pitch 
    umyo_list[idx].roll = roll
    umyo_list[idx].ax = ax
    umyo_list[idx].ay = ay
    umyo_list[idx].az = az
    umyo_list[idx].mag_angle = mag_angle

#    print(data_id)

def umyo_parse_preprocessor(data):
    parse_buf.extend(data)
    cnt = len(parse_buf)
    if(cnt < 72):
        return 0
    parsed_pos = 0
    for i in range(cnt-70):
        if(parse_buf[i] == 79 and parse_buf[i+1] == 213):
            rssi = parse_buf[i+2]
            packet_id = parse_buf[i+3]
            packet_len = parse_buf[i+4]
            if(packet_len > 20 and i + 3 + packet_len < cnt):
                umyo_parse(i+3)
                parsed_pos = i+2+packet_len
                i += 1+packet_len
#                del parse_buf[0:i+2+packet_len]
#                break
    if(parsed_pos > 0): del parse_buf[0:parsed_pos]
    return cnt

def umyo_get_list():
    return umyo_list
