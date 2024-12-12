#parser

from dataclasses import dataclass
from typing import Dict
from time import time
from queue import Queue
from loguru import logger
from umyo_class import uMyo
from quat_math import *
import math

@dataclass
class DeviceData:
    """Represents a single packet of device data"""
    device_id: int
    timestamp: float
    data: Dict[str, float]  # More specific: dictionary with string keys and float values
    
    @classmethod
    def from_umyo(cls, device):
        """Create DeviceData from a uMyo device"""
        return cls(
            device_id=device.unit_id,
            timestamp=time(),
            data={
                'Qsg': device.Qsg.copy(),
                'yaw': device.yaw,
                'pitch': device.pitch,
                'roll': device.roll,
                'ax': device.ax,
                'ay': device.ay,
                'az': device.az,
                'mag_angle': device.mag_angle,
                'data_array': device.data_array.copy(),
                'device_spectr': device.device_spectr.copy(),
                'rssi': device.rssi,
                'batt': device.batt,
                'data_id': device.data_id
            }
        )

class UMyoParser:
    def __init__(self):
        self.data_queue = Queue()
        self.parse_buf = bytearray(0)
        self.umyo_list = []
        self.unseen_cnt = []

    def id2idx(self, uid):
        cnt = len(self.umyo_list)
        u = 0
        while(u < cnt):
            if(self.unseen_cnt[u] > 1000 and self.umyo_list[u].unit_id != uid):
                del self.umyo_list[u]
                del self.unseen_cnt[u]
                cnt -= 1
            else: u += 1
        for u in range(cnt):
            self.unseen_cnt[u] += 1
            if(self.umyo_list[u].unit_id == uid): 
                self.unseen_cnt[u] = 0
                return u
        
        self.umyo_list.append(uMyo(uid))
        self.unseen_cnt.append(0)
        return cnt

    def umyo_parse(self, pos):
        pp = pos
        rssi = self.parse_buf[pp-1]; #pp is guaranteed to be >0 by design
        packet_id = self.parse_buf[pp]; pp+=1
        packet_len = self.parse_buf[pp]; pp+=1
        unit_id = self.parse_buf[pp]; pp+=1; unit_id <<= 8
        unit_id += self.parse_buf[pp]; pp+=1; unit_id <<= 8
        unit_id += self.parse_buf[pp]; pp+=1; unit_id <<= 8
        unit_id += self.parse_buf[pp]; pp+=1
        idx = self.id2idx(unit_id)
        packet_type = self.parse_buf[pp]; pp+=1
        if(packet_type > 80 and packet_type < 120):
            self.umyo_list[idx].data_count = packet_type - 80;
            self.umyo_list[idx].packet_type = 80;
        else:
            logger.warning(f"Invalid packet type {packet_type} for device {unit_id}")
            return

        self.umyo_list[idx].rssi = rssi
        param_id = self.parse_buf[pp]; pp+=1

        pb1 = self.parse_buf[pp]; pp+=1
        pb2 = self.parse_buf[pp]; pp+=1
        pb3 = self.parse_buf[pp]; pp+=1
        if(param_id == 0):
            self.umyo_list[idx].batt = 2000 + pb1*10;
            self.umyo_list[idx].version = pb2
        data_id = self.parse_buf[pp]; pp+=1

        d_id = data_id - self.umyo_list[idx].prev_data_id
        self.umyo_list[idx].prev_data_id = data_id
        if(d_id < 0): d_id += 256
        self.umyo_list[idx].data_id += d_id
        for x in range(self.umyo_list[idx].data_count):
            hb = self.parse_buf[pp]; pp+=1
            lb = self.parse_buf[pp]; pp+=1
            val = hb*256 + lb
            if(hb > 127):
                val = -65536 + val
            self.umyo_list[idx].data_array[x] = val

        for x in range(4):
            hb = self.parse_buf[pp]; pp+=1
            lb = self.parse_buf[pp]; pp+=1
            val = hb*256 + lb
#        if(hb > 127):
#            val = -65536 + val
            self.umyo_list[idx].device_spectr[x] = val

        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        qww = val
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        qwx = val
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        qwy = val
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        qwz = val

        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        ax = val
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        ay = val
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        az = val
        
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        yaw = val
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        pitch = val
        hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
        if(val > 32767): val = -(65536-val)
        roll = val

        mx = 0;
        my = 0;
        mz = 0;
        if(pos + packet_len > pp + 5): #also has magn data
            hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
            if(val > 32767): val = -(65536-val)
            mx = val
            hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
            if(val > 32767): val = -(65536-val)
            my = val
            hb = self.parse_buf[pp]; pp+=1; lb = self.parse_buf[pp]; pp+=1; val = hb*256 + lb    
            if(val > 32767): val = -(65536-val)
            mz = val


        nyr = sV(0, 1, 0)
        Qsg = sQ(qww, qwx, qwy, qwz)    
        nyr = rotate_v(Qsg, nyr);
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

        self.umyo_list[idx].Qsg[0] = qww
        self.umyo_list[idx].Qsg[1] = qwx
        self.umyo_list[idx].Qsg[2] = qwy
        self.umyo_list[idx].Qsg[3] = qwz
        self.umyo_list[idx].yaw = yaw
        self.umyo_list[idx].pitch = self.umyo_list[idx].pitch * 0.95 + 0.05 * pitch
        if(pitch > 2000 and self.umyo_list[idx].pitch < -2000): self.umyo_list[idx].pitch = pitch 
        if(pitch < -2000 and self.umyo_list[idx].pitch > 2000): self.umyo_list[idx].pitch = pitch 
        self.umyo_list[idx].roll = roll
        self.umyo_list[idx].ax = ax
        self.umyo_list[idx].ay = ay
        self.umyo_list[idx].az = az
        self.umyo_list[idx].mag_angle = mag_angle

        # Create and queue the new device data
        device_data = DeviceData.from_umyo(self.umyo_list[idx])
        self.data_queue.put(device_data)

#    print(data_id)


## Packet Format: 
## full packet length is 65
#
# 1 header: 79 
# 2 header: 213 
# 3 RSSI: 
# 4 packet ID: 
# 5 packet length: 62 is only valid packet length
# 6-9 unit ID
# 10 packet type: 80-120   note: data_count = packet_type - 80 == 8; packet_type is set at 88.
# 11 param ID: 0
# 12-13 pb1 battery
# 14-15 pb2 version 
# 16-17 pb3 unused??
# 18-19 data ID
# 20:(20+datacount) data_array has size data_count
# (20+1+datacount):(20+1+datacount+4) device_spectr has size 4      
# (20+1+datacount+5):(20+1+datacount+13) quaternion{w,x,y,z} has size 8
# (20+1+datacount+14):(20+1+datacount+20) accel{x,y,z} has size 6
# (20+1+datacount+21):(20+1+datacount+27) angles{yaw,pitch,roll} has size 6
# (20+1+datacount+28):(20+1+datacount+34) mag{x,y,z} has size 6
# ...


# USB receiver gets those packets and sends them unchanged via USB with adding 3 bytes 
# before each one: 0x4F, 0xD5 and rssi level measured when receiving this packet.

    def umyo_parse_preprocessor(self, data):
        self.parse_buf.extend(data)
        cnt = len(self.parse_buf)

        if(cnt < 65): ##  LESS THAN FULL PACKET LENGTH
            return 0
        parsed_pos = 0
        packets_processed = 0  # Track number of packets processed
        

        #print(f"""NEW PACKET DETECTED | cnt= {cnt}""")
        #N = 30  # adjust this number to control items per line
        #print("\n".join(
        #    "".join(f"{i}:{b}|" for i, b in enumerate(parse_buf[j:j+N], j+1))
        #    for j in range(0, len(parse_buf), N)
        #))  
        #print('-'*100)

        i=0
        while i <= (cnt-65):
            if(self.parse_buf[i] == 79 and self.parse_buf[i+1] == 213): # Found header (0x4F 0xD5)
                packet_len = self.parse_buf[i+4]
                if (packet_len == 62): # valid packet length
                    self.umyo_parse(i+3)  # Parse this packet
                    parsed_pos = i+3+packet_len
                    i += 1+packet_len
                    packets_processed += 1
                    continue
                else:
                    logger.warning("PARSE ERROR. FOUND HEADER BUT NOT VALID PACKET LENGTH. SKIPPING TO NEXT HEADER")
                     # Note: the while loop will increment i by 1, so we will skip to the next header and the deletion in cumulative
            i+=1
        
        if(parsed_pos > 0): 
            #print(f'DELETING = {parsed_pos} | BUFFER AFTER DELETION:')
            del self.parse_buf[0:parsed_pos]
        
            #print("\n".join(
            # "".join(f"{i}:{b}|" for i, b in enumerate(parse_buf[j:j+N], j+1))
            #for j in range(0, len(parse_buf), N)
            #))  
            #print('-'*100)
            #print('-'*100)

        return packets_processed  # Return number of packets processed instead of buffer length

    def umyo_get_list(self):
        return self.umyo_list


#packet size = 67 = 62 +5 header

    def parse_packet(self, data):
        """Main entry point for parsing new data
        
        Returns:
            int: Number of packets processed
        """
        return self.umyo_parse_preprocessor(data)

    def get_next_packet(self):
        """Get the next available packet from the queue
        
        Returns:
            DeviceData or None: The next packet if available, None if queue is empty
        """
        if not self.data_queue.empty():
            return self.data_queue.get()
        return None
